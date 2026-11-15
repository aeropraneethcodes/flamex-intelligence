# Ready-to-use project submission copy / demo outline

## Suggested project title
**FlameX Intelligence — Evidence-Grounded Fire-Safety Research Desk**

## Project summary (approximately 150 words)

NASA's microgravity fire experiments hold important information for designing safer crew habitats, but their findings are spread across investigations with different materials, conditions and measurements. FlameX Intelligence is an interactive, evidence-grounded research desk designed to make this science easier to discover, compare and interpret. A source-linked catalog covers 21 NASA combustion and smoke investigations and ranks their relevance using visible, adjustable research criteria. A deeper laboratory analyzes a real 274-record FLEX droplet dataset, including fuel-specific regression, residual diagnostics, statistical tests and grouped-model validation. Our Artemis scenario explorer checks whether proposed atmospheres are actually represented by historical records and withholds unsupported predictions. FlameIQ, our local research assistant, connects questions to loaded records, calculated findings and NASA investigation metadata; it explicitly declines unsupported numerical claims. FlameX does not claim to certify fire safety. Instead, it helps researchers locate evidence, understand uncertainties and recognize where further experiments are needed for future human space exploration.

## 30-second demonstration sequence

**0–6 s:** Investigation Explorer: adjust two relevance weights and show how BASS-II, Saffire and FLEX appear. State: 'Find the right NASA investigation first.'

**6–13 s:** Drill into FLEX in Combustion Explorer: show oxygen-vs-rate scatter, regression bands and source record hover. State: 'Then examine the actual measurements.'

**13–20 s:** Fuel Comparison: show reproduced slopes and Brown–Forsythe, briefly show caveat. State: 'Every finding gets a method and limitations.'

**20–26 s:** Artemis Scenario: NASA nominal exploration-atmosphere reference, 34% O₂ and 8.2 psia; show zero joint coverage and withheld prediction. State: 'No data means no invented safety answer.'

**26–30 s:** FlameIQ: ask for Saffire-II numerical results; it refuses without a loaded dataset. State: 'FlameIQ knows when evidence is missing.'

## Seven-slide demonstration fallback

1. **FlameX Intelligence** — problem, mission, team and non-endorsement.
2. **Scientific discovery** — investigation ranking with visible editable rubric.
3. **FLEX evidence** — 274-row real dataset and source/provenance.
4. **Scientific insight** — fuel fits and residual spread, limitations.
5. **Prediction under scrutiny** — pressure-grouped CV and uncertainty.
6. **Atmospheric coverage gap** — Moon scenario, zero matching records, no verdict.
7. **FlameIQ + future work** — evidence refusal, sources, next datasets.

## Submission checklist

- [ ] Publish project repository publicly. Check the dataset's original PSI licensing and attribution.
- [ ] Deploy to Streamlit Community Cloud; confirm the URL loads on a fresh browser.
- [ ] Open every page and test sidebar filters on the deployed version.
- [ ] Include ≤7 slides or ≤30-second video according to the current challenge submission rules.
- [ ] Add NASA PSI source links and the official challenge URL.
- [ ] Disclose ChatGPT-assisted code/writing and optional LLM model use.
- [ ] Do not claim NASA endorsement or that the model predicts real habitat safety.
- [ ] Keep NASA 8.2 psia / 34% O₂ exploration and 10.2 psia / 30% O₂ historical test reference POINTS distinct; neither is a safety band.
- [ ] Confirm the physical burning-rate unit and CO-label semantics from source documentation.
