# FlameIQ · no-API research demonstration

The judge-facing assistant works with **no account, token, hosted model, or inference credits**.

1. Open **Guided Tour** for the high-level scientific story.
2. Open **FlameIQ research assistant**. Ask **“What do the fuel regressions reveal, and what can they not prove?”** The response recomputes regression statistics from the loaded FLEX records and names methodological limitations.
3. Ask **“How different are methanol and heptane residual variances?”** It recomputes the dispersion ratio and statistical test rather than inventing values.
4. Ask **“Why do FLEX, BASS-II and Saffire answer different questions?”** It retrieves NASA-linked metadata, without claiming these other experiments' raw data were imported.
5. Ask **“Give exact Saffire-II burning-rate values.”** FlameIQ refuses to fabricate missing measurements.
6. Expand **Verify the last answer** to see the detected intent, calculation/retrieval method, and NASA evidence sources.

**Honest SI disclosure:** This is an offline deterministic research-question interpreter plus evidence retrieval, statistical analysis, and separately evaluated machine-learning models. It is **not** a fully general generative language model and does not know arbitrary facts. Questions outside its supported evidence scope may receive a cautious or incomplete response. Model outputs are not operational fire-safety advice.
