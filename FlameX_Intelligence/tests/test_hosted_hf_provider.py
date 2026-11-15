"""Offline tests of Hugging Face provider selection, credentials, and research gates."""
from pathlib import Path
from unittest.mock import patch
import types
import sys
import pandas as pd
from modules.data_loader import read_raw,normalized_view
from modules.llm_chat import BACKENDS,model_reply,configured_hf_model

ROOT=Path(__file__).resolve().parents[1]
raw,_=read_raw(ROOT/'data/flame_intelligence_master.csv')
df,_=normalized_view(raw)
cat=pd.read_csv(ROOT/'data/investigations.csv')
HF=BACKENDS[2]


def test_hf_backend_added_without_changing_old_provider_order():
    assert BACKENDS[:3]==['Evidence search · no model','OpenAI · API key','Hugging Face · hosted AI']
    assert HF=='Hugging Face · hosted AI'


def test_missing_hf_token_has_clear_error():
    with patch('modules.llm_chat.configured_hf_key',return_value=''):
        answer,error=model_reply('Explain experimental uncertainty',df,cat,HF,scope='General Q&A')
    assert answer is None and 'HF_TOKEN' in error


def test_hf_uses_official_endpoint_and_model_in_general_mode():
    captured={}
    class Client:
        def __init__(self,**kwargs):
            captured.update(kwargs)
            self.chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=self.create))
        def create(self,**kwargs):
            captured['request']=kwargs
            return types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content='Scientific reasoning requires evidence.'))])
    with patch('modules.llm_chat.configured_hf_key',return_value='test-token-not-real'),patch('modules.llm_chat.configured_hf_model',return_value='openai/gpt-oss-20b:fastest'),patch.dict(sys.modules,{'openai':types.SimpleNamespace(OpenAI=Client)}):
        ans,error=model_reply('How does peer review work?',df,cat,HF,scope='General Q&A')
    assert error is None
    assert captured['base_url']=='https://router.huggingface.co/v1'
    assert captured['api_key']=='test-token-not-real'
    assert captured['request']['model']=='openai/gpt-oss-20b:fastest'
    assert ans.startswith('**GENERAL DISCUSSION · NOT NASA-VERIFIED**')


def test_missing_saffire_numbers_refused_without_any_provider_request():
    with patch('modules.llm_chat.configured_hf_key',side_effect=AssertionError('No provider call should happen')):
        response,error=model_reply('What are exact Saffire-II burning rate values?',df,cat,HF)
    assert error is None and 'UNKNOWN' in response


def test_unrelated_question_research_scope_does_not_call_provider():
    with patch('modules.llm_chat.configured_hf_key',side_effect=AssertionError('No provider call should happen')):
        response,error=model_reply('What is the orbital period of Neptune?',df,cat,HF,scope='Research evidence')
    assert error is None and 'UNKNOWN' in response


def test_no_live_key_bundled():
    s=(ROOT/'.env.example').read_text()
    assert 'HF_TOKEN=' in s
    assert not __import__('re').search(r'hf_[A-Za-z0-9]{20,}', s)
    assert 'HF_TOKEN' in (ROOT/'modules/llm_chat.py').read_text()
