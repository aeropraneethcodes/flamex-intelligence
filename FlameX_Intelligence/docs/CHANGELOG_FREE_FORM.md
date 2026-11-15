# FlameX Intelligence — free-form conversation & atmosphere reference update

## New
- FlameIQ now accepts free-form chat prompts; recommended questions are optional.
- Three answer engines: evidence-only offline search, OpenAI hosted conversation (private API key), and Ollama local conversation (downloaded model, no API key).
- Research-evidence mode and general-conversation mode have distinct limitations and labels.
- Follow-up conversation history is sent only to the selected model provider, if a provider is selected.
- NASA evidence and reproducible FLEX statistics appear below generated research interpretations.
- Unsupported BASS-II / Saffire numerical claims remain blocked.
- OpenAI SDK is part of the root environment requirements; an actual API key is never bundled.

## Scientific corrections
- Lunar exploration atmosphere reference: 8.2 psia, 34% oxygen. Source: https://ntrs.nasa.gov/citations/20240003211
- Historical spacecraft material-flammability reference: 10.2 psia, 30% oxygen. Source: https://ntrs.nasa.gov/citations/19880003147
- Both are discrete sourced reference conditions, not a continuous safety or design band.
- Coverage queries O2>=reference and pressure<=reference retain 0 FLEX records for each case. No unverified safety claim.

## Files
- `modules/atmospheres.py`, `modules/llm_chat.py` added.
- App, findings, models, FlameIQ, README and the demo PowerPoint/PDF updated.
- `docs/OPEN_ENDED_AI.md` and `docs/ATMOSPHERE_REFERENCES.md` document usage and source assumptions.
- Expanded tests: 32 passing science/integration tests + 9 mocked page checks.

## Testing limitation
- Real Streamlit desktop/browser rendering and the live OpenAI/Ollama network connection were not executed in the build environment. Fake OpenAI responses verified provider routing without calling an API.
