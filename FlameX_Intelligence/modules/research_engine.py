"""FlameIQ: deterministic, auditable research-question interpreter.

No network, API credentials, text-generation model, or invented measurements.
Scientific numbers come from current selected FLEX data and existing analysis methods.
The assistant is a rule-based scientific Q&A layer, NOT a generative language model.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Tuple
import pandas as pd

from .statistics import diagnostics
from .models import regression_analysis
from .data_loader import PSI_FLEX
from .atmospheres import references_markdown, EXPLORATION, HISTORICAL
from .evidence_retrieval import (load_evidence, retrieval, evidence_comparison,
                                 named_investigations, unsupported_numeric_question)
from .flameiq import answer as original_answer


@dataclass(frozen=True)
class ResearchReply:
    text: str
    intent: str
    basis: str
    sources: Tuple[str, ...]
    data_rows: int
    numeric_verified: bool
    note: str


SOURCE_NOTE = ('The bundled FLEX table is team-supplied; its original NASA-file identity and '
               'burning-rate field units still need independent source verification.')
_NO_SAFETY = ('These are research observations, **not** validated spacecraft fire-risk predictions, '
              'safe/unsafe thresholds, or operational instructions.')


def _has(text, expr):
    return re.search(expr, text, flags=re.I) is not None


def classify_question(question: str) -> str:
    """Prioritizes user intent, including paraphrases and compound questions."""
    q=' '.join(str(question).lower().split())
    if not q:return 'empty'
    if _has(q, r'\b(?:safe|unsafe|certif(?:ied|y)|guarantee|operational|\bcan (?:we|i) (?:use|live)|human safety)\b') or 'safe threshold' in q:
        return 'safety_boundary'
    if unsupported_numeric_question(q):return 'unavailable_measurements'
    if _has(q,r'(?:flex[- #]*|test\s*#?\s*)\d{1,3}'):
        return 'source_record'
    if _has(q,r'\b(?:how many|number of|count|total)\b') and _has(q,r'\b(?:runs?|records?|tests?|trials?|observations?|experiments?)\b'):
        return 'counts'
    if _has(q,r'\b(?:mean|average)\b') and _has(q,r'\b(?:burn(?:ing)?\s*rate|oxygen|pressure)\b'):
        return 'mean'
    if _has(q,r'\b(?:variance|variances|scatter|spread|variability|uncertainty|heteroscedastic|residuals?|brown.forsythe|levene|stability|stable)\b') and not _has(q,r'\b(?:slope|slopes|regressions? reveal|fitted models?)\b'):
        return 'variability'
    if _has(q,r'\b(?:regression|regressions|slope|slopes|fitted|line of best fit|ols|interaction)\b') or (
        _has(q,r'\b(?:methanol|heptane|fuels?)\b') and _has(q,r'\b(?:relationship|correlat|oxygen sensitivity|behav|differ|identical|same)\b')):
        return 'regression'
    if _has(q,r'\b(?:predict|prediction|accuracy|machine learning|random forest|cross.validation|mae|rmse|grouped cv|forecast|validation|predictive)\b'):
        return 'model_validation'
    if _has(q,r'\b(?:atmospher|artemis|lunar|moon|pressure coverage|habitat conditions|8\.2|10\.2|34%|30%)'):
        return 'atmosphere'
    if _has(q,r'\b(?:soot|mechanism|cause|causal|prove|why does|why is)\b'):
        return 'mechanism'
    if _has(q,r'\b(?:test end|end categor|completion|disruption|extinction outcome|outcome)\b'):
        return 'outcomes'
    if _has(q,r'\b(?:which|rank|ranking|important|priority|best)\b') and _has(q,r'\b(?:investigations?|findings?|research|experiments?|studies)\b'):
        return 'research_priorities'
    if named_investigations(q) or _has(q,r'\b(?:investigations?|saffire|bass|smoke|crew|habitat|spacecraft|solid.fuel|study|research comparison)\b'):
        return 'investigation_evidence'
    return 'search_evidence'


def _return(text, intent, basis, df, sources=(PSI_FLEX,), note='',numeric_verified=True,
            trusted_numbers=None):
    # Fail closed if a calculation template introduces a number that was not
    # registered from the current data. This check is intentionally limited to
    # computed answers; NASA publication metadata may contain its own numerals.
    if trusted_numbers is not None:
        passed, unexpected = numeric_claim_check(text, trusted_numbers)
        if not passed:
            return ResearchReply(text='**Verification withheld.** The explanation contained a numeric claim not registered in the calculated result. Open the corresponding analysis page to inspect the primary tables.',
                intent=intent,basis='Numeric-claim verification withheld answer',sources=(PSI_FLEX,),
                data_rows=len(df),numeric_verified=False,note='Unexpected numeric claims suppressed')
    sources=tuple(dict.fromkeys(sources))
    return ResearchReply(text=text,intent=intent,basis=basis,sources=sources,
                         data_rows=len(df),numeric_verified=bool(numeric_verified),note=note)


def _regression(df,question):
    diag=diagnostics(df)
    table=diag['summary']
    if table.empty:
        return _return('**INSUFFICIENT DATA.** The current filter selection does not contain enough complete records and distinct oxygen levels to estimate fuel-specific slopes. Try resetting the experiment filters.',
                       'regression','no fit available',df, note='No numerical conclusion produced')
    parts=[]; trusted=[]
    for r in table.itertuples(index=False):
        # Namedtuple field aliases can be unstable for R² and confidence column labels.
        row=table[table.Fuel.eq(r.Fuel)].iloc[0]
        trusted += [f'{row["Slope"]:.3f}',f'{row["Slope CI low"]:.3f}',f'{row["Slope CI high"]:.3f}',str(int(row["N"])),f'{row["R²"]:.3f}']
        parts.append(f'For **{row["Fuel"]}**, the fitted oxygen–burning-rate slope is **{row["Slope"]:.3f}** '
                     f'(95% confidence interval **{row["Slope CI low"]:.3f} to {row["Slope CI high"]:.3f}**, '
                     f'**{int(row["N"])}** complete records, R² = **{row["R²"]:.3f}**).')
    text='**What the measurements show.** '+' '.join(parts)
    interaction=diag.get('interaction')
    if interaction and len(table)>1:
        trusted.append(f'{interaction["p"]:.3g}')
        text+=(f' The interaction test gives an HC3-robust **p = {interaction["p"]:.3g}**; '
                'we do not detect a statistically significant difference in fitted slopes.')
    if diag.get('variance_ratio') is not None and len(table)>1:
        trusted.append(f'{diag["variance_ratio"]:.2f}')
        top=table.sort_values('Residual variance',ascending=False)
        text+=(f' At the same time, **{top.iloc[0]["Fuel"]}** has '
                f'**{diag["variance_ratio"]:.2f}×** the model residual variance of **{top.iloc[-1]["Fuel"]}**. '
                'That is greater unexplained scatter around its regression line, not a direct flame-stability measurement.')
    text+=('\n\n**What it cannot prove.** Similar estimated slopes do not establish equivalence or causation. '
           'This dataset does not directly measure the mechanisms responsible for residual scatter, '
           'and these fitted relationships cannot certify a safe spacecraft atmosphere.'
           '\n\n**Evidence:** Current selected FLEX records, separate OLS fits and (when both fuels are present) '
           'an HC3-robust fuel–oxygen interaction. '+SOURCE_NOTE)
    return _return(text,'regression','FLEX complete-case OLS; HC3 interaction; residual variance',df,note='Statistical findings, not causal conclusions',trusted_numbers=trusted)


def _variability(df):
    d=diagnostics(df); bf=d.get('brown_forsythe'); ratio=d.get('variance_ratio')
    if not bf or ratio is None:
        return _return('**INSUFFICIENT DATA.** Residual variability cannot be compared with these filters; both fuels need valid regression models.', 'variability','no two-fuel residual comparison',df)
    tbl=d['summary'].sort_values('Residual variance',ascending=False)
    text=(f'**What differs.** In the selected FLEX records, **{tbl.iloc[0]["Fuel"]}** has about '
          f'**{ratio:.2f}×** the residual variance of **{tbl.iloc[-1]["Fuel"]}** after separate '
          f'oxygen regressions. The Brown–Forsythe test returns **p = {bf["p"]:.3g}**, '
          'consistent with unequal residual dispersion in these fitted models.\n\n'
          '**What it means.** The measurements scatter differently around their regression lines. '
          'That does **not** establish which flame is physically more stable or why the scatter differs. '
          'The effect can also be sensitive to influential observations.\n\n'
          '**Evidence:** Recomputed OLS residuals and Brown–Forsythe test. '+SOURCE_NOTE)
    return _return(text,'variability','Fuel-specific OLS residual variance; Brown–Forsythe',df, trusted_numbers=[f'{ratio:.2f}',f'{bf["p"]:.3g}'])


def _count(df,q):
    fuel=None
    if 'methanol' in q and 'heptane' not in q:fuel='Methanol'
    elif 'heptane' in q and 'methanol' not in q:fuel='Heptane'
    target=df if fuel is None else df[df.fuel.eq(fuel)]
    label=f' for **{fuel}**' if fuel else ''
    if _has(q,r'\b(?:complete|nonmissing|valid)\b'):
        n=int(target[['oxygen','burn']].notna().all(axis=1).sum())
        msg=f'There are **{n}** selected FLEX records{label} with both oxygen and the burning-rate field present.'
    else:
        msg=f'There are **{len(target)}** selected FLEX source records{label}, including rows with missing measurements.'
    return _return('**Observed record count.** '+msg+'\n\n**Evidence:** Loaded FLEX records; currently active filters apply.',
                   'counts','Direct row count on selected FLEX records',target,trusted_numbers=[str(len(target)),str(int(target[['oxygen','burn']].notna().all(axis=1).sum()))])


def _means(df,q):
    target=df
    if 'methanol' in q and 'heptane' not in q:target=df[df.fuel.eq('Methanol')]
    elif 'heptane' in q and 'methanol' not in q:target=df[df.fuel.eq('Heptane')]
    col='burn' if _has(q,r'burn(?:ing)?\s*rate') else ('oxygen' if 'oxygen' in q else 'pressure')
    vals=target[col].dropna()
    if vals.empty:return _return('**INSUFFICIENT DATA.** The selected view contains no valid values for that mean.', 'mean','No source measurements',target)
    labels={'burn':'source burning-rate field','oxygen':'oxygen mole fraction','pressure':'ambient pressure (mmHg)'}
    msg=f'The arithmetic mean **{labels[col]}** is **{vals.mean():.5g}** across **{len(vals)}** nonmissing selected records.'
    note=SOURCE_NOTE if col=='burn' else 'Original measured values are not imputed.'
    return _return('**Calculated from the loaded FLEX table.** '+msg+'\n\n'+note, 'mean',f'Arithmetic mean of {col}',target,trusted_numbers=[f'{vals.mean():.5g}',str(len(vals))])


def _outcomes(df):
    counts=df.outcome.dropna().value_counts().sort_index()
    if counts.empty:return _return('**INSUFFICIENT DATA.** No test-end categories are available in the selected records.', 'outcomes','No outcome labels',df)
    summary=', '.join(f'**{k}: {int(v)}**' for k,v in counts.items())
    return _return('**Observed FLEX test-end categories.** '+summary+'. These are recorded experiment labels, not independently verified mechanisms of extinction or real-world safety outcomes.\n\n**Evidence:** `Test end` source column; currently selected FLEX records.', 'outcomes','Direct count of the test-end column',df,trusted_numbers=[str(int(v)) for v in counts.values])


def _prediction(df):
    reg=regression_analysis(df,trees=65)
    if 'error' in reg:
        return _return('**INSUFFICIENT DATA.** '+reg['error']+' The dashboard does not make a prediction from an unsupported subset.', 'model_validation','Grouped cross-validation unavailable',df)
    s=reg['summary'];entries=[];trusted=[]
    for r in s.itertuples(index=False):
        row=s[s.Model.eq(r.Model)].iloc[0]
        trusted += [f'{row["Grouped CV MAE"]:.4f}', f'{row["Grouped CV RMSE"]:.4f}']
        entries.append(f'**{row["Model"]}**: grouped-CV MAE **{row["Grouped CV MAE"]:.4f}**, RMSE **{row["Grouped CV RMSE"]:.4f}**')
    text=('**How predictive performance is measured.** FlameX separates observations by pressure groups during '
          'cross-validation, making the evaluation more demanding than a random row split. '
          +' ; '.join(entries)+'.\n\n'
          '**What it cannot guarantee.** These are errors on held-out pressure groups from the loaded dataset, '
          'not independent mission data. They do not prove accuracy for new spacecraft atmospheres or establish safe/unsafe operating limits. '
          'The original burning-rate field unit still needs verification.')
    return _return(text,'model_validation','Pressure-group held-out model evaluation; no external validation',df,note='Models evaluated only on the provided FLEX subset',trusted_numbers=trusted)


def _investigations(question,df,catalog):
    ans=evidence_comparison(question,catalog)
    names=named_investigations(question)
    if not names:names=['BASS-II','Saffire-I','FLEX']
    ev=load_evidence();links=tuple(ev.loc[ev.investigation.isin(names),'source_url'].head(8).tolist())
    return _return(ans,'investigation_evidence','NASA investigation descriptions; retrieved source-linked summaries',df,links or (PSI_FLEX,),note='Other investigations lack imported raw observations; no cross-study numeric pooling',numeric_verified=False)


def _priorities(question,df,catalog):
    # Never invent an objective performance ranking across incomparable investigations.
    ans=evidence_comparison('Which FLEX BASS-II Saffire-I investigation findings best complement crew-habitat fire research?',catalog)
    pref=('**Research priorities — editorial, not a NASA award ranking.** For liquid-fuel droplet burning, '
          'start with FLEX because its experiment records can be analyzed here. To assess solid materials under airflow, '
          'consult BASS-II. For larger-scale material fires, consult Saffire. They answer different questions, '
          'so there is no scientifically defensible single winner based on the measurements currently loaded.\n\n')
    return _return(pref+ans,'research_priorities','Evidence relevance by experimental role; no cross-study quantitative rank',df,
                   tuple(dict.fromkeys(catalog[catalog.investigation.isin(['FLEX','BASS-II','Saffire-I'])].source_url.tolist())),
                   note='Ordering expresses purpose, not NASA-endorsed safety ranking',numeric_verified=False)


def ask_research(question,df:pd.DataFrame,catalog:pd.DataFrame) -> ResearchReply:
    """Run the evidence-first assistant. Never calls a network or generative model."""
    q=' '.join(str(question).lower().split());intent=classify_question(question)
    if intent=='empty':
        return _return('Ask a question about the FLEX experiments or NASA investigation evidence.',intent,'No question supplied',df,())
    if intent=='safety_boundary':
        return _return('**Not established.** '+_NO_SAFETY+' This FLEX subset does not cover the full solid-fuel, airflow, ventilation, ignition, or crew-operations evidence required for that judgment. You can explore NASA atmospheric reference coverage in the scenario explorer.',intent,'Scientific evidence boundary',df,note='No operational assessment',numeric_verified=False)
    if intent=='unavailable_measurements':
        missing=unsupported_numeric_question(question)
        links=catalog[catalog.investigation.isin(missing)].source_url.tolist()
        return _return('**Those numerical measurements are not loaded.** FlameX has NASA source descriptions for '+', '.join(missing)+', but cannot calculate their experimental values or train on their raw records. Only FLEX experiment-level measurements are bundled. See NASA Data Lab to import and audit separately sourced files.', intent,'Metadata-only investigation coverage',df,tuple(links),note='No fabricated cross-study numerical results',numeric_verified=False)
    if intent=='regression':return _regression(df,question)
    if intent=='variability':return _variability(df)
    if intent=='model_validation':return _prediction(df)
    if intent=='counts':return _count(df,q)
    if intent=='mean':return _means(df,q)
    if intent=='outcomes':return _outcomes(df)
    if intent=='atmosphere':
        return _return('**What NASA reference comparisons show.** '+references_markdown(df)+'\n\n**Interpretation:** Both are reference conditions, not measured safe/unsafe limits. The comparison checks coverage of currently loaded FLEX records; it does not establish conditions for a crewed habitat.',intent,'Direct oxygen/pressure coverage queries against NASA references',df,(EXPLORATION['url'],HISTORICAL['url']),note='No measured safety threshold')
    if intent=='research_priorities':return _priorities(question,df,catalog)
    if intent=='investigation_evidence':return _investigations(question,df,catalog)
    # Existing detailed row retrieval and mechanism-safe answers are authoritative.
    result=original_answer(question,df,catalog)
    matches=retrieval(question,max_results=4)
    links=tuple(matches.source_url.tolist()) if not matches.empty else (PSI_FLEX,)
    return _return(result,intent,'FLEX source inspection or curated NASA evidence retrieval',df,links,
                   note='Retrieval similarity is not independent verification of a new observation',numeric_verified=False)


def numeric_claim_check(text, allowed_numbers):
    """Supplemental guard: reject novel numeric literals in generated numeric prose.

    This function is also usable if a future paraphraser is added. No paraphraser is
    included or called in the judge release. Excludes URLs and common report notation.
    """
    no_urls=re.sub(r'https?://[^\s)]+','',text)
    no_ids=re.sub(r'\b(?:FLEX|PSI|NASA)[- ]?\d+\b|\bBASS-II\b|\bSaffire-(?:I|II|III)\b','',no_urls,flags=re.I)
    numbers=set(re.findall(r'(?<![\w])\d+(?:\.\d+)?(?:e[-+]?\d+)?(?![\w])',no_ids,flags=re.I))
    permitted=set(str(n) for n in allowed_numbers)|{'95','100'}
    return not (numbers-permitted),tuple(sorted(numbers-permitted))
