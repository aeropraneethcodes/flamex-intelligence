# Sources and credit — FlameX Intelligence

**Always cite these original sources in the Space Apps submission.** This independent project does not claim NASA affiliation or endorsement.

## Challenge and dataset

- Official challenge: https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/
- NASA PSI FLEX investigation, PSI-69: https://psi.nasa.gov/physci/repo/data/investigations/PSI-69 (NASA PSI record; CC0-1.0 indicated in published investigation metadata)
- NASA PSI investigation index: https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/
- FLEX source CSV in `data/flame_intelligence_master.csv`: supplied by Team Dynamic Duo; 274 observations, 15 original columns. **The app contains this subset, not the whole PSI investigation archive.**

## Cross-investigation evidence

- NASA PSI BASS-II, PSI-25: https://psi.nasa.gov/physci/repo/data/investigations/PSI-25
- NASA PSI Saffire-I, PSI-98: https://psi.nasa.gov/physci/repo/data/investigations/PSI-98
- NASA Saffire-II/III mission article: https://www.nasa.gov/news-release/nasa-prepares-to-ignite-third-saffire-experiment/
- Individual source links for all 21 catalog entries are in `data/investigations.csv`.
- Individual source links and evidence IDs for all 22 curated source summaries are in `data/evidence_library.csv`.

## Atmosphere reference documents

- NASA Moon to Mars: Exploration Atmosphere (NTRS 20240003211): https://ntrs.nasa.gov/citations/20240003211 — 8.2 psia/34% O2 was an exploration-atmosphere reference; mission-specific atmosphere requirements may differ.
- Spacecraft material flammability testing and configurations (NASA NTRS 19880003147): https://ntrs.nasa.gov/citations/19880003147 — 10.2 psia/30% O2 as a historical materials test condition.

**Do not infer that either reference condition is a tested flammability boundary, operational cabin safety determination, or a NASA-endorsed safe band.** The program's zero-count coverage queries are diagnostic comparisons only.

## Technology acknowledgements

Streamlit, Python, pandas, NumPy, SciPy, statsmodels, scikit-learn, Plotly, plus optional OpenAI SDK and optional Ollama (only when independently configured). Consult the `requirements.txt` and `requirements-optional-ai.txt` files for software requirements. Original project branding and charts; no official NASA logos.

## AI assistance disclosure

Software code, portions of written content, QA tests, scientific explanation and presentation assembly were prepared with **OpenAI ChatGPT assistance** and checked against the original FLEX source table and linked NASA documentation. FlameIQ offline mode performs local retrieval and deterministic calculations, **not unrestricted LLM reasoning**. Its optional OpenAI or Ollama mode generates language-model responses using retrieved evidence. Any externally generated answer is fallible and must be verified; it is not a NASA scientific judgment. No synthetic observations are presented as NASA measurements.
