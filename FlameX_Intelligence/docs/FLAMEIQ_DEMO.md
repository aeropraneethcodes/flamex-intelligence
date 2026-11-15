# FlameIQ — 45-second research demonstration

1. Open **Investigation explorer**. Choose **FLEX** and **BASS-II** and expand **Verified NASA evidence for selected investigations**. Describe the difference between droplets and solid materials with NASA citations.
2. Open **FlameIQ research assistant** and ask: **Which investigations matter for crew-habitat material fire safety?** The reply retrieves and cites separate NASA passages for FLEX, BASS-II and Saffire-I and explains the inference.
3. Ask: **Compare methanol and heptane slopes.** The reply calculates statistics from the bundled FLEX data instead of inventing measurements from other experiments.
4. Ask: **Give exact Saffire-II burning-rate values.** The assistant explicitly refuses because numerical Saffire-II data are not loaded.
5. Open the expandable **verified NASA evidence library** to show evidence IDs, source sections and links.

**One-sentence positioning:** FlameIQ retrieves vetted NASA investigation metadata, calculates FLEX observations locally, and says when the required experiment data are missing.

**Honest disclosure:** local TF-IDF retrieval and rule-constrained response synthesis; optional external text paraphrasing, not required. Cite the NASA PSI sources in the submission.

## Free-form conversational mode

FlameIQ now accepts arbitrary typed questions. For full conversational answers and follow-ups, select **OpenAI · API key** (private key required) or **Ollama · local model** (downloaded model required). Select **Research evidence** for NASA-grounded replies; select **General Q&A** for conversations outside the scientific evidence set.

Try: “Why don't these FLEX droplet measurements establish solid-material safety?”, “What study would help fill the exploration-atmosphere coverage gap?”, and “What evidence could differentiate uncertainty from instability?”

The offline source-search mode remains fully available without an API key. It retrieves relevant evidence for arbitrary wording, but it is not an unrestricted language model.
