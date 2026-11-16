"""Final release: scientific integrity and no-hallucination gates."""
from pathlib import Path
import pandas as pd
from modules.data_loader import read_raw,normalized_view
from modules.research_engine import ask_research
from modules.atmospheres import EXPLORATION,HISTORICAL,reference_count
from modules.statistics import diagnostics

BASE=Path(__file__).resolve().parents[1]
raw,_=read_raw(BASE/'data/flame_intelligence_master.csv')
d,_=normalized_view(raw)
cat=pd.read_csv(BASE/'data/investigations.csv')

def test_source_table_not_modified_and_expected_shape():
    assert raw.shape==(274,15)
    assert d.shape[0]==274

def test_two_reference_points_are_not_safety_bands():
    assert (EXPLORATION['psi'],EXPLORATION['oxygen'])==(8.2,.34)
    assert (HISTORICAL['psi'],HISTORICAL['oxygen'])==(10.2,.30)
    assert reference_count(d,EXPLORATION)==reference_count(d,HISTORICAL)==0

def test_residual_variance_calculation_and_interaction():
    z=diagnostics(d)
    assert abs(z['variance_ratio']-3.365717001889)<1e-5
    assert z['brown_forsythe']['p']<1e-4
    assert z['interaction']['p']>.05

def test_unrelated_question_is_rejected_by_offline_engine():
    result=ask_research('What was the exact ambient temperature on Neptune on January 3, 2026?',d,cat)
    assert 'UNKNOWN' in result.text or 'not' in result.text.lower()

def test_no_provider_or_credentials_in_app():
    source=(BASE/'app.py').read_text()
    assert 'model_reply(' not in source
    assert 'HF_TOKEN' not in source
    assert 'OPENAI_API_KEY' not in source
    assert 'Conversation engine' not in source
