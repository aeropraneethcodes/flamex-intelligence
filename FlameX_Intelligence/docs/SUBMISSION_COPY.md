# Ready-to-paste project submission text

Replace `[PUBLIC_APP_URL]`, `[PUBLIC_REPO_URL]`, and `[PUBLIC_DEMO_URL]` with the real links **after you deploy and share**. Do not submit the placeholders.

## Project name
FlameX Intelligence — Evidence-Grounded Fire-Safety Research Desk

## Project summary (under 1,500 characters)

NASA's microgravity combustion results are spread across investigations that use different fuels, experimental conditions, instruments, and measurement methods. FlameX Intelligence is an interactive research desk that helps users discover the relevant investigations, understand what evidence is actually available, and identify questions that the data cannot answer. A NASA-linked catalog of 21 investigations provides adjustable, transparent rankings for crew-habitat research. A focused analysis lab uses a real 274-record FLEX droplet dataset to compare fuel-specific oxygen relationships, evaluate statistical uncertainty, and show experimental coverage gaps. The Artemis Scenario Explorer checks historical coverage and withholds unsupported predictions. FlameIQ retrieves source-linked NASA investigation summaries and deterministic FLEX findings; optional language-model conversation can be enabled without changing the underlying evidence. FlameX does not assess whether a habitat is safe. Instead, it connects research discovery, scientific interpretation, and the limitations that matter when planning further studies for Moon and Mars missions.

## Project details

### Problem
NASA microgravity combustion research is essential for investigating spacecraft fire prevention, detection, and suppression, but it is difficult to compare investigations when their fuels, geometries, test atmospheres, and measured outputs are different. A single graph or broad AI summary can obscure those differences and overstate what the data prove.

### Solution
FlameX offers three connected workflows. **Summarize:** browse 21 source-linked NASA investigation entries with objectives, fuels, apparatus and available measurements, marking details that need source confirmation. **Rank:** adjust transparent team-assessed research-relevance weights and compare investigations side-by-side; the scores are discovery aids, not NASA ratings or hazard scores. **Interpret:** investigate the original 274-row FLEX experimental subset with non-destructive filters, fuel regression, residual checks, anomaly inspection, and pressure-grouped model validation.

### Scientific findings and limitations
Recalculation of the complete oxygen/rate records gives Methanol slope 1.504754 (N=151) and Heptane slope 1.523092 (N=107). The ratio of per-fuel OLS residual sample variances is about 3.3657, and a Brown–Forsythe test gives p approximately 1.47×10^-5. This supports a difference in *model residual dispersion*, not a direct measurement of flame stability. The fuel-by-oxygen interaction test is not significant; that does not establish equivalence. The source labels its rate field `Burning rate; mm`; physical dimensional interpretation is withheld pending verification of the original NASA metadata.

### Human space exploration relevance
The scenario explorer compares user-defined atmospheres with NASA's **8.2 psia / 34% O2 exploration reference** and a distinct **10.2 psia / 30% O2 historical materials-test condition**. None of the 274 FLEX rows satisfies the associated two-condition coverage query for either reference. That indicates a gap in this *loaded subset*; it does not establish a fire-safety threshold or determine whether a habitat is safe. The app withholds unsupported model output and identifies the need for complementary solid-material and airflow investigations.

### FlameIQ and AI disclosure
FlameIQ's default no-key mode retrieves documented NASA-source summaries and calculates answers from FLEX observations while labeling OBSERVED, CALCULATED, INFERRED, and UNKNOWN claims. Optional hosted OpenAI and local Ollama modes support free-form conversation when configured; they are explicitly separated from NASA-verifiable evidence. ChatGPT was used to assist with software, writing, analysis and presentation production. The project is independent and not NASA-endorsed.

### Limitations and next steps
Only FLEX observation-level data are loaded. BASS-II, Saffire, and other catalog entries include official NASA source references, not imported raw measurements. The source-unit ambiguity, incomplete atmosphere coverage, limited sensor-level uncertainty and exploratory classifier performance are disclosed. Future work would ingest further verified PSI datasets under a versioned schema and validate models against independent experiments.

## Links to paste after publishing

- **Live project:** [PUBLIC_APP_URL]
- **Public repository:** [PUBLIC_REPO_URL]
- **Project demonstration (7 slides or video):** [PUBLIC_DEMO_URL]
- **NASA FLEX data/source:** https://psi.nasa.gov/physci/repo/data/investigations/PSI-69
- **NASA PSI investigation catalog:** https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/
- **Official challenge:** https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/

## Short live demonstration script (~30 seconds)

“FlameX helps researchers find the right microgravity combustion evidence. First, our catalog ranks NASA investigations using criteria the user can change. Next, we drill into 274 actual FLEX records, compare two fuels and report the uncertainty instead of treating the fitted model as ground truth. Our scenario view exposes a coverage gap near NASA's exploration-atmosphere reference, so the model withholds unsupported conclusions. FlameIQ links the available sources and refuses to invent Saffire measurements we haven't loaded. FlameX finds evidence and makes its limits visible.”

## Final checklist

- [ ] Replace all three placeholder URLs.
- [ ] Verify actual deployment works in an incognito browser.
- [ ] Provide public access to the demo presentation/PDF or video.
- [ ] Review all NASA citations, source licenses, AI disclosures, and final submission form fields.
- [ ] Submit through the official team project page by the deadline shown for your event.
