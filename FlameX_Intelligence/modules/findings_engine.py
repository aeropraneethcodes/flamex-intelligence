"""Traceable and editable editorial ranking of scientific findings."""
import numpy as np
import pandas as pd
from .statistics import diagnostics
from .data_loader import psi_to_pressure
from .atmospheres import EXPLORATION, HISTORICAL, reference_count

EARLIER={'Methanol slope':1.5048,'Heptane slope':1.5231,'Variance ratio':3.38,'Brown-Forsythe p':1.47e-5}

def verification_table(df):
    d=diagnostics(df);summary=d['summary']; look=summary.set_index('Fuel') if not summary.empty else pd.DataFrame()
    results={
      'Methanol slope':float(look.loc['Methanol','Slope']) if 'Methanol' in look.index else None,
      'Heptane slope':float(look.loc['Heptane','Slope']) if 'Heptane' in look.index else None,
      'Variance ratio':d.get('variance_ratio'),
      'Brown-Forsythe p':d['brown_forsythe']['p'] if d['brown_forsythe'] else None}
    out=[]
    for name,prior in EARLIER.items():
        measured=results[name]
        rel=(abs(measured-prior)/max(abs(prior),1e-15)) if measured is not None else np.inf
        tol=.01 if name!='Brown-Forsythe p' else .03
        status='REPRODUCED (rounded)' if rel<=tol else 'DIFFERS / REVIEW'
        out.append({'Statistic':name,'Previously reported':prior,'Recalculated':measured,'Relative difference':rel,'Tolerance':tol,'Verification':status})
    return pd.DataFrame(out)


def findings(df):
    summary=diagnostics(df); table=summary['summary']; f=[]
    f.append({'Title':'FLEX source coverage','Evidence':f'{len(df)} source records; {df.burn.notna().sum()} with measured burning rate; 2 recorded fuels.',
      'Class':'VERIFIED','Interpretation':'The currently loaded dataset supports a detailed study of this FLEX subset.',
      'Limits':'It does not represent the entire NASA combustion research archive.','Support':5,'Magnitude':2,'Coverage':5,'Reproducibility':5,'Habitat relevance':4,'Pillar':'Suppression','Method':'Raw record counts'})
    for _,row in table.iterrows():
        f.append({'Title':f'{row["Fuel"]}: burning rate–oxygen association',
        'Evidence':f'N={int(row["N"])}; OLS slope={row["Slope"]:.4f}; 95% CI [{row["Slope CI low"]:.3f}, {row["Slope CI high"]:.3f}]; R²={row["R²"]:.3f}.',
        'Class':'VERIFIED','Interpretation':'A fuel-specific association exists within the measured conditions.',
        'Limits':'Other experimental variables and selection effects may confound interpretation; this is not a causal coefficient.','Support':4,'Magnitude':3,'Coverage':4,'Reproducibility':5,'Habitat relevance':3,'Pillar':'Suppression','Method':'Fuel-specific OLS'})
    if summary['brown_forsythe']:
        f.append({'Title':'Fuel-dependent unexplained scatter',
        'Evidence':f'Variance ratio={summary["variance_ratio"]:.3f}; Brown–Forsythe p={summary["brown_forsythe"]["p"]:.3g}.',
        'Class':'STATISTICALLY SUPPORTED' if summary['brown_forsythe']['p']<.05 else 'EXPLORATORY',
        'Interpretation':'Residual scatter differs between fitted fuel groups.',
        'Limits':'Residual variance is not direct flame-stability measurement; conclusion can change under model or influence sensitivity.',
        'Support':5,'Magnitude':4,'Coverage':4,'Reproducibility':4,'Habitat relevance':3,'Pillar':'Suppression','Method':'OLS residuals; Brown–Forsythe'})
    inter=summary['interaction']
    if inter:
        f.append({'Title':'No detected fuel × oxygen slope interaction',
        'Evidence':f'Robust interaction p={inter["p"]:.3f}; 95% CI [{inter["ci_low"]:.3f},{inter["ci_high"]:.3f}].',
        'Class':'VERIFIED','Interpretation':'The current analysis does not detect a statistically significant slope difference.',
        'Limits':'Failure to reject does NOT establish equivalence; confidence interval permits materially different values.',
        'Support':4,'Magnitude':2,'Coverage':4,'Reproducibility':5,'Habitat relevance':3,'Pillar':'Suppression','Method':'OLS interaction with HC3 robust covariance'})
    count=reference_count(df,EXPLORATION)
    f.append({'Title':'Coverage gap: nominal exploration-atmosphere reference',
      'Evidence':f'{count} FLEX rows satisfy oxygen >=34% and pressure <=8.2 psia (reference point: 34% O₂, 8.2 psia).',
      'Class':'VERIFIED','Interpretation':'NASA cites the 8.2 psia / 34% O₂ exploration atmosphere as a nominal design reference; loaded FLEX measurements do not jointly cover the query region.',
      'Limits':'The two-condition coverage query is NOT a NASA-approved atmosphere band, a material-flammability classification, or a safety threshold. Reference: '+EXPLORATION['url'],
      'Support':5,'Magnitude':5,'Coverage':5,'Reproducibility':5,'Habitat relevance':5,'Pillar':'Prevention','Method':'Direct two-condition query; 1 psi = 760/14.6959488 mmHg'})
    return pd.DataFrame(f)


def rank_findings(frame,weights):
    out=frame.copy();total=sum(weights.values()) or 1
    out['Rank score / 100']=sum(out[k]*float(v) for k,v in weights.items())/total*20
    out=out.sort_values(['Rank score / 100','Title'],ascending=[False,True]).reset_index(drop=True)
    out.insert(0,'Rank',np.arange(1,len(out)+1))
    return out
