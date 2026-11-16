from pathlib import Path
import pandas as pd
from modules.data_loader import read_raw, normalized_view
from modules.flameiq import answer
from modules.research_engine import ask_research
ROOT=Path(__file__).resolve().parents[1]
raw,_=read_raw(ROOT/'data/flame_intelligence_master.csv')
df,_=normalized_view(raw)
catalog=pd.read_csv(ROOT/'data/investigations.csv')

def test_judge_question_answers_both_halves():
    result=answer('What do the fuel regressions reveal and what can they not prove?',df,catalog)
    assert 'CALCULATED' in result and 'UNKNOWN · Mechanism' not in result
    assert '1.504' in result and '1.523' in result
    assert 'cannot prove' in result.lower() and 'variance' in result.lower()

def test_paraphrases_regression_limitations():
    for question in ['Compare the regression slopes and explain their limitations', 'Do the regressions prove the fuels behave the same?', 'What can the fitted models tell us about the fuels?']:
        result=answer(question,df,catalog)
        assert 'CALCULATED' in result, question
        assert 'cannot prove' in result.lower(), question

def test_no_key_evidence_mode_uses_correct_route():
    result=ask_research('What do the fuel regressions reveal and what can they not prove?',df,catalog)
    assert result.intent=='regression' and result.numeric_verified and 'residual variance' in result.text

def test_mechanism_question_still_cautious():
    result=answer('Does soot cause the difference?',df,catalog)
    assert 'UNKNOWN' in result
