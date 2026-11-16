"""Judge-facing acceptance gates for no-API research answer engine."""
from pathlib import Path
import ast
import pandas as pd
import pytest
from modules.data_loader import read_raw,normalized_view
from modules.research_engine import ask_research,classify_question,numeric_claim_check
ROOT=Path(__file__).resolve().parents[1]
raw,_=read_raw(ROOT/'data/flame_intelligence_master.csv')
df,_=normalized_view(raw)
cat=pd.read_csv(ROOT/'data/investigations.csv')

@pytest.mark.parametrize('question',[
 'What do the fuel regressions reveal and what can they not prove?',
 'Compare the fitted oxygen slopes and explain their limitations',
 'Does the regression prove the two fuels are identical?',
 'How do methanol and heptane behave in the fitted models?',
 'What is the difference in oxygen sensitivity between the fuels?',
])
def test_regression_paraphrases(question):
    result=ask_research(question,df,cat)
    assert result.intent=='regression',question
    assert result.numeric_verified,result
    assert '1.523' in result.text and '1.505' in result.text
    assert 'cannot prove' in result.text.lower() and 'residual variance' in result.text

@pytest.mark.parametrize('question',[ 'Why is the residual scatter different?', 'Explain Brown-Forsythe and the variability', 'Is heptane more stable than methanol?', 'How different are the fuel variances?' ])
def test_variability_limitations(question):
    result=ask_research(question,df,cat)
    assert result.intent=='variability'
    assert '3.37' in result.text
    assert 'not' in result.text.lower() and result.numeric_verified

@pytest.mark.parametrize('question', ['Give exact Saffire-II burning rates', 'How many BASS-II observations were measured?', 'What is the measured Saffire-I variance?'])
def test_missing_raw_cross_experiment_data(question):
    result=ask_research(question,df,cat)
    assert result.intent=='unavailable_measurements'
    assert 'not loaded' in result.text and result.sources

@pytest.mark.parametrize('question', ['Is this safe for astronauts?', 'Can you certify the atmosphere is safe?', 'Does the model guarantee spacecraft fire safety?'])
def test_never_certify_fire_safety(question):
    result=ask_research(question,df,cat)
    assert result.intent=='safety_boundary'
    assert 'not' in result.text.lower()

@pytest.mark.parametrize('question', ['How many FLEX records are in the table?', 'How many complete records are there for heptane?', 'What is the mean burning rate for methanol?', 'How many test end outcomes are there?'])
def test_source_driven_statistics(question):
    result=ask_research(question,df,cat)
    assert result.intent in {'counts','mean','outcomes'}
    assert result.numeric_verified
    assert result.data_rows>0

def test_no_novel_numbers_in_numeric_claim_guard():
    assert numeric_claim_check('The value is 1.505 with 95% confidence.', ['1.505'])[0]
    ok,unrecognized=numeric_claim_check('The value is 1.505 and 93.8.', ['1.505'])
    assert not ok and '93.8' in unrecognized

def test_subsetting_updates_computed_answers():
    partial=df[df.fuel.eq('Methanol')]
    result=ask_research('How many FLEX records are there?',partial,cat)
    assert result.numeric_verified
    assert '**151**' not in result.text # source rows vs complete-case rows
    assert f'**{len(partial)}**' in result.text

def test_no_api_import_path_in_app_or_requirements():
    app=(ROOT/'app.py').read_text()
    assert 'from modules.llm_chat' not in app
    assert 'model_reply(' not in app
    assert 'HF_TOKEN' not in app and 'OPENAI_API_KEY' not in app
    assert 'openai' not in (ROOT/'requirements.txt').read_text().lower()
    assert (ROOT/'modules/research_engine.py').exists()
    assert len(ast.parse(app).body)>20

def test_scientific_context_not_made_up():
    result=ask_research('What is the orbital period of Neptune?',df,cat)
    assert 'UNKNOWN' in result.text


def test_multiple_study_metadata_is_not_raw_measurements():
    result=ask_research('Compare FLEX, BASS-II and Saffire-I for habitats',df,cat)
    assert result.intent=='investigation_evidence'
    assert 'not loaded' in result.text.lower()
    assert result.sources


def test_predictions_are_validated_not_mission_predictions():
    result=ask_research('How accurate is the machine learning prediction?',df,cat)
    assert result.intent=='model_validation'
    assert result.numeric_verified
    assert 'MAE' in result.text and 'RMSE' in result.text
    assert 'not independent mission data' in result.text
