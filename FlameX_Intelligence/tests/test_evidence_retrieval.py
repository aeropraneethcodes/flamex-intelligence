"""Evidence provenance, semantic retrieval, refusals, and flexible comparisons."""
from pathlib import Path
import pandas as pd
from modules.evidence_retrieval import load_evidence, retrieval, named_investigations, unsupported_numeric_question
from modules.flameiq import answer
from modules.data_loader import read_raw, normalized_view
ROOT=Path(__file__).resolve().parents[1]
raw,_=read_raw(ROOT/'data/flame_intelligence_master.csv')
frame,_=normalized_view(raw)
catalog=pd.read_csv(ROOT/'data/investigations.csv')

def test_evidence_library_provenance():
    e=load_evidence()
    assert len(e)>=20
    assert e.evidence_id.is_unique
    assert set(e.investigation)=={'FLEX','BASS-II','Saffire-I','Saffire-II','Saffire-III'}
    assert e.source_url.str.contains('nasa.gov/').all()
    assert (e[e.investigation!='FLEX'].raw_data_loaded.str.startswith('No')).all()

def test_flexible_retrieval_works_without_keys():
    matches=retrieval('spacecraft solid fuel flow extinction investigation')
    assert not matches.empty
    assert matches.retrieval_score.between(0,1).all()
    assert matches.source_url.str.startswith('https://').all()

def test_multi_investigation_answer_cites_nasa_and_limits():
    result=answer('Compare FLEX, BASS-II and Saffire-I for crew research',frame,catalog)
    assert all(name in result for name in ('FLEX','BASS-II','Saffire-I'))
    assert result.count('https://')>=3
    assert 'INFERRED' in result and 'UNKNOWN' in result and 'not directly interchangeable' in result

def test_open_ended_crew_habitat_query_is_grounded():
    result=answer('Which NASA investigations matter for crew habitat material fire safety?',frame,catalog)
    assert 'BASS-II' in result and 'Saffire-I' in result and 'FLEX' in result
    assert 'NASA PSI-25' in result
    assert 'NASA ranking' in result

def test_investigation_sensor_retrieval():
    result=answer('Which sensors are described for Saffire-I?',frame,catalog)
    assert 'Measurements' in result and 'cameras' in result.lower()
    assert 'NASA-015' in result

def test_unavailable_raw_nonflex_results_refused():
    for question in ['Give exact Saffire-II burning-rate values',
                     'What is the measured BASS-II regression slope?',
                     'Give raw Saffire-I data results']:
        result=answer(question,frame,catalog)
        assert 'UNKNOWN' in result and 'Not loaded' in result
        assert 'experiment-level measurement table' in result

def test_unsupported_operational_safety_refused():
    result=answer('Can this prove a crew habitat is safe?',frame,catalog)
    assert 'UNKNOWN' in result and 'safety' in result.lower()

def test_source_record_calculation_still_active():
    result=answer('Inspect FLEX test 114',frame,catalog)
    assert 'FLEX-114' in result and 'OBSERVED' in result
    result=answer('Compare methanol and heptane slopes',frame,catalog)
    assert 'CALCULATED' in result and '1.504' in result

def test_no_arbitrary_investigations_injected():
    result=answer('How is quantum entanglement verified?',frame,catalog)
    assert 'UNKNOWN' in result

def test_exposed_catalog_no_fake_raw_data():
    e=load_evidence()
    assert not e.claim.str.contains('sample measurements loaded for BASS|actual Saffire burning rate =',case=False).any()
    assert (catalog[catalog.investigation!='FLEX'].data_loaded.str.startswith('No')).all()
