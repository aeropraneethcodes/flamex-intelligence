# FlameX Intelligence — Competition Release · Verified FlameIQ Research Engine

**Dynamic Duo · NASA Space Apps Challenge 2026 · Flame in Freefall**

FlameX is a light, scientific research dashboard for exploring NASA microgravity combustion investigations, checking what each experiment can actually support, and explaining evidence and uncertainty without inventing missing measurements. It is an **independent research prototype**, not NASA software or an operational fire-safety system.

## Homepage and navigation (polished edition)

- The **home hero** now introduces the science with a large highlighted, underlined message using the existing off-white and scientific-blue palette. It does not suggest that the visualizations are physical flame simulations.
- **Four top-of-page shortcuts** link to Overview, the combustion data, FlameIQ, and the Guided Tour. All eleven research pages are still available in the sidebar with recognizable icons.
- **Three homepage research pathways** take a visitor directly to the measurements, research assistant, or judging walkthrough.
- **Interactive research spotlight:** switch between fuel-model residual variability, NASA atmosphere reference coverage, and evidence/uncertainty boundaries. Numerical spotlight claims recalculate from the source table; each has a direct deep-dive button.
- **Advanced controls are expandable.** Sidebar experiment filters, CSV upload, and source-column mappings are not in the way of the judge-facing walkthrough. A Reset button restores unfiltered data views. Ranking sliders, chart breakdowns, and source digest remain available from labeled homepage expanders.
- **The 11 existing research pages, statistical calculations, bundled CSV, source manifest, and seven-slide demo are preserved.** The homepage is a clearer entrance to the existing science, not a replacement for the analysis.

**Important:** Navigation controls were tested in code and all pages were exercised using a mocked Streamlit runner; the app has not been browser-tested on the live deployment. Test clickable navigation and the filter reset in the live Streamlit Cloud app after upgrading.

## Launch

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the terminal **inside the folder containing `app.py` and `requirements.txt`**. Windows users can also double-click `START_FLAMEX.bat` after extracting the ZIP. On Streamlit Community Cloud, use the correct entrypoint for where you put the folder: `FlameX_Intelligence/app.py` in your current repository. See `docs/DEPLOY_THIS_VERSION.md` for step-by-step instructions. This release uses no hosted-model credentials.

**No credentials, API credits, or hosted language model are needed or used.** FlameIQ is a transparent, deterministic scientific question-routing and evidence-retrieval assistant. It computes FLEX numerical answers with tested research functions; it is **not** a generative chatbot. The predictive learning models live in Predictive Intelligence and are evaluated using cross-validation. A numeric-claim guard checks computed response templates against registered results.

## What's new in the competition release

- **11 dashboard pages**: Mission overview; Investigation explorer; Combustion explorer; Fuel comparison lab; Stability & uncertainty; Predictive intelligence; Artemis scenario explorer; NASA data lab; FlameIQ research assistant; Guided Tour; Research brief & sources.
- **NASA data lab**: A 7-investigation official PSI source registry, including stable NASA investigation links and verified DOIs where available. It ingests additional *user-provided* NASA PSI experimental-table CSVs, preserves the original byte content, creates SHA-256 fingerprints, audits numeric parsing and qualifiers, and plots individual native measurement columns without pooling unrelated experiments.
- **A judge-demo path**: Five evidence questions, with reproducible source retrieval trails and explicit limits on interpretation.
- **Scientific intelligence**: The no-key evidence engine performs question interpretation, traceable source retrieval, verified numerical calculations, and transparent uncertainty reporting. The system also contains cross-validated predictive machine-learning models, with validation limits shown. Neither the evidence engine nor TF-IDF search is described as generative AI.
- **New 7-slide presentation**, matching PDF and stand-alone evidence/judging brief.
- **73 automated checks passed and 11/11 simulated Streamlit page checks** at build time. These are not a substitute for a live deployed-browser check.

## Scientific data: what is and isn't included

| Source | Included today | What's supported |
|---|---|---|
| FLEX / NASA PSI-69 | **274 team-provided original CSV rows** | Numerical plots, two fuel regressions, statistical diagnostics, exploratory modeling |
| BASS-II / PSI-25 | Official source registry, metadata; **no original raw table bundled** | Catalog comparison; experimental-table analysis after CSV upload |
| Saffire-I/II/III / PSI-98/99/100 | Source registry, metadata; **no original raw tables bundled** | Catalog comparison; native-column exploration after upload |
| SAME / SAME-R / PSI-102/101 | Source registry, metadata; **no original raw tables bundled** | Detection research context; native-column exploration after upload |

**Why not bundle more source tables?** NASA PSI investigation pages were verified, but their raw file downloads could not be fetched in this build environment. It would undermine the project to invent or backfill measurement rows. The new Data Lab gives the team a transparent import and audit path for original exports from NASA PSI, with no need to edit Python code. Uploaded files are labeled **not independently authenticated** until externally checked.

**Don't combine numeric readings from these investigations into one model without a justified common outcome/units/schema.** Liquid-droplet burning, solid-fuel spread, spacecraft-scale fire growth, and smoke aerosols answer different scientific questions.

### Verified bundled FLEX calculations

- Raw file: **274 rows, 15 columns**, 258 complete oxygen/burning-rate pairs. Original SHA-256 begins `ae7a2190f624af26`.
- Methanol: n=151, oxygen/rate OLS slope ≈ **1.504754**.
- Heptane: n=107, oxygen/rate OLS slope ≈ **1.523092**.
- Residual variance ratio (Heptane/Methanol) ≈ **3.365717**; Brown–Forsythe p ≈ **1.46519 × 10⁻⁵**.
- These are observations and statistics **about model residuals**, not a measured physical stability index, causal mechanism, or habitat fire-safety threshold. The exact physical unit for source column `Burning rate; mm` requires an original NASA data dictionary check.
- The NASA exploration-atmosphere reference of **8.2 psia, 34% O₂** and the distinct historical materials-test reference of **10.2 psia, 30% O₂** are not interchangeable. Neither two-condition diagnostic query has matching bundled FLEX observations. Zero coverage is a lack of evidence, not evidence of safety or danger.

## Demonstration and submission

1. Open **Guided Tour**: answer a NASA investigation question, reveal the supporting sources.
2. Open **Fuel comparison lab**: recompute the regression and inspect what it cannot prove.
3. Open **FlameIQ research assistant**: ask for an unsupported real-world safety verdict and observe the transparent limitation.
4. Open **NASA data lab**: inspect the source registry and verifiable input pipeline for additional NASA tables.

See `docs/JUDGE_DEMO.md`, `docs/SUBMISSION_COPY.md`, and the PowerPoint/PDF under `docs/`.

## Verified NASA starting points

- Competition brief: https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/
- NASA Physical Sciences Informatics (PSI): https://psi.nasa.gov/physci/repo
- FLEX: https://psi.nasa.gov/physci/repo/data/investigations/PSI-69 — DOI 10.60555/mbq8-0451
- BASS-II: https://psi.nasa.gov/physci/repo/data/investigations/PSI-25 — DOI 10.60555/4qc4-de67
- Saffire-I: https://psi.nasa.gov/physci/repo/data/investigations/PSI-98 — DOI 10.60555/0t15-1z43
- Saffire-II: https://psi.nasa.gov/physci/repo/data/investigations/PSI-99
- SAME-R: https://psi.nasa.gov/physci/repo/data/investigations/PSI-101 — DOI 10.60555/2np7-jv14

### Reproducibility

```bash
python -m pytest -q tests
PYTHONPATH=. python tests/mock_streamlit_smoke.py
```

The code and slide text were developed with AI assistance. All numerical findings use the user-provided file and the included analysis code; AI-generated wording is not represented as independently verified experimental evidence. No NASA endorsement is implied.
