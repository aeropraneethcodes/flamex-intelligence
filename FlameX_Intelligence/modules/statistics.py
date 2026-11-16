"""Reproducible descriptive and inferential statistics; no hidden exclusions."""
from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan, het_white


def fit_fuels(df):
    """OLS burn ~ oxygen within each fuel, plus residual frame and 95% mean CI."""
    summary=[]; frames=[]; curves={}
    for fuel,g in df.dropna(subset=['fuel','oxygen','burn']).groupby('fuel'):
        if len(g)<4 or g['oxygen'].nunique()<2:
            continue
        x=g['oxygen'].to_numpy(float); y=g['burn'].to_numpy(float)
        X=sm.add_constant(x,has_constant='add'); model=sm.OLS(y,X).fit()
        resid=y-model.predict(X)
        ci=model.conf_int(alpha=.05)
        summary.append({'Fuel':str(fuel),'N':len(g),'Slope':float(model.params[1]),
            'Slope CI low':float(ci[1,0]),'Slope CI high':float(ci[1,1]),
            'Intercept':float(model.params[0]),'R²':float(model.rsquared),
            'Residual variance':float(np.var(resid,ddof=1)),'Slope p':float(model.pvalues[1])})
        frame=g[['record_id','id','fuel','oxygen','pressure','burn']].copy()
        frame['fitted']=model.predict(X);frame['residual']=resid
        frame['cooks_d']=model.get_influence().cooks_distance[0]
        frame['flag_cooks']=frame['cooks_d'] > 4/len(g)
        frames.append(frame)
        grid=np.linspace(x.min(),x.max(),70)
        pred=model.get_prediction(sm.add_constant(grid,has_constant='add')).summary_frame(alpha=.05)
        curves[str(fuel)]=pd.DataFrame({'oxygen':grid,'fit':pred['mean'].values,'lo':pred['mean_ci_lower'].values,'hi':pred['mean_ci_upper'].values})
    return pd.DataFrame(summary), (pd.concat(frames) if frames else pd.DataFrame()), curves


def interaction(df):
    frame=df.dropna(subset=['fuel','oxygen','burn']).copy()
    if frame['fuel'].nunique()!=2 or len(frame)<20:return None
    formula='burn ~ oxygen * C(fuel)'
    model=smf.ols(formula,data=frame).fit(cov_type='HC3')
    terms=[i for i in model.params.index if 'oxygen:C(fuel)' in i]
    if not terms:return None
    term=terms[0]; c=model.conf_int().loc[term]
    return {'term':term,'coefficient':float(model.params[term]),'p':float(model.pvalues[term]),
            'ci_low':float(c.iloc[0]),'ci_high':float(c.iloc[1]),'n':len(frame), 'method':'OLS with HC3 heteroscedasticity-robust covariance'}


def diagnostics(df):
    summary,residuals,_=fit_fuels(df)
    result={'summary':summary,'residuals':residuals,'interaction':interaction(df),'brown_forsythe':None,'levene':None,'breusch_pagan':None,'white':None}
    if not residuals.empty and residuals['fuel'].nunique()==2:
        groups=[g['residual'].values for _,g in residuals.groupby('fuel')]
        bf=stats.levene(*groups,center='median'); lv=stats.levene(*groups,center='mean')
        result['brown_forsythe']={'stat':float(bf.statistic),'p':float(bf.pvalue)}
        result['levene']={'stat':float(lv.statistic),'p':float(lv.pvalue)}
        sorted_vars=summary.sort_values('Fuel')['Residual variance'].to_numpy(float)
        result['variance_ratio']=float(sorted_vars.max()/sorted_vars.min()) if sorted_vars.min()>0 else None
    frame=df.dropna(subset=['fuel','oxygen','burn'])
    if len(frame)>10 and frame['fuel'].nunique()==2:
        mod=smf.ols('burn ~ oxygen * C(fuel)',data=frame).fit()
        exog=mod.model.exog
        try:
            z=het_breuschpagan(mod.resid,exog);result['breusch_pagan']={'stat':float(z[0]),'p':float(z[1])}
            z=het_white(mod.resid,exog);result['white']={'stat':float(z[0]),'p':float(z[1])}
        except Exception:
            pass
    return result


def sensitivity(df):
    """Comparison across *views*, never changes source data or deems flags errors."""
    full=diagnostics(df)
    flagged=set(full['residuals'].loc[full['residuals'].get('flag_cooks',False)==True,'id']) if not full['residuals'].empty else set()
    filtered=df.loc[~df['id'].isin(flagged)]
    restricted=diagnostics(filtered) if flagged else full
    return pd.DataFrame([
        {'Analysis view':'All source records','Rows':len(df),'Flagged excluded':0,'Variance ratio':full.get('variance_ratio'),'Brown-Forsythe p':full['brown_forsythe']['p'] if full['brown_forsythe'] else np.nan},
        {'Analysis view':'Sensitivity only: omit Cook-flagged','Rows':len(filtered),'Flagged excluded':len(df)-len(filtered),'Variance ratio':restricted.get('variance_ratio'),'Brown-Forsythe p':restricted['brown_forsythe']['p'] if restricted['brown_forsythe'] else np.nan}
    ])
