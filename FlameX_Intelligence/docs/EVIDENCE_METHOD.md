# FlameIQ: evidence method and scope

## Input provenance

- Real observations: `data/flame_intelligence_master.csv` (274 rows, 15 original fields).
- Catalog: `data/investigations.csv` (21 NASA-linked investigation entries; only FLEX source data loaded).
- Evidence layer: `data/evidence_library.csv` (22 independently assembled, paraphrased NASA investigation descriptions).

Every evidence row has `evidence_id`, `investigation`, `section`, `topic`, `claim`, `source_title`, `source_url`, `evidence_class`, `raw_data_loaded`, and `search_terms`. These are descriptive metadata and research objectives, **not raw BASS-II or Saffire measurements**.

## Retrieval method

1. The question is tokenized with scikit-learn TF-IDF using English stopword removal and unigram/bigram features.
2. A fixed, documented query-expansion rule expands habitat, diagnostics, and comparison queries.
3. Cosine similarity ranks the curated NASA paraphrases. Named investigations constrain retrieval to their own evidence entries.
4. A deterministic formatting layer shows each selected claim with its original NASA URL and an `OBSERVED` label meaning **a sourced description**, not a value observed in a loaded experiment.
5. Multi-investigation comparisons are always marked **INFERRED**, because NASA descriptions do not supply a common numerical metric for comparison. The user-adjustable catalog rankings are separate editorial scores.
6. Questions requesting actual BASS-II/Saffire measurements, statistical estimates, or operational safe/unsafe verdicts return **UNKNOWN**.
7. FLEX statistics and individual record questions are routed through existing reproducible Pandas/Statsmodels tools, not TF-IDF.

## Source audit: official NASA

| Investigation | Source | Link |
|---|---|---|
| FLEX | NASA PSI-69 | https://psi.nasa.gov/physci/repo/data/investigations/PSI-69 |
| BASS-II | NASA PSI-25 | https://psi.nasa.gov/physci/repo/data/investigations/PSI-25 |
| Saffire-I | NASA PSI-98 | https://psi.nasa.gov/physci/repo/data/investigations/PSI-98 |
| Saffire-II & III | NASA Saffire press release | https://www.nasa.gov/news-release/nasa-prepares-to-ignite-third-saffire-experiment/ |
| FLEX cross-investigation context | NASA ISS combustion overview | https://www.nasa.gov/missions/station/studying-combustion-and-fire-safety/ |

The evidence texts are independently written concise paraphrases, not copies of NASA articles. They have not been audited or endorsed by NASA. The source does not establish an inter-investigation ranking or directly comparable measured outcomes.

## Demonstration of a meaningful refusal

Question: **Give exact Saffire-II burning-rate values.**
Expected: `UNKNOWN · Not loaded`; source catalog metadata is cited, but no experimental measurements are invented.

## What this upgrade does not do

- It does not fetch or parse all NASA publications live.
- It does not create or load new observation-level records for BASS-II or Saffire.
- It does not guarantee good retrieval for arbitrary prompts outside the curated NASA evidence library.
- It does not validate any habitat fire-safety threshold.
- An optional LLM (if configured) is only permitted to paraphrase already-retrieved evidence and is disabled by default.
