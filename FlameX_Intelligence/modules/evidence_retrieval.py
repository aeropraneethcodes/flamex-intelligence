"""Local semantic evidence retrieval over independently verified NASA summaries.

The library contains curated paraphrases of NASA investigation metadata,
not scraped articles, raw BASS-II/Saffire measurements, or experiment simulations.
The only observation-level table packaged by FlameX is FLEX.
"""
from functools import lru_cache
from pathlib import Path
import re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

LIBRARY = Path(__file__).resolve().parents[1]/'data'/'evidence_library.csv'
GROUPS = ('FLEX','BASS-II','Saffire-I','Saffire-II','Saffire-III')

@lru_cache(maxsize=1)
def load_evidence():
    frame=pd.read_csv(LIBRARY).fillna('')
    required={'evidence_id','investigation','claim','source_url','section','source_title','raw_data_loaded'}
    if not required.issubset(frame.columns):
        raise ValueError('Evidence library missing required provenance fields.')
    if frame.evidence_id.duplicated().any():
        raise ValueError('Evidence identifiers are not unique.')
    if not frame.source_url.str.startswith('https://').all():
        raise ValueError('Each evidence claim needs an authoritative source URL.')
    return frame

@lru_cache(maxsize=1)
def _index():
    evidence=load_evidence()
    texts=[f'{r.investigation} {r.topic} {r.claim} {r.search_terms}' for r in evidence.itertuples()]
    vectorizer=TfidfVectorizer(stop_words='english',ngram_range=(1,2),sublinear_tf=True)
    return vectorizer, vectorizer.fit_transform(texts)

def named_investigations(query):
    q=query.lower()
    hits=[]
    for name in ('Saffire-III','Saffire-II','Saffire-I','BASS-II','FLEX'):
        if re.search(r'(?<![\w])'+re.escape(name.lower())+r'(?![\w-])',q):
            hits.append(name)
    if 'saffire' in q and not any(n.startswith('Saffire') for n in hits):
        hits.extend(['Saffire-I','Saffire-II'])
    return hits

def retrieval(query, max_results=7, groups=None):
    """Rank passage paraphrases; return source rows plus reproducible relevance scores.

    No browser access, model-generated numbers, or external API key is needed.
    """
    ev=load_evidence()
    q=' '.join(str(query).split())
    if not q: return ev.iloc[0:0].copy()
    expanded=q
    if re.search(r'habitat|crew|spacecraft|lunar|moon|mars',q,re.I):
        expanded+=' materials fire prevention detection suppression airflow flammability'
    if re.search(r'detect|sensor|measure|camera|monitor',q,re.I):
        expanded+=' diagnostics cameras measurements imaging'
    if re.search(r'compare|difference|versus|vs\b',q,re.I):
        expanded+=' experiment objectives fuel geometry conditions'
    vec,matrix=_index()
    scores=cosine_similarity(vec.transform([expanded]),matrix).ravel()
    if groups:
        mask=ev.investigation.isin(groups).to_numpy()
        scores=np.where(mask,scores,-1)
    ev=ev.copy();ev['retrieval_score']=scores
    # Search results require actual topical similarity; no generic catchall fabricated.
    ev=ev[ev.retrieval_score>=0.055].sort_values(['retrieval_score','evidence_id'],ascending=[False,True])
    return ev.head(max_results).reset_index(drop=True)

def format_source(row):
    return f'[{row["evidence_id"]}]({row["source_url"]}) · {row["source_title"]}, {row["section"]}'

def evidence_comparison(question, catalog=None):
    """Grounded structured answer. No numerical claims beyond source metadata.

    An inference is explicitly labelled; each factual claim is accompanied by a
    NASA citation, and missing experiment-level data are disclosed.
    """
    q=question.lower().strip()
    requested=named_investigations(question)
    # Broad crew-habitat questions choose complementary research modes rather than
    # inventing a numerical winner. The order is an editorial example, not NASA rank.
    if not requested and re.search(r'habitat|crew|fire safety|material|spacecraft|investigation|research',q):
        requested=['BASS-II','Saffire-I','FLEX']
    elif not requested:
        return '**UNKNOWN · No retrieved evidence.** No supported research topic or investigation was identified in the local NASA evidence library.'
    requested=list(dict.fromkeys(requested))[:4]
    text=['**INFERRED · Evidence-backed research comparison**' if len(requested)>1 else '**OBSERVED (CATALOG METADATA · NASA SOURCE)**',
          'The following claims paraphrase linked NASA investigation descriptions. **Only the FLEX droplet CSV contains loaded experiment-level records.**']
    if re.search(r'measur|sensors?|camera|monitor|diagnostic',q):
        text.append('**Measurements / sensors (source descriptions; not imported experimental readings):**')
    source_lines=[]
    found=[]
    for name in requested:
        matches=retrieval(question,max_results=4,groups=[name])
        if matches.empty:
            # If question only names an investigation, ask for its core description.
            matches=retrieval(name+' objective measurements conditions',max_results=3,groups=[name])
        if matches.empty:
            text.append(f'**{name} — UNKNOWN:** No verified evidence passages matched this question. Consult the linked NASA catalog entry directly.')
            continue
        found.append(name)
        text.append(f'**{name} — NASA investigation metadata; raw data {"loaded for FLEX subset" if name=="FLEX" else "NOT loaded"}**')
        # Max two claims for a manageable mobile-readable answer.
        for _,r in matches.head(2).iterrows():
            text.append(f'- **OBSERVED · {r["topic"]}:** {r["claim"]} **[{r["evidence_id"]}]({r["source_url"]})**')
            source_lines.append((r['evidence_id'],format_source(r)))
    if len(found)>1:
        text.append('**INFERRED · Why these investigations complement each other:** ' +
                    'FLEX contributes droplet-scale extinction/suppression evidence; BASS-II addresses solid materials under varying airflow; '+
                    'Saffire addresses larger-scale material fire behavior. These investigate different fuels and conditions, so their results are **not directly interchangeable**. ' +
                    'This is a research-relevance comparison, **not a NASA ranking, hazard score, or measured effect-size comparison.**')
    text.append('**UNKNOWN · Evidence limits:** No raw BASS-II or Saffire measurements are loaded. Their observed numerical outcomes, equivalence to FLEX, and safe/unsafe thresholds cannot be determined here.')
    if source_lines:
        text.append('**NASA sources consulted:** '+ ' · '.join(s for _,s in dict(source_lines).items()))
    return '\n\n'.join(text)

def unsupported_numeric_question(question):
    """Detect attempted numeric claims for investigations without loaded raw datasets."""
    names=[x for x in named_investigations(question) if x!='FLEX']
    if not names:return []
    q=question.lower()
    requested_data=bool(re.search(r'\b(exact|raw|observed|experimental|measured|numeric(?:al)?|specific|actual)\b',q) and
                         re.search(r'\b(rate|rates|value|values|result|results|data|dataset|measurements?|numbers?|rows?|trials?)\b',q))
    requested_data |= bool(re.search(r'\b(predicted|prediction|mean|average|variance|p.value|regression|slopes?|precision|recall|significance|significant)\b',q))
    requested_data |= bool(re.search(r'\b(how many|count|total|number of)\b',q) and
                            re.search(r'\b(runs?|records?|experiments?|trials?|observations?|outcomes?|results?)\b',q))
    # NASA can report general experimental design sample count as metadata; this
    # only blocks unheld quantitative observations and statistical results.
    if requested_data:return names
    return []
