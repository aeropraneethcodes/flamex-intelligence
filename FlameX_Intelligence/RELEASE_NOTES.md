# Homepage and Navigation Polish · November 15, 2026

- Retained the original FlameX palette and all existing scientific pages/plots.
- Added a highlighted evidence-first homepage hero and science spotlight with three interactive research angles.
- Added context-aware top navigation, three homepage calls to action, and an always-available judge-demo shortcut.
- Reorganized the sidebar so data mapping, uploads, and experiment filters are discoverable but collapsed by default.
- Added a one-click experiment-filter reset; numeric hero statistics remain data-driven, not hard-coded.
- Preserved source and evidence disclaimers to prevent extrapolating laboratory residual statistics into spacecraft safety decisions.
- No new third-party dependencies, no new API-key requirements, and no changes to the bundled FLEX data.
- 11 page branches verified with the mock runner, plus automated tests. A real Streamlit browser check still needs to occur on deployment.

---

# FlameX Intelligence — Elite competition release (2026-11-15)

**Deliverables:** 11-page Streamlit app, 7-slide PowerPoint and PDF, 2-page evidence brief, a PSI source registry, a user-supplied experimental-table CSV importer, grounded scientific question-answering, unit/provenance warnings, reproducibility tests and submission copy.

**Validated:** 50 automated tests passed; 11 simulated Streamlit page branches passed; source FLEX SHA256 remained unchanged; 7-slide PDF and 2-page technical PDF were rendered and visually inspected.

**Not independently validated:** live public deployment, live hosted model availability, original NASA PSI byte-level provenance for the bundled FLEX input, or source-file downloads for other experiments. BASS-II, Saffire, and SAME experimental tables are **not** in the ZIP. Their NASA registry metadata is linked. The Data Lab can inspect CSVs supplied later without silently mixing different experiments.

**Hosted language models:** optional OpenAI and Hugging Face backends (account/provider terms apply). No credentials bundled. The default no-key evidence engine works locally and on a properly deployed Streamlit instance. This edition does not ship a Gemini backend.

This is a scientific research interface, not an operational spacecraft fire-safety system. AI-assisted code and writing were used; NASA has not endorsed this project.
