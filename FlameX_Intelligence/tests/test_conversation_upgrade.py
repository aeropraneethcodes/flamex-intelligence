"""No-network checks for free-form FlameIQ and verified atmosphere reference corrections."""
from pathlib import Path
from modules.data_loader import read_raw, normalized_view
from modules.atmospheres import EXPLORATION,HISTORICAL,reference_count,references_markdown
from modules.research_engine import ask_research
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


def test_unloaded_saffire_data_refusal_without_api():
    result=ask_research('Give exact Saffire-II burning-rate values',frame,catalog)
    assert result.intent=='unavailable_measurements'
    assert 'not loaded' in result.text

def test_research_engine_is_offline():
    import inspect
    source=inspect.getsource(ask_research)
    assert 'model_reply' not in source
    assert 'http' not in source
