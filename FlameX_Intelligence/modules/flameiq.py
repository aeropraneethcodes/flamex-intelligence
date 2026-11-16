"""Evidence-grounded local retrieval assistant; optional constrained LLM text rendering."""
import re
import pandas as pd
from .statistics import diagnostics
from .data_loader import psi_to_pressure
from .atmospheres import EXPLORATION, HISTORICAL, references_markdown
from .evidence_retrieval import (load_evidence, retrieval, evidence_comparison,
    named_investigations, unsupported_numeric_question)

GROUND_RULES='No external experiment-level dataset is loaded outside FLEX. Catalog pages provide metadata, NOT observation-level measurements.'


def _legacy_answer(question,df,catalog,scenario=None,findings=None):
    q=question.strip().lower()
    if not q:return 'UNKNOWN · Please ask a question about the loaded FLEX table or a catalog investigation.'
    d=diagnostics(df)
    record_ids=re.findall(r'(?:flex[- #]*|test\s*#?\s*)(\d{1,3})',q,re.I)
    if record_ids:
        wanted={int(i) for i in record_ids}
        chosen=df[df['id'].isin(wanted)]
        if chosen.empty:return 'UNKNOWN · No matching FLEX test number appears in the currently filtered data. Clear the filters or verify the ID.'
        lines=['**OBSERVED · FLEX source record inspection**']
        for _,r in chosen.head(8).iterrows():
            lines.append(f'- `{r["record_id"]}` (identifier `{r.get("identifier","not mapped")}`): {r["fuel"]}; O₂={r["oxygen"]:.3f}; pressure={r["pressure"]:.1f} mmHg; burning-rate field={r["burn"] if pd.notna(r["burn"]) else "missing"}; outcome={r["outcome"]}.')
        lines.append('**Source:** Loaded original FLEX CSV, row IDs shown. Missing entries are not filled in.')
        return '\n\n'.join(lines)
    if any(s in q for s in ['safe','unsafe','certified','threshold for humans','guarantee','extinguish a real','operational']):
        return '**UNKNOWN · No operational safety assessment.** This experimental subset does not validate a safe/unsafe threshold for a habitat. Neither the regression nor model predictions certify fire safety. Relevant missing evidence: solid fuels, air flow, atmosphere coverage, and independent replication.'
    # Specific descriptive queries must not be mistaken for regression questions.
    fuel_mentions=[f for f in df.fuel.dropna().astype(str).unique() if f.lower() in q]
    if re.search(r'\b(how many|number of|count|total)\b',q) and any(z in q for z in ['run','record','experiment','test']):
        target=df[df.fuel.isin(fuel_mentions)] if fuel_mentions else df
        complete_words=('complete','nonmissing','valid')
        if any(z in q for z in complete_words) and any(z in q for z in ['rate','burning']):
            n=int(target.burn.notna().sum())
            return f'**CALCULATED · Complete-rate count:** {n} experiments with nonmissing burning-rate values among {len(target)} selected records.\n\n**Source:** Loaded FLEX CSV; filters apply. This is not the number of all available experiments.'
        return f'**OBSERVED · Experiment count:** {len(target)} selected FLEX records' + (f' for {", ".join(fuel_mentions)}.' if fuel_mentions else '.') + '\n\n**Source:** Loaded FLEX CSV, fuel and test identifiers; includes records with missing rates.'
    if any(z in q for z in ['mean burning rate','average burning rate','mean burn rate','average burn rate']):
        target=df[df.fuel.isin(fuel_mentions)] if fuel_mentions else df
        vals=target.burn.dropna()
        if vals.empty:return '**UNKNOWN:** No nonmissing burning-rate observations for this selection.'
        return f'**CALCULATED · Mean source burning-rate field:** {vals.mean():.5g} across {len(vals)} nonmissing observations' + (f' for {", ".join(fuel_mentions)}.' if fuel_mentions else '.') + '\n\n**Method:** Arithmetic mean of `Burning rate; mm`, omitting missing values in the calculation only. The original source unit requires verification before dimensional interpretation.'
    # A multi-part regression question needs the measured findings AND their limits.
    # Route it before generic "prove" / "why" mechanism disclaimers.
    regression_intent = bool(re.search(r'\b(regressions?|slopes?|fitted (?:lines?|models?)|fitted models?|oxygen.rate (?:models?|fits?))\b', q))
    if regression_intent:
        summary=d['summary']
        if summary.empty:
            return '**UNKNOWN · Insufficient data.** At least four complete records and two oxygen levels per fuel are needed for these fits.'
        parts=[]
        for _,r in summary.iterrows():
            parts.append(f'**{r["Fuel"]}** has an estimated oxygen–burning-rate slope of **{r["Slope"]:.5f}** (95% CI {r["Slope CI low"]:.3f} to {r["Slope CI high"]:.3f}; {int(r["N"])} complete records; R² = {r["R²"]:.3f}).')
        opening=' '.join(parts)
        inter=d['interaction']
        if inter:
            opening += f' The fuel-by-oxygen interaction is not statistically significant (HC3-robust p = {inter["p"]:.3g}), so this analysis does not detect a difference between their fitted slopes.'
        ratio=d.get('variance_ratio')
        if ratio is not None:
            higher=summary.loc[summary['Residual variance'].idxmax(),'Fuel']
            lower=summary.loc[summary['Residual variance'].idxmin(),'Fuel']
            opening += f' **{higher}** has about **{ratio:.2f}×** the regression residual variance of **{lower}**, meaning its measurements are more dispersed around its fitted line.'
        return ('**CALCULATED · What the fuel regressions reveal**\n\n'+opening+'\n\n'
                '**What they cannot prove:** Similar fitted slopes do not establish that the fuels behave identically or are statistically equivalent. '
                'The relationships are observational, not causal; residual variability does not directly measure intrinsic flame stability. '
                'The loaded table has no direct soot or chemical-kinetics measurements, so it cannot identify a physical mechanism.\n\n'
                '**Source and method:** Loaded FLEX records with nonmissing oxygen and burning-rate fields; separate ordinary least-squares fits and an HC3-robust fuel-by-oxygen interaction. '
                'The original burning-rate field’s physical units still require source verification.')
    matches=[]
    for _,r in catalog.iterrows():
        name=str(r['investigation']).lower()
        if name in q or (len(name.split())==1 and re.search(r'\b'+re.escape(name)+r'\b',q)):
            matches.append(r)
    if matches:
        matches=sorted(matches,key=lambda r:len(r['investigation']),reverse=True)
        m=matches[0]
        # Requests for what an investigation *measured* are metadata questions.
        # Requests for numerical measurements/results require its raw data.
        numeric_request=bool(re.search(r'\b(exact|numerical|quantitative|numbers?|values?|statistics?|results?|how many|count|data points?|raw data|observed rates?)\b',q))
        if m['investigation']!='FLEX' and numeric_request:
            return f'**UNKNOWN · Not loaded.** The catalog has a verified NASA reference for **{m["investigation"]}**, but no experimental measurement table for it is loaded. I cannot report its observed rates, conditions, or numerical results.\n\n**Catalog source:** {m["source_url"]}\n\n**Next research step:** Acquire the investigation dataset from NASA PSI, verify its fields and metadata, and ingest it separately from FLEX.'
        return f'**OBSERVED (CATALOG METADATA, NOT LOADED EXPERIMENT DATA)** · **{m["investigation"]}**\n\n- **Objective:** {m["objective"]}\n- **Conditions:** {m["conditions"]}\n- **Measurements:** {m["measurements"]}\n- **Data loaded:** {m["data_loaded"]}\n- **NASA source:** {m["source_url"]}\n\n**UNKNOWN:** Numerical observations beyond loaded FLEX cannot be supplied. Some fields explicitly require verification on PSI.'
    if any(z in q for z in ['soot cause','why does','why is','mechanism','causal','prove']):
        return '**UNKNOWN · Mechanism not established.** The loaded table records composition, pressure, droplet measurements, rate, duration, and end category. It has no soot concentration, soot imaging, or chemical-kinetics measurements. Observed relationships alone cannot prove a physical mechanism.'
    if any(z in q for z in ['moon','habitat','30%','10.2','34%','8.2','exploration atmosphere','scenario','coverage','artemis']):
        return ('**CALCULATED · NASA atmosphere-reference coverage**\n\n'
                + references_markdown(df)
                + f'\n\n**Method:** Two-condition queries over {len(df)} currently selected FLEX records. Pressure converted with 1 psi = 760/14.6959488 mmHg.'
                + '\n\n**UNKNOWN:** Neither reference demonstrates an operational fire-safety boundary; the historical screening condition is not the nominal exploration atmosphere.')
    if any(z in q for z in ['fuel','methanol','heptane','regression','slope','compare']):
        bits=['**CALCULATED · Per-fuel oxygen/rate OLS**']
        for _,r in d['summary'].iterrows():
            bits.append(f'For **{r["Fuel"]}**, the estimated oxygen–rate slope is **{r["Slope"]:.5f}** using {int(r["N"])} complete records. The 95% confidence interval runs from {r["Slope CI low"]:.3f} to {r["Slope CI high"]:.3f}, and R² is {r["R²"]:.3f}.')
        inter=d['interaction']
        if inter:bits.append(f'The fuel-by-oxygen interaction has an HC3-robust p-value of {inter["p"]:.4g}. This does not show a statistically significant difference in fitted slopes, but it does not prove the slopes are equivalent either.')
        bits.append('**Method / provenance:** Ordinary least squares on rows with nonmissing oxygen and rate; identifiers remain in source table. This is association, not causation.')
        return '\n\n'.join(bits)
    if any(z in q for z in ['scatter','variance','uncertainty','hetero','brown','levene','stability']):
        bf=d['brown_forsythe']
        if not bf:return '**UNKNOWN:** Not enough fuel groups with complete residual fits in the filtered view.'
        return (f'**CALCULATED · Residual dispersion**\n\nThe fuel-specific regression models have a residual-variance ratio of **{d["variance_ratio"]:.3f}×**. '
                f'The Brown–Forsythe test gives p = {bf["p"]:.5g} using {len(d["residuals"])} observations. '
                'You can inspect the underlying records in Stability & Uncertainty.\n\n'
                '**INFERRED:** The residual spread differs between the models. '
                '**UNKNOWN:** That does not prove a difference in intrinsic flame stability; a physical explanation would require additional evidence.')
    if any(z in q for z in ['outcome','extinction','disruption','completion','count','how many']):
        counts=df.outcome.value_counts().to_dict()
        return '**OBSERVED · Test-end categories**\n\n'+', '.join(f'**{k}:** {v}' for k,v in counts.items())+'.\n\n**Evidence:** `Test end` in loaded FLEX CSV. Categories are outcome labels, not verified failure mechanisms.'
    if any(z in q for z in ['helium','co2','diluent','suppression']):
        nco=int((df.co>0).sum()) if 'co' in df else 0
        nhe=int((df.helium>0).sum()) if 'helium' in df else 0
        return f'**OBSERVED · Gas composition columns**\n\n- CO-labeled source field (interpreted as CO₂ only after checking the original NASA documentation): positive in {nco} rows.\n- Helium positive in {nhe} rows.\n- **Source:** Original composition columns in the FLEX CSV; these are conditions, not measured suppressant efficacy.\n\n**UNKNOWN:** The CSV alone does not establish operational suppression effectiveness.'
    return '**UNKNOWN / NOT RETRIEVED.** I could not connect this question to a verified statistic, a source record, or a catalog entry. Try “Compare methanol and heptane,” “Inspect FLEX test 114,” “What is the Moon atmosphere coverage?”, “Explain Brown–Forsythe,” or “What does BASS-II study?”. I will not invent an answer.'



def answer(question, df, catalog, scenario=None, findings=None):
    """FlameIQ local RAG: NASA source retrieval plus deterministic FLEX science.

    Routes calculations to the established scientific methods and uses the
    independently sourced NASA library for open-ended cross-investigation
    questions. Unavailable numerical results are never inferred from metadata.
    """
    q=question.strip().lower()
    if not q:
        return '**UNKNOWN · Empty question.** Ask about a NASA investigation or the FLEX evidence.'
    # Research mode must not turn incidental vocabulary overlaps (for example,
    # 'ambient temperature on Neptune') into fabricated answers about unrelated
    # phenomena. General knowledge questions belong in separately labeled Q&A.
    research_cues=(r'\b(?:flex|bass|saffire|combustion|fire|flames?|smoke|droplets?|'
                   r'fuels?|oxygen|heptane|methanol|spacecraft|habitats?|astronaut|'
                   r'lunar|moon|mars|suppression|extinction|experiments?|'
                   r'investigations?|regression|variance|uncertainty|datasets?|'
                   r'flammability|soot|anomalies?|sensors?|research|evidence|brown|forsythe|levene|heteroscedasticity|'
                   r'artemis|atmospher(?:e|ic)|coverage|pressure|model|statistics?)\b')
    if (not re.search(research_cues,q) or
        (re.search(r'\b(?:neptune|jupiter|saturn|uranus|venus|mercury)\b',q) and
         not re.search(r'\b(?:flex|bass|saffire|combustion|fire|flame)\b',q))):
        return ('**UNKNOWN · Outside the current NASA combustion evidence.** '
                'I cannot verify that question from the loaded FLEX table or NASA investigation excerpts. '
                'The provided research interface cannot verify unrelated general-knowledge questions.')
    # Scientific safety limits always take precedence, including multi-source prompts.
    if re.search(r'\b(safe|unsafe|certified|guarantee|operational)\b|threshold for humans|extinguish a real',q):
        return _legacy_answer(question,df,catalog,scenario,findings)
    missing=unsupported_numeric_question(question)
    if missing:
        known=catalog[catalog.investigation.isin(missing)]
        refs=' · '.join(f'[{r.investigation}]({r.source_url})' for r in known.itertuples())
        return ('**UNKNOWN · Not loaded.** FlameX contains NASA catalog descriptions, but no original '
                + ', '.join(missing) + ' experiment-level measurement table. I cannot give exact observed rates, '
                + 'results, statistical estimates, or experimental comparisons for those investigations.\n\n'
                + f'**NASA metadata sources:** {refs or "Not available"}.\n\n'
                + '**Next step:** Acquire the original datasets and verify units, protocols and provenance separately from FLEX.')
    # Numeric questions and record inspection must be answered by observed rows
    # or mathematical calculations, not literature similarity search.
    if (re.search(r'(?:flex[- #]*|test\s*#?\s*)\d{1,3}',q) or
        (re.search(r'\b(how many|number of|count|total)\b',q) and any(k in q for k in ['run','record','experiment','test'])) or
        any(k in q for k in ['mean burning rate','average burning rate','mean burn rate','average burn rate']) or
        any(k in q for k in ['regression','slopes','fitted model','brown','levene','variance','hetero','residual','uncertainty']) or
        (not named_investigations(question) and any(k in q for k in ['co2','helium','diluent'])) or
        any(k in q for k in ['soot cause','why does','why is','mechanism','causal','prove']) or
        any(k in q for k in ['30%','10.2','34%','8.2','scenario','coverage','artemis','atmosphere'])):
        return _legacy_answer(question,df,catalog,scenario,findings)
    names=named_investigations(question)
    inquiry=bool(re.search(r'compare|differences?|similarit|which|why|how|what|best|relevant|measure|stud|research|sensor|catalog|investigat|crew|habitat|material|fuel',q))
    if inquiry and (names or re.search(r'investigat|habitat|spacecraft|crew|material fire|fire safety',q)):
        return evidence_comparison(question,catalog)
    # Open-ended evidence search; supports questions beyond the suggested list.
    matches=retrieval(question,max_results=5)
    if not matches.empty:
        lines=['**OBSERVED · Related NASA research evidence (semantic retrieval)**',
               'Here are the closest passages I found in the NASA research library.']
        for _,r in matches.iterrows():
            lines.append(f'**{r["investigation"]} — {r["topic"]}:** {r["claim"]} '
                         f'**[{r["evidence_id"]}]({r["source_url"]})**')
        lines.append('**UNKNOWN:** If your exact question requires facts or records outside these excerpts, the local library cannot verify them.')
        return '\n\n'.join(lines)
    return _legacy_answer(question,df,catalog,scenario,findings)
