from pathlib import Path
import numpy as np
import pandas as pd
from modules.data_loader import read_raw,normalized_view,filtered,psi_to_pressure,suggest_mapping
from modules.statistics import diagnostics,fit_fuels,sensitivity
from modules.findings_engine import verification_table,findings,rank_findings
from modules.anomaly_detection import audit_flags
from modules.models import regression_analysis,classification_analysis,scenario_neighbors,scenario_prediction
from modules.flameiq import answer

ROOT=Path(__file__).resolve().parents[1]
raw,digest=read_raw(ROOT/'data/flame_intelligence_master.csv')
df,audit=normalized_view(raw)
cat=pd.read_csv(ROOT/'data/investigations.csv')

def test_raw_is_preserved():
    assert raw.shape==(274,15)
    assert len(df)==len(raw)
    assert df.burn.notna().sum()==258
    assert set(df.fuel)=={'Methanol','Heptane'}
    assert len(digest)==64
    assert set(suggest_mapping(raw.columns).values()).issubset(set(raw.columns))
    assert 'NO_ROW_DROPS' in audit.step.tolist()

def test_main_stats_reproduce():
    d=diagnostics(df)
    s=d['summary'].set_index('Fuel')
    assert s.loc['Methanol','N']==151
    assert s.loc['Heptane','N']==107
    assert abs(s.loc['Methanol','Slope']-1.5048)<.0001
    assert abs(s.loc['Heptane','Slope']-1.5231)<.0001
    assert abs(d['brown_forsythe']['p']-1.4652e-5)<1e-8
    assert abs(d['variance_ratio']-3.365717)<.001
    assert d['interaction']['p']>.95

def test_zero_pressure_and_outlier_not_deleted():
    d=diagnostics(df);flags=audit_flags(df,d['residuals'])
    bad=df[df.pressure==0]
    assert len(bad)>=1
    assert not flags[flags.Reason=='Nonpositive pressure'].empty
    assert len(df)==274
    sens=sensitivity(df)
    assert sens.iloc[0]['Rows']==274
    assert sens.iloc[1]['Rows']<274

def test_filters_do_not_change_source():
    view=filtered(df,fuels=['Methanol'],oxygen=(.18,.21))
    assert len(df)==274
    assert set(view.fuel)=={'Methanol'}
    assert view.oxygen.between(.18,.21).all()

def test_moon_band_no_joint_support():
    matched=df[(df.oxygen>=.30)&(df.pressure<=psi_to_pressure(10.2))]
    assert len(matched)==0
    assert abs(psi_to_pressure(10.2)-527.5)<2

def test_catalog_sources_and_separation():
    assert len(cat)>=20
    assert cat.source_url.str.startswith('https://').all()
    assert (cat.data_loaded.str.startswith('No')).sum()==len(cat)-1
    assert cat.investigation.is_unique
    assert 'FLEX' in cat.investigation.tolist()

def test_ranked_findings():
    rank=rank_findings(findings(df),{'Support':3,'Magnitude':3,'Coverage':3,'Reproducibility':3,'Habitat relevance':5})
    assert len(rank)>=5
    assert rank.iloc[0].Rank==1
    assert rank['Rank score / 100'].between(0,100).all()
    verification=verification_table(df)
    assert len(verification)==4
    assert (verification.Verification.str.startswith('REPRODUCED')).sum()>=3

def test_model_a_grouped_cv():
    reg=regression_analysis(df,trees=35)
    assert 'error' not in reg
    assert reg.pressure_bins==4 if hasattr(reg,'pressure_bins') else reg['pressure_bins']==4
    assert set(reg['summary'].Model)=={'Mean baseline','Linear (ridge)','Random Forest'}
    assert len(reg['oof'])==len(reg['frame'])
    assert reg['oof']['Random Forest'].notna().all()
    assert reg['interval_halfwidth']>=0

def test_model_b_stratified_cv():
    clf=classification_analysis(df,trees=35)
    assert 'error' not in clf
    assert clf['folds']==5
    assert clf['confusion'].values.sum()==clf['rows']
    assert np.isfinite(clf['logloss'])
    assert len(clf['metrics'])==3

def test_scenario_outside_moon_band():
    s={'fuel':'Methanol','oxygen':.30,'pressure':psi_to_pressure(10.2),'diameter':3.0}
    nn=scenario_neighbors(df,s)
    assert not nn['neighbors'].empty
    reg=regression_analysis(df,trees=35)
    pred=scenario_prediction(reg,s,nn,moon_band=True)
    assert pred['prediction'] is None

def test_assistant_refuses_unsupported():
    q=answer('What are exact Saffire-II test results?',df,cat)
    assert 'UNKNOWN' in q and 'not' in q.lower()
    q=answer('Is 30% O2 at 10.2 psi safe for crew?',df,cat)
    assert 'UNKNOWN' in q
    q=answer('Inspect FLEX test 114',df,cat)
    assert 'FLEX-114' in q


def test_assistant_answers_metadata_vs_numeric():
    metadata=answer('What does Saffire-I measure?',df,cat)
    assert 'CATALOG METADATA' in metadata and 'Measurements' in metadata
    numeric=answer('Give exact Saffire-II burning-rate values',df,cat)
    assert 'UNKNOWN' in numeric and 'Not loaded' in numeric

def test_assistant_total_vs_complete_case_count():
    counts=answer('How many Heptane experiments?',df,cat)
    assert '117' in counts and 'OBSERVED' in counts
    complete=answer('How many Heptane experiments with valid burning rate?',df,cat)
    assert '107' in complete and 'CALCULATED' in complete
    mean=answer('What is the mean burning rate for Heptane?',df,cat)
    assert 'CALCULATED' in mean and 'Mean' in mean
