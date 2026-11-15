# NASA atmosphere reference correction (2026-11-14)

1. **Nominal exploration atmosphere** — NASA Moon-to-Mars research describes **8.2 psia at 34% O₂** as a reference atmosphere for frequent EVA. [NASA NTRS: Moon to Mars Exploration Atmosphere](https://ntrs.nasa.gov/citations/20240003211).
2. **Historical material-flammability test** — an older spacecraft materials testing condition was **10.2 psia at 30% O₂**, documented by NASA. [NASA NTRS: Spacecraft material flammability testing and configurations](https://ntrs.nasa.gov/citations/19880003147).

These are **point references**, not NASA-approved continuous safety envelopes. The app plots distinct points rather than coloring the entire region as safe or applicable. The diagnostic query `oxygen ≥ reference oxygen AND pressure ≤ reference pressure` finds zero of the 274 FLEX records for either reference. It is a query used to illustrate missing experimental coverage, **not** a claim that every atmosphere in that broad rectangle represents a NASA design.

No inference about crew safety, fire resistance, or a physical flammability limit follows from the coverage count.
