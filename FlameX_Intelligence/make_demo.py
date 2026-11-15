"""Rebuild the original seven-slide FlameX demonstration from the authentic FLEX table.

Optional slide-build dependencies: python-pptx, matplotlib, pandas, numpy,
scipy, statsmodels, scikit-learn. No NASA logos or third-party imagery used.
Run from the project root: python make_demo.py
For PDF, export PPTX using PowerPoint or LibreOffice.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.dml import MSO_THEME_COLOR
from pptx.enum.text import MSO_AUTO_SIZE
from modules.data_loader import read_raw,normalized_view,pressure_to_psi,psi_to_pressure
from modules.statistics import diagnostics,fit_fuels
from modules.models import regression_analysis
from modules.atmospheres import EXPLORATION,HISTORICAL,reference_count

BASE=Path(__file__).resolve().parent
ASSET=BASE/'docs'/'assets';ASSET.mkdir(parents=True,exist_ok=True)
OUT=BASE/'docs'/'FlameX_Demo_7_Slides.pptx'
raw,_=read_raw(BASE/'data'/'flame_intelligence_master.csv')
df,_=normalized_view(raw)
stat=diagnostics(df); fit,residual,curves=fit_fuels(df)
reg=regression_analysis(df)
N=RGBColor(23,50,77);B=RGBColor(36,112,152);TEAL=RGBColor(39,127,146);ORANGE=RGBColor(188,99,83)
MUTED=RGBColor(99,117,136);TEXT=RGBColor(36,55,71);PALE=RGBColor(246,249,251)
LINE=RGBColor(222,230,236); WHITE=RGBColor(255,255,255);YELLOW=RGBColor(187,141,63)
C_BLUE='#276F9E';C_RED='#B9655A'; C_GRAY='#667788'

# --- reproducible plot assets ---
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.labelcolor':'#263748','xtick.color':'#6B7885','ytick.color':'#6B7885','axes.edgecolor':'#DDE5EB','axes.spines.top':False,'axes.spines.right':False,'grid.color':'#E7EDF1','grid.alpha':.85})

f,ax=plt.subplots(figsize=(8.1,4.1),dpi=180)
for label,col in [('Methanol',C_BLUE),('Heptane',C_RED)]:
    q=df[(df.fuel==label)&df.burn.notna()]
    ax.scatter(q.oxygen,q.burn,s=16,alpha=.64,color=col,label=f'{label} observations',edgecolor='white',linewidth=.15)
    c=curves[label]
    ax.plot(c.oxygen,c.fit,color=col,lw=2,label=f'{label} OLS')
    ax.fill_between(c.oxygen,c.lo,c.hi,color=col,alpha=.13,lw=0)
ax.set(xlabel='Initial oxygen mole fraction',ylabel='Source burning-rate field (unit not confirmed)')
ax.grid(axis='y');ax.legend(frameon=False,ncol=2,loc='upper left',fontsize=8)
f.tight_layout(pad=1.15)
f.savefig(ASSET/'final_oxygen_fit.png',facecolor='white',bbox_inches='tight');plt.close(f)

f,ax=plt.subplots(figsize=(6.8,4.1),dpi=180)
rs=[]; labels=[]
for fuel in ['Methanol','Heptane']:
    q=residual[residual.fuel==fuel];rs.append(q.residual.values);labels.append(f'{fuel}\nN={len(q)}')
bp=ax.boxplot(rs,tick_labels=labels,patch_artist=True,widths=.5,showfliers=True,medianprops={'color':'#253D53','linewidth':1.8},boxprops={'edgecolor':'#DEE6EC'},whiskerprops={'color':'#8795A1'},capprops={'color':'#8795A1'},flierprops={'marker':'.','markersize':4,'markerfacecolor':'#B76860','markeredgecolor':'#B76860','alpha':.5})
for box,col in zip(bp['boxes'],[C_BLUE,C_RED]):box.set_facecolor(col);box.set_alpha(.22)
ax.axhline(0,color='#8795A1',lw=1,ls='--')
ax.set_ylabel('Residual (source burning-rate field)');ax.grid(axis='y');f.tight_layout(pad=1.15)
f.savefig(ASSET/'final_residuals.png',facecolor='white',bbox_inches='tight');plt.close(f)

f,ax=plt.subplots(figsize=(7.2,4.2),dpi=180)
for fuel,col in [('Methanol',C_BLUE),('Heptane',C_RED)]:
    q=df[df.fuel==fuel]
    ax.scatter(q.oxygen*100,q.pressure.map(pressure_to_psi),s=14,alpha=.55,color=col,label=f'{fuel} records',edgecolor='white',linewidth=.1)
ax.scatter([34],[8.2],s=100,color='#B78F4E',marker='D',edgecolors='white',lw=1.2,zorder=5,label='NASA exploration reference')
ax.scatter([30],[10.2],s=110,color='#334B61',marker='s',edgecolors='white',lw=1.2,zorder=5,label='Historical materials test')
ax.annotate('34% O₂ / 8.2 psia',xy=(34,8.2),xytext=(25,3),color='#865F28',fontsize=9,arrowprops={'arrowstyle':'-','color':'#B78F4E'})
ax.annotate('30% O₂ / 10.2 psia',xy=(30,10.2),xytext=(25,16),color='#334B61',fontsize=9,arrowprops={'arrowstyle':'-','color':'#334B61'})
ax.set_xlim(10.5,38);ax.set_ylim(-.2,48)
ax.set(xlabel='Initial oxygen (%)',ylabel='Ambient pressure (psia)')
ax.grid(axis='y');ax.legend(frameon=False,ncol=2,loc='upper left',fontsize=8)
f.tight_layout(pad=1.0)
f.savefig(ASSET/'final_atmosphere.png',facecolor='white',bbox_inches='tight');plt.close(f)

# --- presentation primitives ---
prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5)
blank=prs.slide_layouts[6]

def shape(s,kind,x,y,w,h,fill,outline=None,radius=False):
    sh=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb=fill
    if outline:
        sh.line.color.rgb=outline;sh.line.width=Pt(.8)
    else:sh.line.fill.background()
    if radius:
        try:sh.adjustments[0]=.09
        except Exception:pass
    return sh

def txt(s,text,x,y,w,h,size=16,color=TEXT,bold=False,align='left',font='Aptos',marg=.02,spacing=1.1):
    tb=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    tf=tb.text_frame;tf.word_wrap=True
    tf.margin_left=tf.margin_right=Inches(marg);tf.margin_top=tf.margin_bottom=Inches(marg)
    tf.vertical_anchor=MSO_ANCHOR.MIDDLE
    for j,line in enumerate(str(text).split('\n')):
        p=tf.paragraphs[0] if j==0 else tf.add_paragraph()
        p.text=line;p.font.name=font;p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=color
        p.alignment={'left':PP_ALIGN.LEFT,'center':PP_ALIGN.CENTER,'right':PP_ALIGN.RIGHT}[align]
        p.space_after=Pt(0);p.line_spacing=1.12
    return tb

def new_slide(k,topic=None,headline=None,desc=None):
    s=prs.slides.add_slide(blank)
    s.background.fill.solid();s.background.fill.fore_color.rgb=PALE
    shape(s,'rect',0,0,13.333,.09,B)
    txt(s,'DYNAMIC DUO   /   FLAMEX INTELLIGENCE',.62,.24,9,.23,10,B,True)
    if topic:txt(s,topic.upper(),.65,.78,11,.26,11,TEAL,True)
    if headline:txt(s,headline,.65,1.12,12.1,.6,30,N,True,font='Aptos Display')
    if desc:txt(s,desc,.66,1.79,11.7,.52,14,MUTED)
    shape(s,'rect',.63,7.12,12.06,.012,LINE)
    txt(s,'INDEPENDENT RESEARCH PROTOTYPE  ·  NOT NASA-ENDORSED',.64,7.18,10,.18,8,MUTED)
    txt(s,f'{k} / 7',12.1,7.16,.53,.2,8,MUTED,align='right')
    return s

def card(s,x,y,w,h,title,body,tag=None,accent=B):
    shape(s,'rect',x,y,w,h,WHITE,LINE,True)
    shape(s,'rect',x+.02,y+.10,.055,h-.20,accent)
    if tag:txt(s,tag.upper(),x+.27,y+.20,w-.52,.21,9,accent,True)
    txt(s,title,x+.27,y+.52,w-.53,.39,18,N,True)
    txt(s,body,x+.27,y+1.01,w-.52,h-1.18,12,TEXT)

def pill(s,text,x,y,w,fg=B,bg=None,size=10):
    bg=bg or RGBColor(233,242,247)
    shape(s,'rect',x,y,w,.36,bg,None,True)
    txt(s,text,x+.08,y+.04,w-.16,.27,size,fg,True)

# SLIDE 1
s=new_slide(1)
shape(s,'rect',.64,1.24,7.85,4.6,WHITE,LINE,True)
txt(s,'EVIDENCE-GROUNDED SCIENTIFIC INTELLIGENCE',.94,1.52,6.9,.32,11,TEAL,True)
txt(s,'FlameX\nIntelligence',.94,1.98,7.4,1.54,44,N,True,font='Aptos Display')
txt(s,'Find the right investigation.\nRead the actual evidence. Know the limits.',.96,3.75,6.75,1.05,21,TEXT)
pill(s,'2026 NASA SPACE APPS',.96,5.02,2.22)
# bespoke vector visual, no NASA logos or photographs
shape(s,'rect',8.80,1.24,3.87,4.6,RGBColor(235,242,246),None,True)
for i in range(7):
    shape(s,'rect',9.25+(i%3)*.93,2.02+(i//3)*.91,.7,.66,RGBColor(255,255,255),LINE,True)
for x,y,col in [(9.61,2.34,B),(10.54,3.25,TEAL),(11.48,2.34,ORANGE),(11.48,4.17,B),(9.61,4.17,TEAL)]:
    oval=s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x-.115), Inches(y-.115), Inches(.23), Inches(.23));oval.fill.solid();oval.fill.fore_color.rgb=col;oval.line.fill.background()
txt(s,'SOURCE → RELEVANCE → REASONING',9.10,5.12,3.18,.35,12,N,True,align='center')
for i,(big,small) in enumerate([('21','NASA-linked entries'),('274','FLEX records'),('22','Source-linked notes')]):
    x=.68+i*4.07
    txt(s,big,x,6.15,1.05,.47,27,N,True)
    txt(s,small,x+1.07,6.29,2.85,.25,11,MUTED)

# SLIDE 2
s=new_slide(2,'Challenge alignment','Summarize → rank → interpret','NASA Space Apps asks for an interactive SI-powered research dashboard, not an unsupported safety verdict.')
card(s,.68,2.50,3.88,3.47,'Investigations','Source-linked objectives, fuels, apparatus, sensors and availability.','01   SUMMARIZE',B)
card(s,4.72,2.50,3.88,3.47,'Research relevance','User-adjustable criteria reveal why a study is worth examining first.','02   RANK',TEAL)
card(s,8.76,2.50,3.88,3.47,'Evidence and limits','Observed FLEX records, rigorous uncertainty checks and explicit missing data.','03   INTERPRET',ORANGE)
shape(s,'rect',.70,6.24,11.95,.51,RGBColor(233,243,248),None,True)
txt(s,'CORE RULE: metadata ≠ measurements   ·   correlation ≠ causation   ·   model output ≠ safety certification',.91,6.35,11.3,.21,11,N,True,align='center')

# SLIDE 3
s=new_slide(3,'Investigation explorer','Find relevant research before running a model','A 21-investigation NASA-linked index; scores are editable team assessments, not NASA ratings.')
# rank table
shape(s,'rect',.67,2.45,7.42,3.78,WHITE,LINE,True)
txt(s,'EXAMPLE RANKING — DEFAULT EQUAL WEIGHTS',.91,2.71,6.88,.27,11,TEAL,True)
items=[('01','BASS-II','100','Solid-fuel / airflow'),('02','Saffire-I','100','Larger-scale material fire'),('03','SAME-R','95','Smoke / detection'),('04','FLEX','90','Liquid-droplet extinction')]
for i,(number,name,score,desc) in enumerate(items):
    yy=3.12+i*.66
    if i%2==0:shape(s,'rect',.90,yy,6.95,.59,RGBColor(246,249,251),None,True)
    txt(s,number,1.08,yy+.13,.38,.25,10,MUTED,True)
    txt(s,name,1.53,yy+.09,1.85,.32,15,N,True)
    txt(s,desc,3.51,yy+.15,2.85,.23,10,MUTED)
    txt(s,score,7.02,yy+.10,.57,.3,15,B,True,align='right')
shape(s,'rect',8.35,2.45,4.28,3.78,WHITE,LINE,True)
txt(s,'THE EDITABLE RUBRIC',8.67,2.73,3.55,.30,11,TEAL,True)
for i,x in enumerate(['Crew-material match','Atmosphere match','Diagnostic usefulness','Source completeness']):
    txt(s,x,8.69,3.22+i*.55,3.05,.25,12,TEXT)
    pill(s,'3 / 5',11.57,3.17+i*.55,.75,size=9)
txt(s,'Score = 20 × weighted average (0–5).\nSource metadata only for all but FLEX.',8.68,5.58,3.68,.53,10,MUTED)
txt(s,'NASA sources: PSI-25 (BASS-II)  ·  PSI-98 (Saffire-I)  ·  PSI-69 (FLEX)',.77,6.48,11.85,.25,10,MUTED)

# SLIDE 4
s=new_slide(4,'Combustion explorer','A real FLEX table, with an auditable analysis','274 original runs · 15 columns · 258 complete oxygen/rate pairs · no deleted or synthetic records')
shape(s,'rect',.67,2.42,8.34,4.17,WHITE,LINE,True)
s.shapes.add_picture(str(ASSET/'final_oxygen_fit.png'), Inches(.94), Inches(2.60),width=Inches(7.78))
shape(s,'rect',9.22,2.42,3.4,4.17,WHITE,LINE,True)
txt(s,'FUEL-SPECIFIC OLS',9.49,2.71,2.88,.25,10,TEAL,True)
txt(s,'Methanol',9.48,3.17,2.9,.28,14,N,True)
txt(s,'N = 151   ·   slope = 1.5048',9.48,3.54,2.87,.36,13,B)
txt(s,'Heptane',9.48,4.17,2.9,.28,14,N,True)
txt(s,'N = 107   ·   slope = 1.5231',9.48,4.54,2.87,.36,13,ORANGE)
shape(s,'rect',9.44,5.17,2.88,.95,RGBColor(249,244,233),None,True)
txt(s,'The CSV literally labels this variable “Burning rate; mm”. Dimensional meaning requires metadata verification.',9.59,5.31,2.58,.66,9,TEXT)
txt(s,'Data: team-supplied FLEX master table · NASA PSI-69. Shaded regions are 95% confidence intervals for the fitted mean.',.75,6.74,11.92,.22,9,MUTED)

# SLIDE 5
s=new_slide(5,'Scientific uncertainty','The result is a difference in residual scatter','Model diagnostics constrain interpretation; they do not establish a mechanism or direct flame-stability measurement.')
shape(s,'rect',.67,2.42,6.07,4.18,WHITE,LINE,True)
s.shapes.add_picture(str(ASSET/'final_residuals.png'),Inches(.88),Inches(2.57),width=Inches(5.65))
shape(s,'rect',6.97,2.42,5.66,4.18,WHITE,LINE,True)
txt(s,'3.3657×',7.28,2.74,2.48,.60,29,N,True)
txt(s,'Ratio of fitted OLS residual sample variances',7.29,3.35,4.94,.43,12,TEXT)
shape(s,'rect',7.23,3.95,5.03,.014,LINE)
txt(s,'p = 1.47 × 10⁻⁵',7.28,4.16,4.70,.44,22,B,True)
txt(s,'Brown–Forsythe · unequal residual dispersion',7.29,4.64,4.9,.32,12,TEXT)
shape(s,'rect',7.23,5.12,5.03,.014,LINE)
txt(s,'p = 0.960',7.29,5.36,4.4,.35,20,ORANGE,True)
txt(s,'Fuel × oxygen interaction: no detected slope difference is not proof of equivalence.',7.29,5.76,4.89,.51,11,TEXT)
txt(s,'Further caution: pressure-grouped regression CV is exploratory; outcome classifier probabilities are withheld after failing the reliability gate.',.76,6.75,11.8,.22,9,MUTED)

# SLIDE 6
s=new_slide(6,'Scenario explorer','Make missing evidence visible—not a safety score','NASA reference conditions are distinct points; neither defines an experimentally validated safety envelope.')
shape(s,'rect',.67,2.42,8.0,4.18,WHITE,LINE,True)
s.shapes.add_picture(str(ASSET/'final_atmosphere.png'),Inches(1.05),Inches(2.49),width=Inches(7.00))
shape(s,'rect',8.88,2.42,3.74,4.18,WHITE,LINE,True)
txt(s,'NASA EXPLORATION REFERENCE',9.13,2.72,3.19,.26,10,TEAL,True)
txt(s,'34% O₂ / 8.2 psia',9.13,3.05,3.17,.44,17,N,True)
txt(s,'HISTORICAL MATERIAL TEST',9.13,3.78,3.16,.26,10,TEAL,True)
txt(s,'30% O₂ / 10.2 psia',9.13,4.12,3.21,.44,17,N,True)
shape(s,'rect',9.13,4.92,3.17,1.21,RGBColor(249,244,233),None,True)
txt(s,'0 / 274',9.32,5.08,2.58,.43,24,ORANGE,True)
txt(s,'FLEX records satisfy either broad reference-based coverage query.',9.32,5.55,2.65,.40,10,TEXT)
txt(s,'The scatter is plotted from the original FLEX table. Reference sources: NASA NTRS 20240003211 and 19880003147. No prediction or safe/unsafe verdict is inferred.',.75,6.72,11.91,.28,9,MUTED)

# SLIDE 7
s=new_slide(7,'FlameIQ + final impact','Ask freely. Cite evidence. Refuse unsupported results.','Offline scientific retrieval works with no API key; optional hosted and local language models are clearly labeled.')
shape(s,'rect',.67,2.40,6.05,3.66,WHITE,LINE,True)
txt(s,'SOURCE-BACKED QUESTION',.96,2.75,5.35,.26,10,TEAL,True)
txt(s,'“Which studies help with crew-habitat material fire research?”',.96,3.15,5.33,.69,17,N,True)
txt(s,'BASS-II → solid fuels and forced airflow (NASA PSI-25)\nSaffire-I → larger-scale material behavior (NASA PSI-98)\nFLEX → droplet extinction, but different geometry (NASA PSI-69)',.96,4.09,5.34,1.37,12,TEXT)
shape(s,'rect',6.91,2.40,5.71,3.66,WHITE,LINE,True)
txt(s,'UNSUPPORTED-NUMBER REFUSAL',7.18,2.75,5.11,.26,10,ORANGE,True)
txt(s,'“Give exact Saffire-II burning-rate measurements.”',7.18,3.15,5.0,.67,17,N,True)
shape(s,'rect',7.18,4.09,4.98,1.34,RGBColor(249,244,233),None,True)
txt(s,'UNKNOWN: Saffire-II numerical records are not loaded. Source descriptions are not experimental measurements.',7.35,4.28,4.62,.83,13,TEXT)
txt(s,'NEXT: source metadata verification · additional PSI datasets · independent prediction validation',.78,6.32,11.56,.33,12,B,True)
txt(s,'AI assistance disclosed · Live site and GitHub links should be added to the NASA submission after deployment.',.78,6.75,11.59,.21,9,MUTED)

assert len(prs.slides)==7
prs.save(str(OUT))
print('Wrote',OUT,'slides',len(prs.slides))
print('Asset files:',*[str(ASSET/x) for x in ['final_oxygen_fit.png','final_residuals.png','final_atmosphere.png']])
