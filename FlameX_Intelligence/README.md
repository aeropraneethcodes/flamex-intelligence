# FlameX Intelligence

**Team Dynamic Duo · NASA Space Apps Challenge 2026 · Independent project (not NASA-affiliated)**

> The evidence-grounded fire-safety research desk: find the right investigation, see what its data actually supports, and know what it cannot tell you.

## Start in Windows (fastest)

1. **Extract** the final `FlameX_Intelligence_Final_2026.zip` using Windows **Extract All**. Do not run anything inside the ZIP without extracting it.
2. Open the nested `FlameX_Intelligence` folder. It contains **`app.py`**, **`requirements.txt`**, **`START_FLAMEX.bat`**, **`data`**, and **`modules`**.
3. Double-click `START_FLAMEX.bat`. It opens a terminal, creates `.venv`, installs packages, and starts the dashboard.
4. Open **http://localhost:8501** if it doesn't open automatically.

**Manual Windows launch**: Open File Explorer in the folder where you see `requirements.txt`, click the address bar, type `cmd`, Enter, then run:

```bat
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If `streamlit` is not recognized, use `python -m streamlit` (above). If it says `requirements.txt` not found, your terminal is in the wrong folder. Use `dir` to check.

### Cross-platform / Linux / macOS

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

Python 3.10+ recommended. Streamlit Community Cloud provides Python in its environment.

## What is in the app?

| Section | What it does | Scientific scope |
|---|---|---|
| Mission overview | Filtered record counts, missingness, ranked evidence | Loaded FLEX only; catalog separately |
| Investigation explorer | 21 sourced NASA investigation descriptions; user-adjustable ranking; side-by-side comparison | Metadata, not observation-level measurements |
| Combustion explorer | Five linked interactive plot types with hover record IDs | O₂/rate, pressure/rate, diameter/time, rate/time, O₂/outcome |
| Fuel comparison lab | Recomputed fuel-specific fits, interaction test, reproducibility comparison | OLS + HC3; no slope-equivalence claim |
| Stability & uncertainty | Brown–Forsythe, mean-centered Levene, Breusch–Pagan, White, Cook, sensitivity, anomaly hunter | Outliers flagged, never deleted |
| Predictive intelligence | Mean/linear/forest regression, grouped pressure-regime CV; outcome classification with stratified CV and reliability gate | No safety or deployment certification |
| Artemis scenario explorer | User-defined O₂, pressure, droplet diameter and fuel; historical neighbors; coverage/withheld predictions; reports | NASA exploration-atmosphere reference is **34% O₂ at 8.2 psia**; the separate historical materials test reference is **30% O₂ at 10.2 psia**. Both are reference points, not physical safety bands |
| FlameIQ research assistant | TF-IDF retrieval across 22 cited NASA source summaries plus deterministic FLEX record/statistics tools | No API key, sourced comparisons, unsupported raw measurements refused |
| Research brief & sources | Brief download (Markdown/HTML), NASA links and audit data | Clear evidence classes |

## Source separation

- `data/flame_intelligence_master.csv` — **the exact 274-row, 15-column source experimental table provided by the team**, included as-is and never rewritten by calculations. SHA256 is displayed inside the app.
- `data/investigations.csv` — a **source-linked NASA investigation index**, not a collection of the full experiment datasets. Most rows intentionally say `Verify on PSI` for unverified conditions, instruments and sensors.
- `data/evidence_library.csv` — **22 concise, curated paraphrases** of NASA FLEX, BASS-II and Saffire investigation descriptions, each with an evidence ID, source title/section, and official NASA link. These are metadata/evidence summaries, not numerical experimental records.
- User scenario input — always labeled `USER-DEFINED SCENARIO — NOT AN OBSERVED NASA EXPERIMENT`.
- Synthetic data — **none generated or included**.

NASA PSI FLEX: https://psi.nasa.gov/physci/repo/data/investigations/PSI-69

NASA PSI index: https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/

Challenge: https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/

## Key verified calculations using default full dataset

- 274 records, 2 recorded fuels, 3 end-outcome categories; 258 complete oxygen/burning-rate pairs.
- Methanol (N=151) oxygen slope ≈ **1.504754**; Heptane (N=107) slope ≈ **1.523092**.
- Residual-variance ratio (using sample variance, per-fuel OLS) ≈ **3.3657**.
- Brown–Forsythe p ≈ **1.46519×10⁻⁵**. Tests differences in model residual variation, **not directly physical flame stability**.
- Two separately sourced NASA reference conditions are shown: **exploration atmosphere 8.2 psia / 34% O₂** and **historical spacecraft material testing 10.2 psia / 30% O₂**. Zero FLEX records satisfy either associated *descriptive two-condition query* (O₂ ≥ the reference percentage and pressure ≤ the reference pressure). Those queries are diagnostic coverage regions, **not NASA-defined atmospheric bands or safety thresholds**. Sources: https://ntrs.nasa.gov/citations/20240003211 and https://ntrs.nasa.gov/citations/19880003147 .
- The team's previously quoted variance values differ slightly under the stated variance convention. The app recalculates values instead of forcing agreement.

## Interpretation and units

The original data says `Burning rate; mm`. The physically intended unit is not asserted here. NASA's detailed measurement description / data dictionary must be checked before assigning mm²/s to the plotted quantity. The original table's `CO initial ambient composition; mole fraction` likewise keeps the original `CO` label, pending verification of whether a subscript was lost during transcription.

The model uses complete-case cohorts *only for each calculation*, never drops raw rows, never imputes burning rate, and flags suspect observations (e.g. nonpositive pressure) without declaring them erroneous. Catalog rankings are transparent **editorial assessments**, not scientific fire-risk scores.

### Model A: grouped regression validation

The 4 pressure-regime folds are made from **unique pressure settings**, so identical pressure values are never assigned to different folds. Models: train-mean baseline, ridge regression and Random Forest. Report out-of-fold MAE/RMSE/R². The empirical `±90th-percentile absolute OOF residual` band is **not** a calibrated or conditional 90% predictive coverage guarantee. Inputs outside observed fuel / variable / joint-support bounds do not get predictions. Reference-atmosphere scenarios with unsupported joint conditions are withheld. The two NASA reference points are not fire-safety boundaries.

### Model B: classification validation

Class-weighted Random Forest, stratified five-fold CV; confusion matrix, per-class recall/precision/F1, macro-F1, multiclass Brier and log loss, coarse calibration diagnostics. If macro-F1 <0.55 or *any* class recall <0.40, per-scenario probabilities are gated off. Even passing this internal rule **does not** prove external calibration or habitat safety validity.


## FlameIQ: source-backed questions (new)

Open **FlameIQ research assistant** in the left navigation, select a suggested question and click **Ask selected example**, or type an original question. Try:

1. **Which investigations matter for crew-habitat material fire safety?** — compares NASA evidence from FLEX, BASS-II and Saffire; marks similarities as inferred.
2. **Compare FLEX, BASS-II and Saffire-I for spacecraft research.** — shows source-linked claims and explains that the different experimental geometries are not interchangeable.
3. **Which sensors are described for Saffire-I?** — cites a NASA investigation page rather than fabricating readings.
4. **Inspect FLEX test 114.** — reads the actual bundled experimental record.
5. **Give exact Saffire-II burning-rate values.** — refuses: source metadata exists, but its raw experiments are not loaded.

Every source-linked claim carries a `NASA-###` evidence ID and clickable NASA URL. Download the library in FlameIQ's **Browse the verified NASA evidence library** expander. In **Investigation explorer**, comparing catalog entries with verified evidence shows linked research-source cards.

**Scope:** These 22 evidence entries cover FIVE named experiments/groups (FLEX, BASS-II, Saffire-I, Saffire-II and Saffire-III); the original 21-entry investigation catalog is still available. Other investigations remain catalog-only, with detailed fields requiring verification. This is a constrained local retrieval-and-analysis assistant, **not a complete scientific literature search tool**. Source descriptions are paraphrases, not claims of NASA review of this app.

For auditing retrieval, see `docs/EVIDENCE_METHOD.md`. For demo questions see `docs/FLAMEIQ_DEMO.md`.

## FlameIQ unrestricted question entry and optional conversational AI

**You can type any question** in FlameIQ's chat box; you are not restricted to suggested questions. Three modes are available:

- **Evidence search · no model (default):** works with no account or key and retrieves source passages for arbitrarily phrased research questions. It does *not* produce general LLM conversation. Out-of-scope research questions are marked UNKNOWN.
- **OpenAI · API key:** actual free-form model conversation and follow-ups. Select **Research evidence** for source-constrained science answers, or **General Q&A** for non-NASA general discussion (explicitly labeled NOT NASA-VERIFIED). This requires a separately configured private API key and may incur provider charges.
- **Ollama · local model:** actual free-form model conversation and follow-ups on your own computer, with no API key. Install Ollama and pull a compatible model; this cannot run on a visitor's laptop through Streamlit Community Cloud.

The source-constrained research mode always provides reproducible evidence below the generated response and withholds model outputs that introduce numbers absent from evidence. No mode certifies habitat or material fire safety. The assistant does not automatically browse NASA PSI or retrieve other unprovided numerical datasets.

**OpenAI setup (optional):**

```bash
python -m pip install -r requirements-optional-ai.txt
```

Set `OPENAI_API_KEY` in your process environment or Streamlit Community Cloud **Secrets** (never commit a key). The base `requirements.txt` now includes the OpenAI SDK so the hosted feature is available once the private API key is configured. Nothing is sent to OpenAI in offline mode. `FLAMEX_MODEL` may be set in the environment; the local assistant remains the source of numerical evidence, and optional responses are rejected when they add unsupported numbers. Keep the toggle OFF for offline judging. Never enter keys in the app itself.

### Ollama setup for fully conversational AI without an API key (local Windows)

Install [Ollama](https://ollama.com/download), then in your terminal run:

```bat
ollama pull llama3.2:3b
```

Start FlameX as usual, visit **FlameIQ research assistant**, choose **Ollama · local model**, and set the model name to `llama3.2:3b`. Ollama must be running on **the same computer as Streamlit** and needs several GB of available resources. The default evidence-only mode remains fully functional if Ollama is unavailable.

For the **public Streamlit Cloud** demo, use key-free evidence search or configure a hosted OpenAI key privately in Streamlit Secrets. Streamlit Cloud cannot access the Ollama instance running on someone else's laptop. The hosted `openai` dependency is already included in `requirements.txt`; a private API key is still required for hosted conversation.

## Publish (requires a GitHub account; not performed automatically)

1. Make a **public GitHub repository** with the **contents** of this project folder at its root (`app.py`, `requirements.txt`, `modules/`, `data/`). Do not upload `.venv` or secrets.
2. In **Streamlit Community Cloud**, choose **Create app → GitHub repo → branch → main file path: `app.py`**.
3. Once deployed, open the public app URL and test every section on desktop and mobile/tablet widths. The `data/` folder already contains the experiment CSV; no API key is needed.
4. Add the public URL, repository URL, and a demo link to the NASA Space Apps submission portal.

**No public URL is bundled**: deploying requires access to your GitHub and Streamlit accounts. An actual live deployment must be checked before claiming the app is published.

## Test locally

```bash
python -m pip install pytest
python -m pytest tests -q
```

The test suite verifies column mapping, unchanged raw CSV, scientific metrics, flags, filters, NASA-data separation, grouped regression, classification, unsupported queries, source URLs, cross-investigation citations, and the no-coverage Moon scenario. See `docs/QA.md` for test status and limitations.

## Scientific ethics / AI disclosure

- Independent project by Dynamic Duo; not an official NASA product or endorsed by NASA.
- NASA source links are included and original data remains unchanged.
- Code, project copy, and data explanations were developed with assistance from OpenAI ChatGPT (AI-assisted). FlameIQ's **default** mode is TF-IDF source retrieval with deterministic evidence assembly and statistical tools, not an open-ended LLM. Optional OpenAI text paraphrasing can be enabled with a private API key; disable for offline judging.
- No AI-generated NASA imagery, NASA logos, fake laboratory runs or synthetic observational datasets are used.
- Report any meaningful uncertainties, missing experimental domains, influence sensitivity, and validation weaknesses to judges.

## License / attribution

Project code may be reused by the authors; NASA source documents and datasets retain their separate original attribution and licensing terms. Before sharing, consult each NASA PSI page for its license and credit statements. This project does not assert ownership of NASA's research.
