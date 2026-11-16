# FlameX Intelligence — Evidence-first public release · November 2026

- Preserves the existing 11-page Streamlit research desk, blue-and-white design, Guided Tour, all original NASA evidence/catalog tables, FLEX measurements and research analyses.
- Makes FlameIQ completely no-key and no-cost at runtime. Removes Hugging Face, OpenAI, Gemini, and Ollama provider selectors, hosted provider backend, and OpenAI requirement. There are no outbound language-model calls.
- Adds transparent intent routing for regressions, fuel variability, record counts, means, outcome categories, predictive-model evaluation, NASA experiment comparison, atmospheric references, and unsupported numeric/safety questions.
- All generated numeric summaries are built from the selected scientific data; numeric reply templates include a fail-closed claim guard against extra numeric literals. Original measurement units/provenance remain explicitly uncertain.
- New source/method audit expander for last FlameIQ answer; homepage clearly shows three research-intelligence layers.
- Keeps the original research/scenario models and does not pretend that metadata-only BASS-II/Saffire/SAME records are raw measurements.
- Automated tests and mock Streamlit page checks included. Verify the live site after GitHub deployment; a live-browser deployment test is not included.
- This system is an independently developed scientific research interface, not NASA-endorsed or an operational spacecraft fire-safety tool. AI assisted with software development and writing; the live research assistant is deterministic rather than a hosted generative model.
