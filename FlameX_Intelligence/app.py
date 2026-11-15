"""FlameX Intelligence — evidence-grounded NASA combustion research desk.

Not NASA-endorsed. Loaded raw data: one FLEX table. No operational safety verdicts.
"""
from pathlib import Path
import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from modules.data_loader import (FIELD_MAP,read_raw,suggest_mapping,normalized_view,filtered,
    completeness,composition_diagnostics,psi_to_pressure,pressure_to_psi)
from modules.statistics import fit_fuels,diagnostics,sensitivity
from modules.anomaly_detection import audit_flags
from modules.findings_engine import findings,rank_findings,verification_table
from modules.models import regression_analysis,classification_analysis,scenario_neighbors,scenario_prediction
from modules.flameiq import answer
from modules.llm_chat import BACKENDS, model_reply, configured_key
from modules.atmospheres import EXPLORATION, HISTORICAL, reference_count
from modules.evidence_retrieval import load_evidence, retrieval, evidence_comparison
from modules.report_generator import build_markdown,markdown_to_html

BASE=Path(__file__).resolve().parent
MASTER=BASE/'data'/'flame_intelligence_master.csv'
CATALOG=BASE/'data'/'investigations.csv'
EVIDENCE_LIBRARY=BASE/'data'/'evidence_library.csv'
CHALLENGE='https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/'
COLORS=['#2A6E9E','#BC645A','#70A8B1','#9F813D']
C={'bg':'#F6F8FA','navy':'#18344F','blue':'#2878A5','muted':'#637588','rule':'#DCE4EA'}
st.set_page_config(page_title='FlameX Intelligence | Dynamic Duo',page_icon='🔬',layout='wide',initial_sidebar_state='expanded')
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',system-ui,sans-serif}
.stApp{background:#f6f8fa;color:#1e3042} .block-container{padding-top:1.25rem;max-width:1460px;padding-bottom:3rem}
section[data-testid="stSidebar"]{background:white;border-right:1px solid #dce4ea}
h1,h2,h3{font-family:Manrope,system-ui,sans-serif!important;color:#18344f!important;letter-spacing:-.03em}
.stMarkdown p{line-height:1.55}
.headerbox{background:white;padding:25px 30px 20px;border:1px solid #dce4ea;border-top:4px solid #2878a5;border-radius:10px;margin-bottom:20px}
.brand{font-family:Manrope,sans-serif;font-weight:800;font-size:31px;letter-spacing:-1px;color:#18344f}
.deck{font-size:14px;color:#637588;max-width:800px;margin-top:3px}
.eyebrow{font-size:10px;font-weight:800;letter-spacing:1.9px;color:#2878a5;margin-bottom:6px}
.micro{font-size:11px;letter-spacing:.5px;color:#718293}
.panelbox{background:white;border:1px solid #dce4ea;border-radius:10px;padding:17px 18px;margin:6px 0}
.notice{border-left:3px solid #2878a5;background:#eaf2f7;color:#284662;border-radius:5px;padding:11px 15px;margin:10px 0;font-size:13px}
.caution{border-left:3px solid #b28b41;background:#faf3e7;color:#695022;border-radius:5px;padding:11px 15px;margin:10px 0;font-size:13px}
.metric{background:white;border:1px solid #dce4ea;border-radius:10px;padding:14px 16px;min-height:102px}
.metric .k{font-size:10px;font-weight:700;letter-spacing:1.15px;color:#627588;text-transform:uppercase}
.metric .v{font-family:Manrope,sans-serif;font-size:26px;font-weight:800;color:#18344f;margin:5px 0 1px}
.metric .n{font-size:11px;color:#768699}
hr{border-color:#dce4ea}.stButton button{border-radius:7px;font-weight:600}
[data-testid="stMetric"]{background:white;border:1px solid #dce4ea;border-radius:9px;padding:12px 16px}
[data-testid="stDataFrame"]{border:1px solid #dce4ea;border-radius:8px}
</style>''',unsafe_allow_html=True)

def alert(msg,kind='notice'):
    st.markdown(f'<div class="{kind}">{msg}</div>',unsafe_allow_html=True)
def metric(label,value,note=''):
    st.markdown(f'<div class="metric"><div class="k">{label}</div><div class="v">{value}</div><div class="n">{note}</div></div>',unsafe_allow_html=True)
def chart(fig,height=360):
    fig.update_layout(height=height,margin=dict(l=12,r=14,t=25,b=20),font_family='DM Sans',font_color='#29425b',
        plot_bgcolor='white',paper_bgcolor='white',legend_title_text='',
        xaxis=dict(gridcolor='#E9EDF1',zeroline=False),yaxis=dict(gridcolor='#E9EDF1',zeroline=False))
    st.plotly_chart(fig,use_container_width=True,config={'displaylogo':False,'toImageButtonOptions':{'format':'png','scale':2}})
def precision_frame(df,columns):
    return df[[x for x in columns if x in df]]

def title(text,subtitle=None):
    st.subheader(text)
    if subtitle:st.caption(subtitle)

@st.cache_data(show_spinner=False)
def source_data(blob):
    raw,digest=read_raw(blob)
    return raw,digest
@st.cache_data(show_spinner=False)
def catalog_data():
    return pd.read_csv(CATALOG)
@st.cache_data(show_spinner=False)
def evidence_data():
    return pd.read_csv(EVIDENCE_LIBRARY)
@st.cache_data(show_spinner=False)
def diagnostic_data(df):return diagnostics(df)
@st.cache_data(show_spinner=False)
def model_a(df):return regression_analysis(df)
@st.cache_data(show_spinner=False)
def model_b(df):return classification_analysis(df)

st.sidebar.markdown('<div class="eyebrow">DYNAMIC DUO · 2026 SPACE APPS</div><div class="brand" style="font-size:24px">FlameX <span style="color:#2878a5">Intelligence</span></div>',unsafe_allow_html=True)
st.sidebar.caption('An evidence-grounded fire-safety research desk')
upload=st.sidebar.file_uploader('Replace FLEX experimental table (CSV)',type='csv',help='Optional: the authentic 274-row master CSV is already bundled.')
raw_blob=upload.getvalue() if upload else MASTER.read_bytes()
try:raw,source_hash=source_data(raw_blob)
except Exception as e:st.error(f'Unable to load experimental data: {e}');st.stop()

st.sidebar.markdown('**Column mapping**')
with st.sidebar.expander('Verify original column names',expanded=False):
    st.caption('Default mappings match the bundled file; no data column is invented.')
    sugg=suggest_mapping(raw.columns);mapping={}
    for key,expected in FIELD_MAP.items():
        names=['— NOT LOADED —']+list(raw.columns)
        default=sugg[key] if sugg.get(key) in raw.columns else '— NOT LOADED —'
        value=st.selectbox(key.replace('_',' ').title(),names,index=names.index(default),key='map_'+key)
        mapping[key]=None if value==names[0] else value
if 'mapping' not in locals():mapping=suggest_mapping(raw.columns)
try:full,audit=normalized_view(raw,mapping)
except ValueError as e:st.error(str(e));st.stop()
cat=catalog_data()
evidence_lib=evidence_data()

PAGES=['Mission overview','Investigation explorer','Combustion explorer','Fuel comparison lab','Stability & uncertainty',
       'Predictive intelligence','Artemis scenario explorer','FlameIQ research assistant','Research brief & sources']
st.sidebar.divider()
page=st.sidebar.radio('RESEARCH DESK',PAGES,label_visibility='collapsed')
st.sidebar.divider()
with st.sidebar.expander('Experiment filters',expanded=True):
    all_fuel=sorted(full.fuel.dropna().unique().tolist())
    fuels=st.multiselect('Fuel',all_fuel,default=all_fuel)
    all_outcome=sorted(full.outcome.dropna().unique().tolist())
    outcomes=st.multiselect('Test end',all_outcome,default=all_outcome)
    ox=(float(full.oxygen.min()),float(full.oxygen.max()))
    orng=st.slider('O₂ mole fraction',ox[0],ox[1],ox,step=.01)
    pmin,pmax=float(full.pressure.min()),float(full.pressure.max())
    prng=st.slider('Pressure (mmHg)',pmin,pmax,(pmin,pmax),step=1.0)
view=filtered(full,fuels,outcomes,orng,prng)
st.sidebar.caption(f'VISIBLE: {len(view)} / {len(full)} records · filters never modify the original file')
st.sidebar.divider()
st.sidebar.caption('Independent team project · No NASA affiliation or endorsement · Research interpretation only')

st.markdown(f'''<div class="headerbox"><div class="eyebrow">SPACE APPS 2026 · MICROGRAVITY COMBUSTION RESEARCH</div>
<div class="brand">FlameX Intelligence</div><div class="deck">Find the right investigation. See what its evidence actually supports. Know what it cannot tell you.</div>
<div class="micro" style="margin-top:13px">NASA PSI SOURCES &nbsp; / &nbsp; FLEX SOURCE DATA &nbsp; / &nbsp; TRANSPARENT UNCERTAINTY &nbsp; / &nbsp; EVIDENCE-ONLY FLAMEIQ</div></div>''',unsafe_allow_html=True)

if page=='Mission overview':
    title('Mission overview','A transparent snapshot of one loaded FLEX table and the wider NASA investigation catalog.')
    a,b,c,d=st.columns(4)
    with a:metric('Loaded FLEX runs',len(full),'complete original source table')
    with b:metric('Current selection',len(view),'all filters applied')
    with c:metric('Rate observations',int(view.burn.notna().sum()),'not imputed')
    with d:metric('Catalog investigations',len(cat),'metadata only beyond FLEX')
    l,r=st.columns(2)
    with l:
        title('Fuel distribution')
        counts=view.fuel.value_counts().rename_axis('Fuel').reset_index(name='Runs')
        if len(counts):chart(px.bar(counts,x='Fuel',y='Runs',color='Fuel',text='Runs',color_discrete_sequence=COLORS),300)
    with r:
        title('Test-end outcomes')
        counts=view.outcome.value_counts().rename_axis('Outcome').reset_index(name='Runs')
        if len(counts):chart(px.pie(counts,names='Outcome',values='Runs',hole=.57,color_discrete_sequence=COLORS),300)
    l,r=st.columns(2)
    with l:
        st.markdown('#### Experimental ranges')
        st.write(f'**O₂ mole fraction:** {view.oxygen.min():.3f}–{view.oxygen.max():.3f}' if len(view) else 'No records selected')
        st.write(f'**Pressure:** {view.pressure.min():.1f}–{view.pressure.max():.1f} mmHg ({pressure_to_psi(view.pressure.min()):.2f}–{pressure_to_psi(view.pressure.max()):.2f} psi)' if len(view) else '')
        alert('The master file includes oxygen, N, CO-labeled, and He composition fields. The CO label must be checked against original NASA metadata before assigning its chemical identity.')
    with r:
        st.markdown('#### Missing-data audit')
        st.dataframe(completeness(raw).query('Missing > 0'),use_container_width=True,hide_index=True)
    st.divider()
    title('Ranked scientific findings','Research priority, not a hazard/safety score. Change ranking weights to see why findings move.')
    weights={}
    cols=st.columns(5)
    for col,key in zip(cols,['Support','Magnitude','Coverage','Reproducibility','Habitat relevance']):
        with col:weights[key]=st.slider(key,0,5,3 if key!='Habitat relevance' else 5,key='fw_'+key)
    items=rank_findings(findings(full),weights)
    st.dataframe(items[['Rank','Title','Class','Pillar','Evidence','Rank score / 100']],use_container_width=True,hide_index=True,
        column_config={'Rank score / 100':st.column_config.NumberColumn(format='%.1f')})
    pick=st.selectbox('Inspect finding and ranking rationale',items['Title'].tolist())
    row=items[items.Title==pick].iloc[0]
    st.markdown(f'**{row["Class"]}:** {row["Evidence"]}')
    st.write('**Interpretation:**',row['Interpretation']);st.write('**Limitations:**',row['Limits'])
    st.caption(f'Method: {row["Method"]}. Rubric: '+', '.join(f'{k}={row[k]}/5' for k in weights)+f'. Weighted score = 20 × Σ(weight×criterion)/Σ(weights). Editorial inputs, not objective hazards.')
    with st.expander('Original column mapping, cleaning log, and source digest'):
        st.dataframe(pd.DataFrame({'Mapped field':list(mapping),'Source column':[mapping[k] for k in mapping]}),hide_index=True)
        st.dataframe(audit,use_container_width=True,hide_index=True)
        st.code(f'SHA256: {source_hash}')
        st.caption('All 274 source rows are retained. Filtering changes only the view, not the raw CSV.')

elif page=='Investigation explorer':
    title('Investigation explorer','A sourced metadata catalog. Only FLEX experiment-level observations are loaded; unknown facts explicitly require PSI verification.')
    alert('Rankings indicate **team-assessed relevance for research discovery**, not a NASA rating or a quantitative fire-risk assessment. Sources link to original NASA pages.')
    col=st.columns(4)
    cw={}
    for c,key,label in zip(col,['applicability','atmosphere','measurement_utility','source_quality'],['Crew-material match','Atmosphere match','Diagnostic usefulness','Source completeness']):
        with c:cw[key]=st.slider(label,0,5,3,key='cw_'+key)
    st.caption('Edit the 0–5 assessment values below; research relevance score = weighted rubric / 5, scaled to 100. Scores are editorial, not experimental measurements.')
    rubric=cat[['investigation','applicability','atmosphere','measurement_utility','source_quality']].copy()
    edited=st.data_editor(rubric,hide_index=True,use_container_width=True,num_rows='fixed',disabled=['investigation'],key='catalog_editor',
        column_config={key:st.column_config.NumberColumn(key,min_value=0,max_value=5,step=1) for key in cw})
    ranking=cat.merge(edited,on='investigation',suffixes=('_old',''))
    ranking['Research relevance / 100']=sum(ranking[key]*weight for key,weight in cw.items())/(sum(cw.values()) or 1)*20
    ranking=ranking.sort_values('Research relevance / 100',ascending=False)
    s=st.text_input('Filter by investigation or objective',placeholder='e.g. smoke, droplets, Saffire, cool flames')
    pillar=st.selectbox('Fire-safety research pillar',['All','Prevention','Detection','Suppression'])
    shown=ranking.copy()
    if s:shown=shown[shown.investigation.str.contains(s,case=False,regex=False)|shown.objective.str.contains(s,case=False,regex=False)]
    if pillar!='All':shown=shown[shown.pillar==pillar]
    st.dataframe(shown[['investigation','pillar','objective','fuel_geometry','conditions','data_loaded','Research relevance / 100','source_url']],hide_index=True,use_container_width=True,
        column_config={'source_url':st.column_config.LinkColumn('NASA / PSI source'),'Research relevance / 100':st.column_config.NumberColumn(format='%.1f')})
    st.divider();title('Compare two investigations','Similarity = shared topical metadata; it does not imply experimental interchangeability.')
    a,b=st.columns(2)
    with a:n1=st.selectbox('Investigation A',cat.investigation.tolist(),index=0)
    with b:n2=st.selectbox('Investigation B',cat.investigation.tolist(),index=min(11,len(cat)-1))
    if n1==n2:st.info('Choose two different investigations.')
    else:
        r1=cat.set_index('investigation').loc[n1];r2=cat.set_index('investigation').loc[n2]
        comparison=pd.DataFrame({'Field':['Objective','Fuel / geometry','Conditions','Measurements','Hardware','Research pillar','Data loaded','Source note'],
          n1:[r1[x] for x in ['objective','fuel_geometry','conditions','measurements','hardware','pillar','data_loaded','source_note']],
          n2:[r2[x] for x in ['objective','fuel_geometry','conditions','measurements','hardware','pillar','data_loaded','source_note']]})
        st.dataframe(comparison,hide_index=True,use_container_width=True)
        st.write('**Similarity:**',f'Both are grouped as {r1.pillar.lower()} research.' if r1.pillar==r2.pillar else 'These investigations address different pillars of fire-safety research.')
        st.write('**Difference:**',f'{n1}: {r1.objective}  |  {n2}: {r2.objective}')
        st.markdown(f'**Sources:** [A — NASA]({r1.source_url}) · [B — NASA]({r2.source_url})')
        # Two source-backed research evidence cards, intentionally separate from
        # FLEX's observation-level table and user-adjustable ranking numbers.
        verified=evidence_lib[evidence_lib.investigation.isin([n1,n2])]
        if not verified.empty:
            with st.expander('NASA source-linked evidence for selected investigations',expanded=True):
                for inv in (n1,n2):
                    hits=retrieval(inv+' '+str(cat.set_index('investigation').loc[inv].objective),max_results=2,groups=[inv])
                    if not hits.empty:
                        st.markdown(f'**{inv} · research source evidence**')
                        for _,ev in hits.iterrows():
                            st.markdown(f'- {ev["claim"]} **[{ev["evidence_id"]}]({ev["source_url"]})**')
                st.caption('Source paraphrases are not loaded observation-level measurements or a NASA-endorsed ranking.')
    alert('Rocket propulsion/propellant fire safety is outside this platform’s challenge scope. The investigation catalog is a discovery index, not a complete ingestion of NASA PSI.', 'caution')

elif page=='Combustion explorer':
    title('Combustion explorer',f'{len(view)} filtered FLEX observations. Hover to inspect original test numbers; filters are non-destructive.')
    s,res,curves=fit_fuels(view)
    q=view.dropna(subset=['oxygen','burn'])
    if len(q):
        fig=px.scatter(q,x='oxygen',y='burn',color='fuel',custom_data=['record_id','identifier','pressure','diameter','outcome'],
            labels={'oxygen':'Initial O₂ mole fraction','burn':'Burning-rate column (original header: mm)'},color_discrete_sequence=COLORS)
        fig.update_traces(hovertemplate='O₂=%{x:.3f}<br>Rate field=%{y:.3f}<br>FLEX record=%{customdata[0]}<br>Identifier=%{customdata[1]}<br>Pressure=%{customdata[2]} mmHg<br>Diameter=%{customdata[3]} mm<br>Outcome=%{customdata[4]}<extra></extra>')
        for fuel,curve in curves.items():
            fig.add_trace(go.Scatter(x=curve.oxygen,y=curve.hi,mode='lines',line=dict(width=0),legendgroup=fuel,showlegend=False,hoverinfo='skip'))
            fig.add_trace(go.Scatter(x=curve.oxygen,y=curve.lo,mode='lines',fill='tonexty',fillcolor='rgba(60,115,155,.12)',line=dict(width=0),legendgroup=fuel,showlegend=False,hoverinfo='skip'))
            fig.add_trace(go.Scatter(x=curve.oxygen,y=curve.fit,name=f'{fuel} OLS',mode='lines',line=dict(width=2)))
        chart(fig,430)
        st.caption('Bands show 95% **confidence intervals for the fitted mean**, not prediction intervals for individual experiments.')
    else:st.info('No complete oxygen/burning-rate pairs under current filters.')
    a,b=st.columns(2)
    with a:
        title('Pressure vs. burning rate')
        q=view.dropna(subset=['pressure','burn'])
        if len(q):chart(px.scatter(q,x='pressure',y='burn',color='fuel',hover_data=['record_id','outcome'],color_discrete_sequence=COLORS),315)
    with b:
        title('Initial diameter vs. burn time')
        q=view.dropna(subset=['diameter','burntime'])
        if len(q):chart(px.scatter(q,x='diameter',y='burntime',color='fuel',hover_data=['record_id','outcome'],color_discrete_sequence=COLORS),315)
    c,d=st.columns(2)
    with c:
        title('Burn rate vs. burn time')
        q=view.dropna(subset=['burn','burntime'])
        if len(q):chart(px.scatter(q,x='burn',y='burntime',color='fuel',hover_data=['record_id'],color_discrete_sequence=COLORS),315)
    with d:
        title('Oxygen by test-end outcome')
        if len(view):chart(px.box(view,x='outcome',y='oxygen',color='outcome',points='all',color_discrete_sequence=COLORS),315)
    alert('The original CSV literally labels its rate field “Burning rate; mm”. The physical meaning and unit must be verified with the original NASA data dictionary before treating it as mm²/s or drawing dimensional conclusions.','caution')
    with st.expander('View records behind the plots'):
        st.dataframe(precision_frame(view,['record_id','identifier','fuel','oxygen','pressure','diameter','burn','burntime','outcome','co','helium']),hide_index=True,use_container_width=True)

elif page=='Fuel comparison lab':
    title('Fuel comparison lab','Recomputed directly from the complete-case subset. Previous team numbers are checked rather than assumed.')
    summary,residual,curves=fit_fuels(view)
    if len(summary):
        st.dataframe(summary,hide_index=True,use_container_width=True,column_config={'Slope':st.column_config.NumberColumn(format='%.5f'),'Residual variance':st.column_config.NumberColumn(format='%.6f')})
        a,b=st.columns(2)
        with a:
            title('Recorded outcome frequency by fuel')
            counts=view.groupby(['fuel','outcome']).size().reset_index(name='Runs')
            if len(counts):chart(px.bar(counts,x='fuel',y='Runs',color='outcome',barmode='group',color_discrete_sequence=COLORS),330)
        with b:
            title('Fuel-specific regression residuals')
            if len(residual):chart(px.violin(residual,x='fuel',y='residual',color='fuel',box=True,points='all',color_discrete_sequence=COLORS),330)
        d=diagnostic_data(view)
        if d['interaction']:
            i=d['interaction'];st.write(f'**Fuel × O₂ interaction (HC3 robust):** coefficient {i["coefficient"]:.5f}, p={i["p"]:.5g}, 95% CI [{i["ci_low"]:.3f}, {i["ci_high"]:.3f}].')
            alert('A non-significant interaction means this sample did not detect a difference in slopes. **It is not evidence that the fuels have equivalent slopes.**')
    else:st.warning('Select both fuels with sufficient oxygen/rate observations.')
    st.divider();title('Team-result verification','Checks the original 274-row table, independent of sidebar filters. Tolerances are visible.')
    verified=verification_table(full)
    st.dataframe(verified,hide_index=True,use_container_width=True)
    alert('Brown–Forsythe is median-centered Levene applied to fuel-specific OLS residuals. The earlier residual variance figures may differ because of variance denominator conventions; no match is silently forced.')

elif page=='Stability & uncertainty':
    title('Stability & uncertainty','Inspect residual variation, statistical diagnostics and source-record flags. Flagged does not mean erroneous.')
    d=diagnostic_data(view)
    res=d['residuals']
    if not res.empty:
        l,r=st.columns(2)
        with l:
            title('Residual vs. fitted')
            fig=px.scatter(res,x='fitted',y='residual',color='fuel',hover_data=['record_id','cooks_d'],color_discrete_sequence=COLORS)
            fig.add_hline(y=0,line_dash='dash',line_color='#8996A4');chart(fig,320)
        with r:
            title('Cook’s distance by original test number')
            fig=px.scatter(res,x='id',y='cooks_d',color='flag_cooks',hover_data=['record_id','fuel'],color_discrete_map={True:'#B86A52',False:'#2A6E9E'})
            chart(fig,320)
    nums=[]
    for key,label in [('brown_forsythe','Brown–Forsythe'),('levene','Levene (mean-centered)'),('breusch_pagan','Breusch–Pagan'),('white','White test')]:
        item=d.get(key)
        nums.append({'Test':label,'Statistic':item['stat'] if item else None,'p-value':item['p'] if item else None})
    st.dataframe(pd.DataFrame(nums),hide_index=True,use_container_width=True)
    st.caption('Breusch–Pagan and White tests use the combined fuel×oxygen interaction model; fuel-specific residual tests use separate OLS fits.')
    alert('Four distinct concepts: measurement uncertainty (instrument precision, not supplied); model prediction uncertainty (requires validation); residual variation (fitted-model error); experimental variability (differences in repeated physical conditions). These are **not interchangeable**.','caution')
    title('Influence sensitivity','A second view omits Cook-flagged records for analysis only; the original CSV and default results are unchanged.')
    if len(view)>25:st.dataframe(sensitivity(view),hide_index=True,use_container_width=True)
    flags=audit_flags(view,res)
    title('Anomaly hunter',f'{len(flags)} flags across {flags.Record.nunique() if len(flags) else 0} distinct source records. Multiple reasons can flag the same record.')
    if len(flags):
        choice=st.selectbox('Inspect original flagged record',flags.Record.unique().tolist())
        st.dataframe(flags[flags.Record==choice],hide_index=True,use_container_width=True)
        record=view[view.record_id==choice]
        if len(record):
            st.markdown('**Original CSV values (verbatim):**')
            st.dataframe(raw.iloc[record.index],hide_index=True,use_container_width=True)
        with st.expander('See all flags'):st.dataframe(flags,hide_index=True,use_container_width=True)
    else:st.info('No flags under the current selection and rules.')

elif page=='Predictive intelligence':
    title('Predictive intelligence','Fitted models are exploratory research aids. Performance is measured out-of-fold, not on training predictions.')
    with st.spinner('Evaluating regression models across pressure groups…'):
        reg=model_a(full)
    title('Model A · Burning-rate regression')
    if 'error' in reg:st.warning(reg['error'])
    else:
        alert(f'Validation: {reg["method"]}. Complete-case model cohort N={len(reg["frame"])}. Raw records remain intact.')
        st.dataframe(reg['summary'],hide_index=True,use_container_width=True)
        a,b=st.columns(2)
        with a:
            title('Observed vs. grouped-CV prediction')
            fig=px.scatter(reg['oof'],x='Measured',y='Random Forest',hover_data=['Record'])
            lo=min(reg['oof'].Measured.min(),reg['oof']['Random Forest'].min());hi=max(reg['oof'].Measured.max(),reg['oof']['Random Forest'].max())
            fig.add_shape(type='line',x0=lo,y0=lo,x1=hi,y1=hi,line=dict(dash='dash',color='#B96459'))
            chart(fig,345)
        with b:
            title('Random Forest feature importance')
            chart(px.bar(reg['importance'],x='Importance',y='Feature',orientation='h',color_discrete_sequence=COLORS),345)
        st.write(f'**Empirical residual interval:** ±{reg["interval_halfwidth"]:.4f}, based on the 90th percentile of absolute grouped-CV errors. It is not a calibrated 90% conditional prediction interval.')
        with st.expander('Inspect pressure-fold performance'):st.dataframe(reg['folds'],hide_index=True,use_container_width=True)
    st.divider();title('Model B · Test-end outcome classifier')
    with st.spinner('Evaluating stratified out-of-fold classification…'):
        clf=model_b(full)
    if 'error' in clf:st.warning(clf['error'])
    else:
        a,b,c=st.columns(3)
        with a:st.metric('Macro-F1 (stratified CV)',f'{clf["macro_f1"]:.3f}')
        with b:st.metric('Multiclass Brier',f'{clf["brier"]:.3f}')
        with c:st.metric('Log loss',f'{clf["logloss"]:.3f}')
        st.dataframe(clf['metrics'],hide_index=True,use_container_width=True)
        l,r=st.columns(2)
        with l:
            title('Confusion matrix · actual by predicted')
            heat=px.imshow(clf['confusion'],text_auto=True,color_continuous_scale=['#EEF4F8','#2476A9'])
            chart(heat,335)
        with r:
            title('Calibration check · aggregated out-of-fold')
            cdf=clf['calibration']
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=cdf['Mean confidence'],y=cdf['Observed accuracy'],mode='markers+lines',marker_size=9,name='Observed'))
            fig.add_trace(go.Scatter(x=[0,1],y=[0,1],mode='lines',line_dash='dash',name='Ideal'))
            fig.update_layout(xaxis_title='Mean confidence per bin',yaxis_title='Fraction correct')
            chart(fig,335)
        if not clf['reliable']:
            alert('**Classifier reliability gate FAILED:** at least one predefined rule (macro-F1 ≥ 0.55 and every class recall ≥ 0.40) was not met. Per-scenario outcome probabilities are therefore hidden.','caution')
        else:
            alert('Internal reliability gate passed. Probabilities are STILL not used for habitat safety decisions: these results lack external, pressure-grouped and prospective validation.')
        st.caption(clf['note'])

elif page=='Artemis scenario explorer':
    title('Artemis scenario explorer', 'User-defined atmosphere examples are not NASA FLEX test records or fire-safety certification.')
    alert('<b>USER-DEFINED SCENARIO — NOT AN OBSERVED NASA EXPERIMENT.</b> Atmospheric references are documented NASA design or screening conditions; neither is a proven fire-safety boundary.','caution')
    ref_choice=st.selectbox('Atmosphere reference',[
        'NASA exploration atmosphere — 34% O₂, 8.2 psia',
        'Historical materials test — 30% O₂, 10.2 psia',
        'Custom experimental scenario'])
    reference=EXPLORATION if ref_choice.startswith('NASA exploration') else HISTORICAL if ref_choice.startswith('Historical') else None
    a,b,c,d=st.columns(4)
    with a:fuel=st.selectbox('Droplet fuel',sorted(full.fuel.dropna().unique()))
    with b:o2=st.number_input('O₂ (%)',min_value=10.,max_value=60.,value=(reference['oxygen']*100 if reference else 25.),step=1.)
    with c:psi=st.number_input('Atmospheric pressure (psia)',min_value=1.,max_value=40.,value=(reference['psi'] if reference else 14.7),step=.2)
    with d:diam=st.number_input('Droplet diameter (mm)',min_value=.1,max_value=9.,value=3.,step=.1)
    scenario={'fuel':fuel,'oxygen':o2/100,'pressure':psi_to_pressure(psi),'diameter':diam}
    explored=reference_count(full,EXPLORATION)
    historic=reference_count(full,HISTORICAL)
    m1,m2,m3=st.columns(3)
    with m1:st.metric('Exploration-reference query coverage',f'{explored} / {len(full)}',help='Descriptive O₂≥34%, P≤8.2 psia query; not a NASA-defined atmosphere band.')
    with m2:st.metric('Historical-test query coverage',f'{historic} / {len(full)}',help='Descriptive O₂≥30%, P≤10.2 psia query; not a NASA-defined atmosphere band.')
    with m3:st.metric('Scenario pressure',f'{scenario["pressure"]:.1f} mmHg')
    fig=px.scatter(full,x='oxygen',y='pressure',color='fuel',hover_data=['record_id','outcome'],color_discrete_sequence=COLORS)
    fig.add_trace(go.Scatter(x=[EXPLORATION['oxygen']],y=[psi_to_pressure(EXPLORATION['psi'])],
        mode='markers',marker=dict(symbol='diamond',size=14,color='#A77B25'),
        name='Exploration atmosphere: 34%, 8.2 psia'))
    fig.add_trace(go.Scatter(x=[HISTORICAL['oxygen']],y=[psi_to_pressure(HISTORICAL['psi'])],
        mode='markers',marker=dict(symbol='square',size=12,color='#7290A4'),
        name='Historical test: 30%, 10.2 psia'))
    fig.add_trace(go.Scatter(x=[scenario['oxygen']],y=[scenario['pressure']],mode='markers',
        marker=dict(symbol='star',size=16,color='#18344f'),name='User-defined scenario'))
    fig.update_layout(xaxis_title='Initial oxygen mole fraction',yaxis_title='Pressure (mmHg)');chart(fig,385)
    st.caption('The two NASA conditions are POINT references, not validated flammability or habitat-safety bands. Data gap counts query the broader quadrants O₂ ≥ reference and pressure ≤ reference; they are not claims of direct experiment matching.')
    st.markdown(f'**Sources:** [NASA exploration atmosphere]({EXPLORATION["url"]}) · [Historical spacecraft materials tests]({HISTORICAL["url"]})')
    nearby=scenario_neighbors(full,scenario)
    st.markdown(f'**Joint-domain status:** `{nearby["domain"]}` — {nearby["reason"]}')
    if len(nearby['neighbors']):
        st.markdown('#### Nearest historical FLEX records (same fuel)')
        st.dataframe(precision_frame(nearby['neighbors'],['record_id','fuel','oxygen','pressure','diameter','burn','outcome','normalized_distance']),hide_index=True,use_container_width=True)
    reg=model_a(full)
    # A joint reference quadrant with no experiments is intentionally out of predictive scope.
    empty_reference_region = bool((o2>=34 and psi<=8.2 and explored==0) or (o2>=30 and psi<=10.2 and historic==0))
    prediction=scenario_prediction(reg,scenario,nearby,moon_band=empty_reference_region)
    if prediction.get('prediction') is None:alert('**Model output withheld:** '+prediction.get('reason','Unsupported input region.'),'caution')
    else:
        st.metric('Exploratory predicted rate field',f'{prediction["prediction"]:.4f}',f'Empirical residual band: {prediction["lower"]:.4f} to {prediction["upper"]:.4f}')
        st.caption(prediction['method'])
    alert('A real habitat assessment needs experiments with solid cabin materials, airflow and ventilation, more atmospheric settings, replicates, qualified sensors and external validation.')
    fs=rank_findings(findings(full),{'Support':3,'Magnitude':3,'Coverage':3,'Reproducibility':3,'Habitat relevance':5})
    brief=build_markdown(scenario,nearby,prediction,fs,reg,source_hash)
    st.download_button('Download evidence-grounded research brief (.md)',data=brief,file_name='FlameX_research_brief.md',mime='text/markdown')
    st.download_button('Download printable research brief (.html)',data=markdown_to_html(brief),file_name='FlameX_research_brief.html',mime='text/html')
    st.session_state['scenario_latest']={'scenario':scenario,'neighbors':nearby,'prediction':prediction}

elif page=='FlameIQ research assistant':
    title('FlameIQ · ask freely',
          'Type your own question. Offline mode searches NASA sources; optional language-model modes can have natural conversations about your evidence.')
    alert('**Two answer types:** Research evidence = retrieved NASA/FLEX evidence only. General Q&A = conversational AI discussion, clearly NOT NASA-verified. Missing raw experiments cannot be invented.')
    a,b,c=st.columns(3)
    with a:metric('NASA source entries',len(evidence_lib),'traceable source descriptions')
    with b:metric('Covered investigations',evidence_lib.investigation.nunique(),'FLEX · BASS-II · Saffire')
    with c:metric('Selected FLEX records',len(view),'original CSV unchanged')
    mode=st.selectbox('Conversation engine',BACKENDS,index=0,help='Offline search works immediately. OpenAI requires your private API key. Ollama uses a downloaded language model on your local computer.')
    scope=st.radio('Answer scope',['Research evidence','General Q&A'],horizontal=True,
                   help='General Q&A is available only with an LLM and does not make NASA-verified research claims.')
    ollama_model='llama3.2:3b'
    if mode==BACKENDS[1]:
        if configured_key():st.success('Private OpenAI key detected in environment / Streamlit Secrets. Hosted AI calls may incur usage charges.')
        else:st.info('OpenAI selected, but no key is configured. Set OPENAI_API_KEY privately, or choose offline search / Ollama.')
    elif mode==BACKENDS[2]:
        ollama_model=st.text_input('Installed local Ollama model',value='llama3.2:3b',help='Example: llama3.2:3b. Download with `ollama pull llama3.2:3b` after installing Ollama. Works only where Ollama runs.')
        st.caption('Ollama runs only on the Streamlit host computer. It is not a public cloud backend and requires sufficient local resources.')
    else:
        st.caption('**No-key offline evidence search** accepts any wording but only retrieves and calculates from the available NASA/FLEX evidence. It cannot behave like a full generative language model.')
    if mode==BACKENDS[0] and scope=='General Q&A':
        st.info('Select OpenAI or Ollama for free-form general conversation. Offline mode answers research questions using retrieved evidence.')
    suggestions=[
        'Why might BASS-II and Saffire complement FLEX for crew-habitat research?',
        'What do the fuel regressions reveal and what can they not prove?',
        'Compare the two NASA atmospheric reference points and dataset coverage.',
        'Explain why Saffire-II exact numerical results cannot be shown.',
    ]
    example=st.selectbox('Optional example question',['— I will type my own —']+suggestions)
    if 'flameiq_chat' not in st.session_state:st.session_state['flameiq_chat']=[]
    for role,msg in st.session_state['flameiq_chat']:
        with st.chat_message(role):st.markdown(msg)
    user_q=st.chat_input('Ask FlameIQ anything; unsupported research facts will be marked UNKNOWN…')
    if st.button('Ask example') and example!='— I will type my own —':user_q=example
    if user_q:
        previous=st.session_state['flameiq_chat'][-6:]
        st.session_state['flameiq_chat'].append(('user',user_q))
        if mode==BACKENDS[0]:
            rendered=answer(user_q,view,cat,scenario=st.session_state.get('scenario_latest'))
        else:
            rendered,error=model_reply(user_q,view,cat,mode,scope=scope,history=previous,
                       ollama_model=ollama_model,scenario=st.session_state.get('scenario_latest'))
            if error:
                rendered=f'**Model not connected:** {error}\n\n**Evidence-only fallback:**\n\n'+answer(user_q,view,cat)
        st.session_state['flameiq_chat'].append(('assistant',rendered));st.rerun()
    if st.button('Clear conversation'):st.session_state['flameiq_chat']=[];st.rerun()
    with st.expander('Browse the NASA evidence library and source links',expanded=False):
        st.caption('Entries are traceable paraphrases of linked NASA source descriptions, NOT newly loaded numerical experiments.')
        st.dataframe(evidence_lib[['evidence_id','investigation','topic','claim','source_url','raw_data_loaded']],
                     hide_index=True,use_container_width=True,
                     column_config={'source_url':st.column_config.LinkColumn('NASA source')})
        st.download_button('Download NASA evidence library (.csv)',evidence_lib.to_csv(index=False),
                           file_name='FlameX_NASA_evidence_library.csv',mime='text/csv')
    st.caption('No API key is bundled. Language-model answers can still make mistakes: verify them against the accompanying evidence and calculations. Set an API budget before making hosted mode publicly available. The app cannot certify fire safety.')

elif page=='Research brief & sources':
    title('Research brief & sources','Provenance, science boundaries and what can be claimed for the submission.')
    st.markdown('#### Research scope')
    alert('**One FLEX observation table** (274 rows) is loaded; the investigation catalog contains NASA-linked descriptions only. No raw Saffire, BASS, ACME, SAME, CFI, SPICE or SLICE experiment measurements are loaded.')
    st.markdown('#### Three pillars of fire safety')
    a,b,c=st.columns(3)
    with a:st.markdown('**Prevention**\n\nHow combustion, flame spread and habitat materials depend on local conditions; other NASA investigations provide more directly relevant solid-fuel evidence.')
    with b:st.markdown('**Detection**\n\nSmoke and aerosol observations help frame questions for future detector research; not measurable from the loaded droplet CSV alone.')
    with c:st.markdown('**Suppression**\n\nFLEX addresses liquid droplet extinction and candidate inert-gas effects; the loaded CSV includes original CO-labeled and helium composition columns, not measured whole-habitat suppression efficacy.')
    st.markdown('#### Earth applications (context, not additional datasets)')
    st.write('The team-supplied challenge description mentions fine-water-mist extinguishing, smoke detection and firefighter equipment as related application themes. These applications are **not directly evaluated** by the loaded FLEX table.')
    st.markdown('#### NASA source-linked research evidence library')
    st.caption('Structured NASA metadata paraphrases for FLEX, BASS-II and Saffire; each claim links to a NASA source. Only FLEX raw measurements are loaded.')
    st.dataframe(evidence_lib[['evidence_id','investigation','topic','source_url']],hide_index=True,use_container_width=True, column_config={'source_url':st.column_config.LinkColumn('NASA source')})
    st.markdown('#### Original source and NASA investigation references')
    st.write(f'**Experimental source:** uploaded FLEX CSV. SHA256: `{source_hash}`')
    st.markdown(f'**Challenge page:** {CHALLENGE}')
    st.markdown('**FLEX PSI dataset:** https://psi.nasa.gov/physci/repo/data/investigations/PSI-69')
    st.markdown('**NASA investigations index:** https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/')
    st.dataframe(cat[['investigation','source_url','source_note','data_loaded']],hide_index=True,use_container_width=True,column_config={'source_url':st.column_config.LinkColumn('NASA source')})
    st.markdown('#### Verification and disclosure')
    st.write('Statistical tests and model results are generated at runtime from the original CSV. Catalog scores are user-adjustable editorial judgments. The project uses code and text produced with AI assistance; optional FlameIQ model-generated paraphrases must be identified separately if enabled.')
    st.write('No NASA imagery, logo, insignia or endorsement is used in the original FlameX interface.')
    st.markdown('#### Download sources')
    st.download_button('Download the original FLEX CSV',raw_blob,file_name='flame_intelligence_master.csv',mime='text/csv')
    st.download_button('Download the referenced investigation catalog',cat.to_csv(index=False),file_name='investigations.csv',mime='text/csv')
    st.download_button('Download column-cleaning audit',audit.to_csv(index=False),file_name='cleaning_audit.csv',mime='text/csv')
    if st.session_state.get('scenario_latest'):
        item=st.session_state['scenario_latest'];reg=model_a(full)
        ranked=rank_findings(findings(full),{'Support':3,'Magnitude':3,'Coverage':3,'Reproducibility':3,'Habitat relevance':5})
        brief=build_markdown(item['scenario'],item['neighbors'],item['prediction'],ranked,reg,source_hash)
        st.download_button('Download latest scenario brief',brief,'FlameX_research_brief.md',mime='text/markdown')
    else:st.caption('To generate a scenario-specific research brief, visit Artemis scenario explorer and set a user-defined scenario.')

st.divider()
st.caption('FlameX Intelligence · Team Dynamic Duo · Independent NASA Space Apps project · No NASA affiliation/endorsement · Experimental evidence, not operational fire-safety advice.')
