# FlameX Intelligence — final GitHub/deployment handoff

**Team:** Dynamic Duo  
**Independent NASA Space Apps 2026 project — not NASA-endorsed**  
**Challenge:** [Flame in Freefall](https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/)

## What is included

- `app.py`, `modules/` — nine-page Streamlit research dashboard, statistics, evidence retrieval, optional language-model conversation, cautious modeling, scenario explorer, report generator.
- `data/flame_intelligence_master.csv` — **original, unchanged 274-record FLEX source table**. No synthetic NASA measurements.
- `data/investigations.csv` — 21-entry NASA-linked discovery catalog. Entries are **not** imported experiment measurements.
- `data/evidence_library.csv` — 22 curated, source-linked *paraphrases* of five FLEX/BASS-II/Saffire investigation descriptions.
- `docs/FlameX_Demo_7_Slides.pptx` and `.pdf` — seven-slide demo using calculations reproduced from the real CSV.
- `docs/SUBMISSION_COPY.md`, `docs/REFERENCES.md` — copy-ready project details, limitations, NASA links, and AI disclosure.
- `tests/` — offline source-science and reasoning checks.

## Publish on GitHub

1. Extract the complete ZIP. Open the **inner `FlameX_Intelligence/` folder** (you should see `app.py` and `requirements.txt`).
2. Create a public GitHub repository. Upload the **contents** of this folder at the repository root, not the parent ZIP or another nested folder.
3. Double-check that `.env`, `.venv`, `.streamlit/secrets.toml`, API keys, and credentials are NOT in the repository. The `.gitignore` already excludes them when using Git; web-upload requires manual checking.
4. Publish the code and verify the `data` and `modules` folders exist on GitHub.

## Deploy to Streamlit Community Cloud

1. Go to https://share.streamlit.io and create a new app from the GitHub repo.
2. Select the repository and branch; **main file path: `app.py`**.
3. Once built, open the public app URL in an incognito window. Test all nine sections, changes to filters, and research-brief exports.
4. **Evidence search needs no key.** If enabling hosted conversational AI, set the key under **App settings -> Secrets**, never in source code:

```toml
OPENAI_API_KEY = "your_actual_private_key"
FLAMEX_MODEL = "gpt-4o-mini"
```

5. In FlameIQ choose `OpenAI · API key` -> `Research evidence`. Ask a free-form question. The app defaults to key-free evidence retrieval to avoid automatic API use. Set a provider spending budget before publicly exposing a paid model; the app does **not** enforce a provider-wide spend limit.
6. Public Streamlit hosting cannot access an Ollama model running on a visitor's local computer. Use Evidence Search or OpenAI on public hosting.

## Local run

On Windows double-click `START_FLAMEX.bat`. Or, with Terminal opened in the folder containing `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Verified in this workspace

- **37/37** automated scientific/integration/retrieval tests passed.
- **9/9** mocked Streamlit page checks passed.
- **7/7** slides rendered in both PowerPoint and PDF.
- An actual hosted Streamlit browser session and live paid API call were **not** executed here.

## Before submitting

- [ ] Confirm deployment opens without login on a new browser.
- [ ] Test **all nine pages** and select a narrower oxygen/pressure range, then reset filters.
- [ ] Inspect original FLEX test 114. It must remain in the raw data; nonpositive pressure is flagged, not silently removed.
- [ ] Check the Investigation Explorer ranking changes when weights are edited. These are **editorial scores**, not NASA safety ratings.
- [ ] FlameIQ: try a free-form FLEX question, a three-investigation comparison, and a request for unavailable Saffire-II exact measurements. Unsupported measurements must be refused.
- [ ] Confirm the atmosphere references: **8.2 psia / 34% O2** exploratory design reference versus **10.2 psia / 30% O2** historical flammability test condition. Neither point is a validated safety boundary.
- [ ] Inspect research-brief exports and the seven-slide demo PDF.
- [ ] Add your **real** public Streamlit URL, GitHub URL, and public slide/PDF link to the Space Apps project form. No URLs are invented in the package.
- [ ] Include NASA data/source links and disclose use of ChatGPT-assisted programming/writing and any optional LLM.
- [ ] Verify the project's pre-event work is permitted under your event's eligibility guidance.

## Scientifically important limits

- The physically intended unit of `Burning rate; mm` and the meaning of the CSV's `CO` composition label still require original NASA data-dictionary confirmation. This app retains the **source's exact labels** rather than asserting mm²/s or CO₂.
- Ordinary least-squares slopes for the two fuels reflect **association**, not causation. A nonsignificant fuel-by-O2 interaction does not establish slope equivalence.
- Differences in model residual variance do **not** measure physical flame stability directly.
- Model A uses pressure-grouped cross-validation; the empirical error band is **not a guaranteed calibrated prediction interval**. Model B's weakest-class recall is low and its probabilities are withheld.
- Neither the FLEX table nor NASA metadata validates fire risk, suppression effectiveness, or any safe/unsafe crew-habitat threshold.
- Live browser rendering, paid OpenAI calls, and public hosting were **not performed** in this workspace. Local automated and mocked tests do not replace deployment QA.
