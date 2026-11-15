"""Auditable, no-key scientific reasoning briefs built from retrieved NASA evidence.

Each statement is linked to a NASA source or is explicitly labeled calculation/inference.
"""
from .evidence_retrieval import retrieval
from .flameiq import answer

STORY_QUESTIONS = [
 ('01 · FIND', 'What investigations address spacecraft fire safety?'),
 ('02 · COMPARE', 'How do FLEX, BASS-II, and Saffire-I investigate different fire behaviors?'),
 ('03 · CALCULATE', 'What do the fuel regressions reveal and what can they not prove?'),
 ('04 · CHECK COVERAGE', 'Compare the NASA habitat atmosphere reference points and dataset coverage.'),
 ('05 · SHOW THE LIMIT', 'Can these data certify that a lunar habitat is safe?'),
]


def evidence_brief(question, flex, catalog, imported=None):
    """Return a reproducible answer, evidence citations and boundary note; never fabricate rows."""
    imported=imported or {}
    response=answer(question,flex,catalog)
    hits=retrieval(question,max_results=5)
    records=[{'id':str(r.evidence_id),'investigation':str(r.investigation),
              'claim':str(r.claim),'source':str(r.source_url),'score':round(float(r.retrieval_score),3)}
              for r in hits.itertuples(index=False)]
    unknown=[]
    if imported:
        unknown.append('Uploaded investigation files are displayed and audited in the NASA Data Lab, but are not yet incorporated into FLEX regression or the source-based FlameIQ science model.')
    else:
        unknown.append('Other NASA investigation raw tables are not bundled. Their source summaries are not numerical observations.')
    unknown.append('Statistical associations do not establish causal mechanisms, material qualification, or habitat fire-safety limits.')
    return {'question':question,'answer':response,'sources':records,'boundary':unknown,
            'method':'Deterministic analysis of FLEX + TF-IDF search over a curated NASA-linked source library (no hosted LLM required).'}
