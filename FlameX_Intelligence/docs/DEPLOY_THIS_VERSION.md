# Deploy FlameX · evidence-first no-API edition

**Project root:** The folder containing `app.py`, `requirements.txt`, `data/`, `modules/`, and `tests/`.

## Existing GitHub / Streamlit Community Cloud deployment

1. Download and extract the ZIP. Open its inner `FlameX_Intelligence/` folder.
2. In the existing GitHub repository, replace the corresponding files under `FlameX_Intelligence/` (the repository path currently used by Streamlit). **Do not upload the ZIP itself as the app, or put a second `FlameX_Intelligence/` folder inside the first.**
3. Commit the modified and added files (including `modules/research_engine.py`). Remove legacy files from the repository if present: `modules/llm_chat.py`, `requirements-optional-ai.txt`, and `docs/HOSTED_AI_SETUP.md`. They are not used in this edition.
4. Keep the existing Streamlit entrypoint **`FlameX_Intelligence/app.py`**. You do not need to change the deployment branch.
5. In Streamlit Cloud Secrets, remove any unused `HF_TOKEN`, `HF_MODEL`, `OPENAI_API_KEY`, or similar settings. This new edition will not call them even if they remain configured, but removing them minimizes risk.
6. Reboot/redeploy. Open the public site in an incognito window; check Overview, Guided Tour, all other pages and FlameIQ.

## Three judge questions

- `What do the fuel regressions reveal and what can they not prove?` — should show slopes, residual variance and limitations.
- `How accurate are the models under pressure-group cross-validation?` — should show FLEX model evaluation with warnings about generalization.
- `What are the exact Saffire-II burning-rate measurements?` — must say the original raw Saffire measurements are not loaded.

Open **Verify the last answer** to inspect the route, method and NASA sources. No keys or sign-in are required for visitors.

## Local testing (optional)

From inside `FlameX_Intelligence/`:

```bash
python -m pip install -r requirements.txt
python -m pytest -q tests
python -m streamlit run app.py
```

The Streamlit browser UI must be checked on the live deployment. The repository includes only original FLEX experimental rows; other NASA investigations have official source links and a data-lab import workflow, not bundled raw measurement tables.
