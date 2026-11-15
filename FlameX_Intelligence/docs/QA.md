# Quality assurance — final competition build

Local automated verification:

- `python -m pytest -q tests` — 50 tests passed
- `PYTHONPATH=. python tests/mock_streamlit_smoke.py` — 11/11 simulated page runs passed
- FLEX source hash unchanged from the team-provided original input
- Native source-table upload parser tested for exact, qualified, missing, and unparsed values
- Seven slides exported to PDF and independently rendered for layout inspection

These tests **do not** establish a live browser deployment, external API availability, original NASA PSI source-file authentication, or the scientific validity of future imported tables. Those require separate real-world verification.
