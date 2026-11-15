"""No-network checks for free-form FlameIQ and verified atmosphere reference corrections."""
from pathlib import Path
from unittest.mock import patch
import importlib, types
from modules.data_loader import read_raw, normalized_view
from modules.atmospheres import EXPLORATION,HISTORICAL,reference_count,references_markdown
from modules.llm_chat import BACKENDS,evidence_pack,model_reply,prompt_messages,refusal_if_unavailable
from modules.flameiq import answer
from modules.evidence_retrieval import retrieval
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
raw,_=read_raw(ROOT/'data/flame_intelligence_master.csv')
frame,_=normalized_view(raw)
catalog=pd.read_csv(ROOT/'data/investigations.csv')


def test_nominal_and_historical_references_are_distinct_and_sourced():
    assert EXPLORATION['oxygen']==.34 and EXPLORATION['psi']==8.2
    assert HISTORICAL['oxygen']==.30 and HISTORICAL['psi']==10.2
    assert all(x['url'].startswith('https://ntrs.nasa.gov/') for x in (EXPLORATION,HISTORICAL))
    assert reference_count(frame,EXPLORATION)==0
    assert reference_count(frame,HISTORICAL)==0
    formatted=references_markdown(frame)
    assert '8.2' in formatted and '10.2' in formatted and '34%' in formatted and '30%' in formatted


def test_free_form_non_preset_research_question_has_source_links():
    question='What makes the small solid-fuel spaceflight research different from larger spacecraft experiments?'
    result=answer(question,frame,catalog)
    assert 'https://' in result and ('OBSERVED' in result or 'INFERRED' in result)


def test_arbitrary_query_not_about_nasa_is_not_fabricated():
    result=answer('What is the orbital period of Neptune?',frame,catalog)
    assert 'UNKNOWN' in result


def test_atmosphere_answer_corrects_label():
    result=answer('What is the Artemis atmosphere coverage?',frame,catalog)
    assert '34%' in result and '8.2' in result and '30%' in result and '10.2' in result
    assert 'historical' in result.lower()


def test_unloaded_saffire_data_refusal_is_pre_model():
    assert 'UNKNOWN' in refusal_if_unavailable('Give exact Saffire-II burning-rate values')
    with patch('modules.llm_chat.configured_key',side_effect=AssertionError('should never request API key')):
        result,error=model_reply('Give exact Saffire-II burning-rate values',frame,catalog,BACKENDS[1])
    assert error is None and 'UNKNOWN' in result


def test_local_mode_works_without_model_setup():
    result,error=model_reply('Compare methanol and heptane slopes',frame,catalog,BACKENDS[0])
    assert error is None and 'CALCULATED' in result and '1.504' in result


def test_model_missing_key_reported_and_no_hardcoded_key():
    with patch('modules.llm_chat.configured_key',return_value=''):
        result,error=model_reply('Explain NASA experimental uncertainty',frame,catalog,BACKENDS[1])
    assert result is None and 'OPENAI_API_KEY' in error


def test_general_chat_is_explicitly_unverified_and_keeps_history():
    # Stub OpenAI response, no external network access.
    class Msg:content='Orbit concepts are studied in physics.'
    class Choice:message=Msg()
    class Result:choices=[Choice()]
    class Chat: 
        class Completions:
            def create(self,**kwargs):
                assert 'follow-up' in kwargs['messages'][-1]['content']
                assert any(m.get('role')=='user' and m.get('content')=='previous question' for m in kwargs['messages'])
                return Result()
        completions=Completions()
    class FakeOpenAI:
        def __init__(self,**kwargs):pass
        chat=Chat()
    with patch('modules.llm_chat.configured_key',return_value='dummy'),patch.dict('sys.modules', {'openai': types.SimpleNamespace(OpenAI=FakeOpenAI)}):
        result,error=model_reply('a follow-up',frame,catalog,BACKENDS[1],scope='General Q&A',history=[('user','previous question')])
    assert error is None and result.startswith('**GENERAL DISCUSSION · NOT NASA-VERIFIED**')


def test_new_module_avoids_auto_hosted_requests():
    import inspect
    source=inspect.getsource(importlib.import_module('modules.llm_chat'))
    assert 'http://127.0.0.1:11434/api/chat' not in source
    assert 'openai.com/v1/' not in source
    assert 'OPENAI_API_KEY' in source
