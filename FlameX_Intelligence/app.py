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
from modules.research_engine import ask_research
from modules.atmospheres import EXPLORATION, HISTORICAL, reference_count
from modules.evidence_retrieval import load_evidence, retrieval, evidence_comparison
from modules.report_generator import build_markdown,markdown_to_html
from modules.psi_lab import psi_catalog, read_psi_csv, column_audit, measurement_view, source_coverage, study_data_answer
from modules.judge_brief import STORY_QUESTIONS, evidence_brief

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
.stApp{background:#f6f8fa;color:#1e3042} .block-container{padding-top:5rem!important;max-width:1460px;padding-bottom:3rem}
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
/* Navigation and homepage enhancements: deliberately retain the original FlameX palette. */
section[data-testid="stSidebar"] [data-testid="stRadio"] label{font-size:.89rem}
section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"]{gap:.2rem}
section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label{padding:5px 7px;border-radius:8px}
section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:hover{background:#eaf2f7}
.nav-caption{font-size:11px;text-transform:uppercase;font-weight:800;letter-spacing:1.5px;color:#637588;margin-top:3px}
.hero{border:1px solid #dce4ea;border-radius:16px;background:linear-gradient(115deg,#fff 0%,#f0f6fa 68%,#e6f1f7 100%);padding:31px 34px;margin:4px 0 16px;box-shadow:0 12px 34px rgba(24,52,79,.035)}
.hero h1{font-family:Manrope,system-ui,sans-serif!important;font-size:clamp(30px,3.2vw,47px)!important;font-weight:800;line-height:1.15;letter-spacing:-1.7px;margin:12px 0 12px!important;max-width:900px}
.hero .hero-underlined{color:#2878a5;border-bottom:4px solid #9fd0e9;text-decoration:none;white-space:normal}
.hero-sub{font-size:15px;color:#526a7e;line-height:1.65;max-width:750px}
.hero-footer{font-size:11px;font-weight:700;letter-spacing:.65px;color:#627588;margin-top:17px}
.hero-tag{display:inline-block;padding:6px 10px;font-weight:700;font-size:11px;color:#2878a5;border:1px solid #c4dfed;border-radius:100px;background:rgba(255,255,255,.83)}
.finding-spotlight{border-radius:13px;border:1px solid #c8dfe9;background:#f1f7fa;padding:20px 23px;margin:12px 0}
.finding-spotlight h2{font-family:Manrope,sans-serif!important;font-size:23px!important;line-height:1.36!important;letter-spacing:-.6px!important;margin:3px 0 9px!important}
.finding-spotlight em{font-style:normal;color:#2878a5;border-bottom:2px solid #80b5d0}
.finding-spotlight p{font-size:13px;color:#425a6c;line-height:1.65;margin-bottom:7px}
.finding-spotlight .spotlight-k{font-weight:800;color:#2878a5;font-size:10px;letter-spacing:1.5px;text-transform:uppercase}
.journey-card{background:#fff;border:1px solid #dce4ea;border-radius:12px;padding:16px 19px;min-height:118px;margin:8px 0}
.journey-card strong{font-family:Manrope,sans-serif;color:#18344f;font-size:14px}
.journey-card p{font-size:12px;color:#627588;line-height:1.5;margin:7px 0 0}
.quicknav-note{font-size:12px;color:#64778a;margin:0 0 10px}
.page-masthead{background:white;border:1px solid #dce4ea;border-left:4px solid #2878a5;padding:15px 19px;border-radius:10px;margin:6px 0 14px}
.page-masthead .brand{font-size:19px}
.page-masthead .deck{font-size:12px}
@media (max-width:730px){.hero{padding:20px 19px}.hero h1{font-size:30px!important}.block-container{padding-top:.8rem}}
</style>''',unsafe_allow_html=True)

def alert(msg,kind='notice'):
    st.markdown(f'<div class="{kind}">{msg}</div>',unsafe_allow_html=True)
def metric(label,value,note=''):
    st.markdown(f'<div class="metric"><div class="k">{label}</div><div class="v">{value}</div><div class="n">{note}</div></div>',unsafe_allow_html=True)
def chart(fig,height=360):
    fig.update_layout(height=height,margin=dict(l=12,r=14,t=25,b=20),font_family='DM Sans',font_color='#29425b',
        plot_bgcolor='white',paper_bgcolor='white',legend_title_text='',
        xaxis=dict(gridcolor='#E9EDF1',zeroline=False),yaxis=dict(gridcolor='#E9EDF1',zeroline=False))
    st.plotly_chart(fig,width='stretch',config={'displaylogo':False,'toImageButtonOptions':{'format':'png','scale':2}})
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

# One persistent navigation state drives both the sidebar and the homepage shortcuts.
# Buttons use callbacks so Streamlit updates widget state *before* the next render.
PAGES=['Mission overview','Guided Tour','Investigation explorer','Combustion explorer','Fuel comparison lab','Stability & uncertainty',
       'Predictive intelligence','Artemis scenario explorer','NASA data lab','FlameIQ research assistant','Research brief & sources']
PAGE_ICONS={'Mission overview':'🏠','Investigation explorer':'🔎','Combustion explorer':'🧪',
    'Fuel comparison lab':'⚗️','Stability & uncertainty':'📊','Predictive intelligence':'📈',
    'Artemis scenario explorer':'🌙','NASA data lab':'🗂️','FlameIQ research assistant':'💬',
    'Guided Tour':'🎯','Research brief & sources':'📚'}

def navigate_to(destination):
    if destination in PAGES:
        st.session_state['active_page']=destination

def clear_experiment_filters():
    for key in ('flame_filter_fuels','flame_filter_outcomes','flame_filter_oxygen','flame_filter_pressure'):
        st.session_state.pop(key,None)

st.sidebar.markdown('<div class="eyebrow">DYNAMIC DUO · 2026 SPACE APPS</div><div class="brand" style="font-size:24px">FlameX <span style="color:#2878a5">Intelligence</span></div>',unsafe_allow_html=True)
st.sidebar.caption('Explore the evidence. Understand its limits.')
st.sidebar.markdown('<div class="nav-caption">Research desk · choose a page</div>',unsafe_allow_html=True)
page=st.sidebar.radio('Research desk',PAGES,label_visibility='collapsed',key='active_page',
                      format_func=lambda name: PAGE_ICONS.get(name,'•')+'  '+name)
st.sidebar.button('▶  Start Guided Tour',on_click=navigate_to,args=('Guided Tour',),
                  width='stretch',key='sidebar_judge_demo')
st.sidebar.divider()
with st.sidebar.expander('⚙️  Dataset & column mapping',expanded=False):
    st.caption('The original FLEX CSV is loaded automatically; upload a replacement only if needed.')
    upload=st.file_uploader('Replace FLEX experimental table (CSV)',type='csv',
                            help='Optional: the team-supplied 274-row master CSV is already bundled.')
raw_blob=upload.getvalue() if upload else MASTER.read_bytes()
try:raw,source_hash=source_data(raw_blob)
except Exception as e:st.error(f'Unable to load experimental data: {e}');st.stop()

with st.sidebar.expander('🧾  Verify original column names',expanded=False):
    st.caption('Default mappings match the bundled source; no data column is invented.')
    sugg=suggest_mapping(raw.columns);mapping={}
    for key,expected in FIELD_MAP.items():
        names=['— NOT LOADED —']+list(raw.columns)
        default=sugg[key] if sugg.get(key) in raw.columns else '— NOT LOADED —'
        value=st.selectbox(key.replace('_',' ').title(),names,index=names.index(default),key='map_'+key)
        mapping[key]=None if value==names[0] else value
try:full,audit=normalized_view(raw,mapping)
except ValueError as e:st.error(str(e));st.stop()
cat=catalog_data()
evidence_lib=evidence_data()
if 'psi_session_tables' not in st.session_state:st.session_state['psi_session_tables']={}

with st.sidebar.expander('🎚️  Filter experiment views',expanded=False):
    st.caption('These filters change the visible research subset, never the source CSV. Use Reset for a complete view.')
    all_fuel=sorted(full.fuel.dropna().unique().tolist())
    fuels=st.multiselect('Fuel',all_fuel,default=all_fuel,key='flame_filter_fuels')
    all_outcome=sorted(full.outcome.dropna().unique().tolist())
    outcomes=st.multiselect('Test end',all_outcome,default=all_outcome,key='flame_filter_outcomes')
    ox=(float(full.oxygen.min()),float(full.oxygen.max()))
    orng=st.slider('O₂ mole fraction',ox[0],ox[1],ox,step=.01,key='flame_filter_oxygen')
    pmin,pmax=float(full.pressure.min()),float(full.pressure.max())
    prng=st.slider('Pressure (mmHg)',pmin,pmax,(pmin,pmax),step=1.0,key='flame_filter_pressure')
    st.button('↺  Reset experiment filters',on_click=clear_experiment_filters,
              width='stretch',key='reset_experiment_filters')
view=filtered(full,fuels,outcomes,orng,prng)
st.sidebar.caption(f'VIEWING {len(view):,} / {len(full):,} FLEX source rows')
st.sidebar.caption('Independent research prototype · Not NASA-endorsed · Not operational fire-safety advice')

# Always-visible shortcuts; all 11 destinations remain available in the sidebar.
nav_cols=st.columns(4)
for column,label,destination in zip(nav_cols,
        ['🏠 Overview','🧪 Explore data','💬 Ask FlameIQ','🎯 Guided Tour'],
        ['Mission overview','Combustion explorer','FlameIQ research assistant','Guided Tour']):
    with column:
        st.button(label,key='top_nav_'+destination.replace(' ','_'),
                  width='stretch',on_click=navigate_to,args=(destination,),
                  type='primary' if page==destination else 'secondary')

if page!='Mission overview':
    st.markdown('''<div class="page-masthead"><div class="eyebrow">FLAMEX INTELLIGENCE · SCIENTIFIC RESEARCH DESK</div>
      <div class="brand">Evidence-first microgravity combustion</div>
      <div class="deck">NASA-linked investigation discovery · reproducible FLEX analysis · clear uncertainty boundaries</div></div>''',
      unsafe_allow_html=True)

if page=='Mission overview':
    st.markdown('''<section class="hero" aria-label="FlameX research mission">
      <div class="hero-tag">NASA SPACE APPS 2026 · FLAME IN FREEFALL</div>
      <h1>Explore combustion research.<br><span class="hero-underlined">Follow the evidence.</span></h1>
      <div class="hero-sub">FlameX connects NASA investigation sources with reproducible analysis of a loaded FLEX experiment table. Explore what the data reveals, find the gaps, and ask scientific questions without mistaking a model for a safety verdict.</div>
      <div class="hero-footer">SOURCE-LINKED RESEARCH &nbsp; · &nbsp; INTERACTIVE STATISTICS &nbsp; · &nbsp; EVIDENCE-GROUNDED INTELLIGENCE</div>
      </section>''',unsafe_allow_html=True)
    st.markdown('### The intelligence behind FlameX')
    st.caption('Three complementary layers; numerical findings come from measured records, not a text generator.')
    si1,si2,si3=st.columns(3)
    with si1:
        st.markdown('<div class="panelbox"><div class="eyebrow">01 · RESEARCH INTELLIGENCE</div><strong>Source-linked synthesis</strong><p>Trace FLEX, BASS-II, and Saffire research objectives back to NASA investigation pages. Coverage gaps remain visible.</p></div>',unsafe_allow_html=True)
    with si2:
        st.markdown('<div class="panelbox"><div class="eyebrow">02 · PREDICTIVE INTELLIGENCE</div><strong>Reproducible models</strong><p>Inspect FLEX regressions and grouped-validation results. Unsupported extrapolation is withheld.</p></div>',unsafe_allow_html=True)
    with si3:
        st.markdown('<div class="panelbox"><div class="eyebrow">03 · EVIDENCE REASONING</div><strong>FlameIQ · no API key</strong><p>Ask natural research questions. Source-backed calculations and transparent limitations form every numeric answer.</p></div>',unsafe_allow_html=True)
    st.markdown('''<div class="nav-caption">Start anywhere · choose a research path</div>''',unsafe_allow_html=True)
    p1,p2,p3=st.columns(3)
    with p1:
        st.markdown('<div class="journey-card"><strong>01 / See the measurements</strong><p>Explore real FLEX records with linked plots, filters, and original row IDs.</p></div>',unsafe_allow_html=True)
        st.button('Open combustion explorer →',key='home_go_combustion',width='stretch',
                  on_click=navigate_to,args=('Combustion explorer',))
    with p2:
        st.markdown('<div class="journey-card"><strong>02 / Check the explanation</strong><p>Ask FlameIQ a question, inspect its evidence, and discover what remains unknown.</p></div>',unsafe_allow_html=True)
        st.button('Ask FlameIQ →',key='home_go_flameiq',width='stretch',
                  on_click=navigate_to,args=('FlameIQ research assistant',))
    with p3:
        st.markdown('<div class="journey-card"><strong>03 / Present the result</strong><p>Follow a source-audited question and a reproducible, judge-friendly demonstration.</p></div>',unsafe_allow_html=True)
        st.button('Start Guided Tour →',key='home_go_judge',width='stretch',
                  on_click=navigate_to,args=('Guided Tour',))

    st.markdown('### The finding worth investigating')
    st.caption('Choose a question to change the scientific spotlight. All displayed numerical claims are computed from the loaded table.')
    focus=st.radio('Research spotlight', ['Fuel variability','Atmosphere coverage','Scientific trust'],
                   key='homepage_spotlight',horizontal=True,label_visibility='collapsed')
    featured=diagnostic_data(full)
    target='Fuel comparison lab'
    if focus=='Fuel variability':
        ratio=featured.get('variance_ratio')
        bf=featured.get('brown_forsythe')
        if ratio is not None and np.isfinite(ratio) and bf:
            headline=f'The two fuels show <em>{ratio:.2f}× different residual variance.</em>'
            description=(f'For the two fuel-specific oxygen regressions, the larger residual variance is {ratio:.2f} times the smaller. '
                        f'A Brown–Forsythe test gives p = {bf["p"]:.2g}. This supports a difference in model scatter, '
                        'not a direct measurement of flame stability or the cause of the difference.')
        else:
            headline='A <em>fuel comparison</em> requires both fuel groups.'
            description='The currently loaded source does not support a two-fuel residual-variance comparison. Reset the filters or load the original FLEX table.'
        label='Statistical discovery · fuel-specific models'
    elif focus=='Atmosphere coverage':
        target='Artemis scenario explorer'
        n=reference_count(full,EXPLORATION)
        headline=f'Only <em>{n} FLEX records</em> meet the exploration-reference coverage query.'
        description=('This descriptive query asks which loaded records jointly have oxygen ≥34% and pressure ≤8.2 psia. '
                     'It does not establish matching spacecraft tests, a flammability boundary, or safety. '
                     'See the scenario explorer for both NASA reference conditions and the individual observations.')
        label='Data gap · NASA atmosphere reference'
    else:
        target='Guided Tour'
        headline='A credible answer must show <em>what the data cannot prove.</em>'
        description=('FlameX separates recorded experiments, computed statistics, research interpretations, '
                     'and missing measurements. For example, a difference in model residual scatter cannot be '
                     'renamed a physical flame-stability threshold. Follow the evidence trail in the guided demo.')
        label='Research quality · evidence boundaries'
    st.markdown(f'<div class="finding-spotlight"><div class="spotlight-k">{label}</div><h2>{headline}</h2><p>{description}</p></div>',
                unsafe_allow_html=True)
    # The evidence preview follows the selected scientific question. Hover a
    # point/bar to inspect values; it is never a rendered physics simulation.
    if focus=='Fuel variability' and not featured['summary'].empty:
        variance_frame=featured['summary'][['Fuel','Residual variance','N']].copy()
        if len(variance_frame):
            fig=px.bar(variance_frame,x='Fuel',y='Residual variance',color='Fuel',
                       custom_data=['N'],color_discrete_sequence=COLORS,
                       labels={'Residual variance':'Within-fuel OLS residual variance'})
            fig.update_traces(hovertemplate='%{x}<br>Residual variance=%{y:.6f}<br>Observations=%{customdata[0]}<extra></extra>')
            chart(fig,240)
            st.caption('The bars show unexplained model scatter, not physical flame oscillation or direct stability measurements.')
    elif focus=='Atmosphere coverage':
        plotted=full.dropna(subset=['oxygen','pressure'])
        if len(plotted):
            fig=px.scatter(plotted,x='oxygen',y='pressure',color='fuel',
                           hover_data=['record_id'],color_discrete_sequence=COLORS,
                           labels={'oxygen':'O₂ mole fraction','pressure':'Pressure (mmHg)'})
            fig.add_trace(go.Scatter(x=[EXPLORATION['oxygen']],
                    y=[psi_to_pressure(EXPLORATION['psi'])],mode='markers',
                    marker=dict(symbol='diamond',size=14,color='#A77B25'),
                    name='NASA reference point'))
            chart(fig,280)
            st.caption('The diamond marks a cited NASA atmosphere reference, not an experimental FLEX run or a certified safety boundary.')
    st.button('Investigate this finding →',key='home_spotlight_deep_dive',on_click=navigate_to,args=(target,))

    st.markdown('### Evidence at a glance')
    a,b,c,d=st.columns(4)
    with a:metric('Loaded FLEX records',f'{len(full):,}','original table, unmodified')
    with b:metric('Current filtered view',f'{len(view):,}','experiment filters applied')
    with c:metric('Complete rate pairs',f'{int(full.dropna(subset=["oxygen","burn"]).shape[0]):,}','O₂ and rate both recorded')
    with d:metric('NASA investigations',len(cat),'linked catalog, not raw rows')
    with st.expander('Explore the selected data distribution',expanded=False):
        l,r=st.columns(2)
        with l:
            title('Fuel distribution')
            counts=view.fuel.value_counts().rename_axis('Fuel').reset_index(name='Runs')
            if len(counts):chart(px.bar(counts,x='Fuel',y='Runs',color='Fuel',text='Runs',color_discrete_sequence=COLORS),275)
            else:st.info('No records match the current selection.')
        with r:
            title('Recorded test-end outcomes')
            counts=view.outcome.value_counts().rename_axis('Outcome').reset_index(name='Runs')
            if len(counts):chart(px.pie(counts,names='Outcome',values='Runs',hole=.57,color_discrete_sequence=COLORS),275)
        st.caption('The source file has oxygen, N, CO-labeled, and He composition columns. Verify the original CO label against NASA metadata before inferring chemical identity.')
        st.markdown('**Missing-data audit**')
        st.dataframe(completeness(raw).query('Missing > 0'),width='stretch',hide_index=True)
    with st.expander('Advanced · change the research finding rankings',expanded=False):
        st.caption('These sliders change the team’s editorial research-priority ranking, not a NASA risk score.')
        weights={}
        cols=st.columns(5)
        for col,key in zip(cols,['Support','Magnitude','Coverage','Reproducibility','Habitat relevance']):
            with col:weights[key]=st.slider(key,0,5,3 if key!='Habitat relevance' else 5,key='fw_'+key)
        items=rank_findings(findings(full),weights)
        st.dataframe(items[['Rank','Title','Class','Pillar','Evidence','Rank score / 100']],
                     width='stretch',hide_index=True,
                     column_config={'Rank score / 100':st.column_config.NumberColumn(format='%.1f')})
        pick=st.selectbox('Read the methodology and caveats',items['Title'].tolist())
        row=items[items.Title==pick].iloc[0]
        st.markdown(f'**{row["Class"]}:** {row["Evidence"]}')
        st.write('**Interpretation:**',row['Interpretation'])
        st.write('**Limits:**',row['Limits'])
        st.caption(f'Method: {row["Method"]}. Weighted score = 20 × Σ(weight × criterion) / Σ(weights). Editorial inputs, not objective hazards.')
    with st.expander('Source integrity · file fingerprint and cleaning record',expanded=False):
        st.dataframe(pd.DataFrame({'Mapped field':list(mapping),'Source column':[mapping[k] for k in mapping]}),hide_index=True)
        st.dataframe(audit,width='stretch',hide_index=True)
        st.code(f'SHA256: {source_hash}')
        st.caption(f'{len(full)} source rows are preserved. Sidebar filters alter only what is displayed. The dataset was supplied by the team and has not been independently authenticated against the NASA PSI export.')

elif page=='Investigation explorer':
    title('Investigation explorer','A sourced metadata catalog. Only FLEX experiment-level observations are loaded; unknown facts explicitly require PSI verification.')
    alert('Rankings indicate **team-assessed relevance for research discovery**, not a NASA rating or a quantitative fire-risk assessment. Sources link to original NASA pages.')
    col=st.columns(4)
    cw={}
    for c,key,label in zip(col,['applicability','atmosphere','measurement_utility','source_quality'],['Crew-material match','Atmosphere match','Diagnostic usefulness','Source completeness']):
        with c:cw[key]=st.slider(label,0,5,3,key='cw_'+key)
    st.caption('Edit the 0–5 assessment values below; research relevance score = weighted rubric / 5, scaled to 100. Scores are editorial, not experimental measurements.')
    rubric=cat[['investigation','applicability','atmosphere','measurement_utility','source_quality']].copy()
    edited=st.data_editor(rubric,hide_index=True,width='stretch',num_rows='fixed',disabled=['investigation'],key='catalog_editor',
        column_config={key:st.column_config.NumberColumn(key,min_value=0,max_value=5,step=1) for key in cw})
    ranking=cat.merge(edited,on='investigation',suffixes=('_old',''))
    ranking['Research relevance / 100']=sum(ranking[key]*weight for key,weight in cw.items())/(sum(cw.values()) or 1)*20
    ranking=ranking.sort_values('Research relevance / 100',ascending=False)
    s=st.text_input('Filter by investigation or objective',placeholder='e.g. smoke, droplets, Saffire, cool flames')
    pillar=st.selectbox('Fire-safety research pillar',['All','Prevention','Detection','Suppression'])
    shown=ranking.copy()
    if s:shown=shown[shown.investigation.str.contains(s,case=False,regex=False)|shown.objective.str.contains(s,case=False,regex=False)]
    if pillar!='All':shown=shown[shown.pillar==pillar]
    st.dataframe(shown[['investigation','pillar','objective','fuel_geometry','conditions','data_loaded','Research relevance / 100','source_url']],hide_index=True,width='stretch',
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
        st.dataframe(comparison,hide_index=True,width='stretch')
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
        st.dataframe(precision_frame(view,['record_id','identifier','fuel','oxygen','pressure','diameter','burn','burntime','outcome','co','helium']),hide_index=True,width='stretch')

elif page=='Fuel comparison lab':
    title('Fuel comparison lab','Recomputed directly from the complete-case subset. Previous team numbers are checked rather than assumed.')
    summary,residual,curves=fit_fuels(view)
    if len(summary):
        st.dataframe(summary,hide_index=True,width='stretch',column_config={'Slope':st.column_config.NumberColumn(format='%.5f'),'Residual variance':st.column_config.NumberColumn(format='%.6f')})
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
    st.dataframe(verified,hide_index=True,width='stretch')
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
    st.dataframe(pd.DataFrame(nums),hide_index=True,width='stretch')
    st.caption('Breusch–Pagan and White tests use the combined fuel×oxygen interaction model; fuel-specific residual tests use separate OLS fits.')
    alert('Four distinct concepts: measurement uncertainty (instrument precision, not supplied); model prediction uncertainty (requires validation); residual variation (fitted-model error); experimental variability (differences in repeated physical conditions). These are **not interchangeable**.','caution')
    title('Influence sensitivity','A second view omits Cook-flagged records for analysis only; the original CSV and default results are unchanged.')
    if len(view)>25:st.dataframe(sensitivity(view),hide_index=True,width='stretch')
    flags=audit_flags(view,res)
    title('Anomaly hunter',f'{len(flags)} flags across {flags.Record.nunique() if len(flags) else 0} distinct source records. Multiple reasons can flag the same record.')
    if len(flags):
        choice=st.selectbox('Inspect original flagged record',flags.Record.unique().tolist())
        st.dataframe(flags[flags.Record==choice],hide_index=True,width='stretch')
        record=view[view.record_id==choice]
        if len(record):
            st.markdown('**Original CSV values (verbatim):**')
            st.dataframe(raw.iloc[record.index],hide_index=True,width='stretch')
        with st.expander('See all flags'):st.dataframe(flags,hide_index=True,width='stretch')
    else:st.info('No flags under the current selection and rules.')

elif page=='Predictive intelligence':
    title('Predictive intelligence','Fitted models are exploratory research aids. Performance is measured out-of-fold, not on training predictions.')
    with st.spinner('Evaluating regression models across pressure groups…'):
        reg=model_a(full)
    title('Model A · Burning-rate regression')
    if 'error' in reg:st.warning(reg['error'])
    else:
        alert(f'Validation: {reg["method"]}. Complete-case model cohort N={len(reg["frame"])}. Raw records remain intact.')
        st.dataframe(reg['summary'],hide_index=True,width='stretch')
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
        with st.expander('Inspect pressure-fold performance'):st.dataframe(reg['folds'],hide_index=True,width='stretch')
    st.divider();title('Model B · Test-end outcome classifier')
    with st.spinner('Evaluating stratified out-of-fold classification…'):
        clf=model_b(full)
    if 'error' in clf:st.warning(clf['error'])
    else:
        a,b,c=st.columns(3)
        with a:st.metric('Macro-F1 (stratified CV)',f'{clf["macro_f1"]:.3f}')
        with b:st.metric('Multiclass Brier',f'{clf["brier"]:.3f}')
        with c:st.metric('Log loss',f'{clf["logloss"]:.3f}')
        st.dataframe(clf['metrics'],hide_index=True,width='stretch')
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
        st.dataframe(precision_frame(nearby['neighbors'],['record_id','fuel','oxygen','pressure','diameter','burn','outcome','normalized_distance']),hide_index=True,width='stretch')
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

elif page=='NASA data lab':
    title('NASA data lab · experimental evidence',
          'Bring authentic NASA PSI tables into the same research desk without blending incompatible experiments.')
    alert('**Scientific provenance:** The bundled 274-row FLEX CSV is team-supplied and preserved verbatim. Other NASA investigation tables are discoverable in NASA PSI, but **not bundled** in this build. Uploaded files remain marked as user-supplied until their source and checksum are independently checked.')
    coverage=source_coverage(st.session_state['psi_session_tables'])
    a,b,c=st.columns(3)
    with a:metric('PSI investigations indexed',len(coverage),'official NASA records')
    with b:metric('Session measurement tables',1+len(st.session_state['psi_session_tables']),'FLEX + optional CSV uploads')
    with c:metric('Cross-study pooled models',0,'studies have incompatible measurements')
    st.markdown('#### NASA source registry')
    st.dataframe(coverage[['study','id','family','doi','session_rows','coverage_note','nasa_source']],
                 hide_index=True,width='stretch',column_config={'nasa_source':st.column_config.LinkColumn('NASA PSI source')})
    st.download_button('Export source manifest',coverage.to_csv(index=False),
                       file_name='FlameX_NASA_source_manifest.csv',mime='text/csv')
    st.markdown('#### Import an official experimental table')
    st.caption('In the relevant NASA PSI investigation, open Data files and documents → Experimental table, and obtain its CSV. Upload here. The app keeps its original bytes and reports SHA-256. It does not assume that a file is an authentic NASA export merely because its name matches.')
    c1,c2=st.columns([1,2])
    with c1:study=st.selectbox('Source investigation',psi_catalog().query("study != 'FLEX'").study.tolist(),key='psi_study_choice')
    with c2:uploaded=st.file_uploader('Experimental table from NASA PSI (CSV)',type=['csv'],key='psi_table_upload')
    expected=psi_catalog().set_index('study').loc[study]
    st.caption(f'Expected NASA table filename: `{expected["file"]}` · Official record: {expected["nasa_source"]}')
    if uploaded and st.button('Import and audit original rows',type='primary'):
        try:
            item=read_psi_csv(uploaded.getvalue(),uploaded.name,study)
            st.session_state['psi_session_tables'][study]=item
            st.success(f'Imported {len(item.frame)} source rows for {study}. Recorded SHA-256: {item.sha256[:18]}…')
        except ValueError as e:st.error(str(e))
    if st.session_state['psi_session_tables']:
        st.markdown('#### Inspect uploaded measurement table')
        selected=st.selectbox('Loaded dataset',list(st.session_state['psi_session_tables']))
        current=st.session_state['psi_session_tables'][selected]
        st.caption(f'Original filename: `{current.filename}` · {len(current.frame)} rows × {len(current.frame.columns)} columns · SHA-256 `{current.sha256}` · NASA registry: {current.source_url}')
        st.dataframe(current.frame.head(200),hide_index=True,width='stretch')
        l,r=st.columns([1,1])
        with l:
            st.markdown('**Column validity audit**')
            audited=column_audit(current)
            st.dataframe(audited,hide_index=True,width='stretch')
            st.download_button('Download audit CSV',audited.to_csv(index=False),
                               file_name=f'{selected}_column_audit.csv',mime='text/csv')
        with r:
            chosen=st.selectbox('Inspect numerical field (original header)',current.frame.columns.tolist())
            inspected=measurement_view(current,chosen)
            exact=inspected[inspected.parse_status=='exact']
            metric('Exact numeric cells',len(exact),f'of {len(inspected)} source rows')
            st.caption('Approximate values (e.g., ~22.1) and ambiguous text are withheld from exact-number calculations. The original column name is retained; no cross-study units are assumed.')
            if len(exact)>1:
                fig=px.scatter(exact,x='source_row',y='value',hover_data=['original_value'],
                               title=f'{selected} · {chosen}',color_discrete_sequence=COLORS)
                chart(fig,320)
                st.write(f'Exact-cell median for this **native column only**: **{exact.value.median():.4g}** (reported source units, unverified).')
            st.dataframe(inspected.head(100),hide_index=True,width='stretch')
        st.download_button('Download unchanged uploaded CSV',current.raw_bytes,
                           file_name=current.filename,mime='text/csv')
        if st.button(f'Remove {selected} session upload'):
            del st.session_state['psi_session_tables'][selected];st.rerun()
    else:
        st.info('No additional NASA measurements have been imported in this session. The source registry remains useful, but descriptions are not substituted for numerical readings.')
    st.markdown('#### Why studies are not automatically pooled')
    st.write('FLEX measures liquid-droplet combustion, BASS-II studies solid-fuel behavior under airflow, Saffire tests larger spacecraft material fires, and SAME-R studies smoke aerosols. Their outcome variables, geometry, test conditions, and units differ. FlameX compares **what each dataset can answer** rather than treating unrelated values as one training set.')
    st.caption('This feature is a reproducible native-column audit, not a physical-hazard rating, fire experiment guide, or validated cross-study predictor.')

elif page=='FlameIQ research assistant':
    title('FlameIQ · scientific research assistant',
          'Ask about NASA combustion investigations, FLEX measurements, regression results, prediction limits, or what the evidence cannot prove.')
    st.markdown('''<div class="notice"><strong>No API key · No paywall · Reproducible answers.</strong> FlameIQ uses a deterministic question interpreter, calculated FLEX results and source-linked NASA investigation summaries. It is <strong>not</strong> a general-purpose generative chatbot, and it never invents missing measurements.</div>''',unsafe_allow_html=True)
    a,b,c=st.columns(3)
    with a:metric('NASA evidence entries',len(evidence_lib),'source-linked research summaries')
    with b:metric('Catalog investigations',len(cat),'raw measurements available only for FLEX')
    with c:metric('Selected FLEX records',len(view),'current research filter view')

    with st.expander('How FlameIQ reasons · transparent method',expanded=False):
        st.markdown('**1. Interpret the question.** An offline intent router recognizes regressions, counts, model performance, atmospheric references, source investigations and evidence gaps.\n\n'
                    '**2. Calculate or retrieve evidence.** Numerical findings are recomputed from the selected FLEX records using the analysis modules. Source-description questions retrieve linked NASA metadata.\n\n'
                    '**3. Disclose what is unknown.** It does not fabricate experiment-level records, confuse model scatter with flame stability, or certify a spacecraft fire-safety threshold.\n\n'
                    '**Scope:** Research Q&A and retrieval, not an autonomous language model. No hosted AI connection is required or attempted.')

    suggestions=[
        'What do the fuel regressions reveal, and what do they not prove?',
        'How different are methanol and heptane residual variances?',
        'How accurate are the models under pressure-group cross-validation?',
        'Why do FLEX, BASS-II and Saffire answer different questions?',
        'Can the experiments certify that a spacecraft atmosphere is safe?',
        'Which NASA investigations matter for crew-habitat research and why?',
    ]
    example=st.selectbox('Try a research question',['— Type my own question —']+suggestions,key='flameiq_example')
    if 'flameiq_chat' not in st.session_state:st.session_state['flameiq_chat']=[]
    if 'flameiq_audit' not in st.session_state:st.session_state['flameiq_audit']=None
    for role,msg in st.session_state['flameiq_chat']:
        with st.chat_message(role):st.markdown(msg)
    user_q=st.chat_input('Ask about experiments, model results, or evidence limits…')
    if st.button('Ask selected example',key='flameiq_ask_example') and example!='— Type my own question —':user_q=example
    if user_q:
        st.session_state['flameiq_chat'].append(('user',user_q))
        external=study_data_answer(user_q,st.session_state['psi_session_tables'])
        result=ask_research(user_q,view,cat)
        if external:
            rendered=external+'\n\n*This answer uses the supplementary NASA Data Lab session upload, which must be independently authenticated.*'
            audit_record={'route':'Supplementary uploaded data','basis':'Original uploaded CSV fields; see NASA Data Lab',
                          'rows':'Session CSV (see upload audit)','sources':[],'note':'Source not authenticated automatically'}
        else:
            rendered=result.text
            audit_record={'route':result.intent.replace('_',' ').title(),'basis':result.basis,
                          'rows':result.data_rows,'sources':list(result.sources),
                          'note':result.note or 'Computed findings use selected FLEX records'}
        st.session_state['flameiq_chat'].append(('assistant',rendered))
        st.session_state['flameiq_audit']=audit_record
        st.rerun()
    if st.session_state.get('flameiq_audit'):
        audit=st.session_state['flameiq_audit']
        with st.expander('Verify the last answer · method & provenance',expanded=False):
            st.markdown(f'**Question route:** {audit["route"]}  \n**Method:** {audit["basis"]}  \n**Research records considered:** {audit["rows"]}')
            if audit.get('note'):st.caption(audit['note'])
            for url in audit.get('sources',[]):
                st.markdown(f'- [Source / reference]({url})')
    if st.button('Clear conversation',key='flameiq_clear'):
        st.session_state['flameiq_chat']=[];st.session_state['flameiq_audit']=None;st.rerun()
    with st.expander('Browse the NASA evidence library and original references',expanded=False):
        st.caption('The entries are sourced research descriptions, not imported experimental observations for those investigations.')
        st.dataframe(evidence_lib[['evidence_id','investigation','topic','claim','source_url','raw_data_loaded']],
                     hide_index=True,width='stretch',
                     column_config={'source_url':st.column_config.LinkColumn('NASA source')})
        st.download_button('Download evidence library (.csv)',evidence_lib.to_csv(index=False),
                           file_name='FlameX_NASA_evidence_library.csv',mime='text/csv')
    st.caption('Independent research prototype · No automatic operational safety assessment · Team-supplied FLEX file provenance/units require NASA source verification.')

elif page=='Guided Tour':
    title('90-second guided tour',
          'A reproducible chain from NASA investigation → scientific question → model → evidence boundary.')
    alert('**Start here to explore FlameX:** The system ranks relevant NASA sources, executes numerical calculations only on data actually loaded, and prevents unsupported spacecraft safety claims.')
    a,b,c=st.columns(3)
    with a:metric('FLEX source records',len(full),'original data, SHA-audited')
    with b:metric('Evidence passages',len(evidence_lib),'NASA-linked statements')
    with c:metric('Research investigations',len(cat),'metadata, separately labeled')
    st.markdown('#### Follow the evidence in five steps')
    selected=st.radio('Choose a live demonstration question',range(len(STORY_QUESTIONS)),
                      format_func=lambda i:STORY_QUESTIONS[i][0],horizontal=True)
    question=STORY_QUESTIONS[selected][1]
    st.markdown(f'**Research question:** {question}')
    brief=evidence_brief(question,view,cat,st.session_state['psi_session_tables'])
    st.markdown(brief['answer'])
    with st.expander('Show the retrieval and claim-audit trail',expanded=True):
        st.caption(brief['method'])
        if brief['sources']:
            st.dataframe(pd.DataFrame(brief['sources']),hide_index=True,width='stretch',
                         column_config={'source':st.column_config.LinkColumn('NASA primary source')})
        else:st.info('This answer was derived from the loaded original FLEX table rather than a retrieved metadata excerpt.')
    st.markdown('#### Limits that build trust')
    for limitation in brief['boundary']:st.markdown('• '+limitation)
    st.markdown('#### What a judge should verify')
    st.write('Try a FLEX regression question, inspect the source and statistical assumptions, then ask for an unsupported habitat safety verdict. The refusal is an intentional guardrail, not a system failure. Finish in NASA data lab to review the complete audit trail and identify research gaps.')
    st.download_button('Export this source-audited research answer',
            '# FlameX judge evidence brief\n\n**Question:** '+question+'\n\n'+brief['answer']+'\n\n'+
            '\n'.join(f'- {r["id"]}: {r["source"]}' for r in brief['sources'])+'\n',
            file_name='FlameX_judge_evidence_brief.md',mime='text/markdown')

elif page=='Research brief & sources':
    title('Research brief & sources','Provenance, science boundaries and what can be claimed for the submission.')
    st.markdown('#### Research scope')
    alert('**Bundled:** One 274-row FLEX observation table. **In-session:** Original NASA PSI CSVs can additionally be uploaded and audited in NASA data lab, but they are not pooled with FLEX or authenticated automatically. All remaining investigation entries are metadata.')
    st.markdown('#### Three pillars of fire safety')
    a,b,c=st.columns(3)
    with a:st.markdown('**Prevention**\n\nHow combustion, flame spread and habitat materials depend on local conditions; other NASA investigations provide more directly relevant solid-fuel evidence.')
    with b:st.markdown('**Detection**\n\nSmoke and aerosol observations help frame questions for future detector research; not measurable from the loaded droplet CSV alone.')
    with c:st.markdown('**Suppression**\n\nFLEX addresses liquid droplet extinction and candidate inert-gas effects; the loaded CSV includes original CO-labeled and helium composition columns, not measured whole-habitat suppression efficacy.')
    st.markdown('#### Earth applications (context, not additional datasets)')
    st.write('The team-supplied challenge description mentions fine-water-mist extinguishing, smoke detection and firefighter equipment as related application themes. These applications are **not directly evaluated** by the loaded FLEX table.')
    st.markdown('#### NASA source-linked research evidence library')
    st.caption('Structured NASA metadata paraphrases for FLEX, BASS-II and Saffire; each claim links to a NASA source. Only FLEX raw measurements are loaded.')
    st.dataframe(evidence_lib[['evidence_id','investigation','topic','source_url']],hide_index=True,width='stretch', column_config={'source_url':st.column_config.LinkColumn('NASA source')})
    st.markdown('#### Original source and NASA investigation references')
    st.write(f'**Experimental source:** uploaded FLEX CSV. SHA256: `{source_hash}`')
    st.markdown(f'**Challenge page:** {CHALLENGE}')
    st.markdown('**FLEX PSI dataset:** https://psi.nasa.gov/physci/repo/data/investigations/PSI-69')
    st.markdown('**NASA investigations index:** https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/')
    st.dataframe(cat[['investigation','source_url','source_note','data_loaded']],hide_index=True,width='stretch',column_config={'source_url':st.column_config.LinkColumn('NASA source')})
    st.markdown('#### Verification and disclosure')
    st.write('Statistical tests and model results are generated at runtime from the original CSV. Catalog scores are user-adjustable editorial judgments. The project uses code and text produced with AI assistance; FlameIQ uses offline deterministic routing and source retrieval, not a hosted language model.')
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
