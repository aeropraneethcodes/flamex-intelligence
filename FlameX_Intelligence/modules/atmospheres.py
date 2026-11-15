"""NASA atmosphere reference cases; references are not FLEX measurements or safety thresholds."""
from .data_loader import psi_to_pressure

EXPLORATION = {'label':'NASA exploration-atmosphere reference (nominal)', 'oxygen':0.34, 'psi':8.2,
               'url':'https://ntrs.nasa.gov/citations/20240003211',
               'description':'NASA Moon-to-Mars exploration atmosphere cited for habitats with frequent EVA; vehicle requirements may differ.'}
HISTORICAL = {'label':'Historical spacecraft material-flammability test reference', 'oxygen':0.30, 'psi':10.2,
              'url':'https://ntrs.nasa.gov/citations/19880003147',
              'description':'Previously used material-flammability test atmosphere; not a nominal Moon-habitat atmosphere.'}
REFERENCES = [EXPLORATION, HISTORICAL]

def reference_count(df, reference):
    """Descriptive two-condition coverage window (not a physical atmosphere or safety band)."""
    return int(((df.oxygen >= reference['oxygen']) &
                (df.pressure <= psi_to_pressure(reference['psi']))).sum())

def references_markdown(df):
    lines=[]
    for item in REFERENCES:
        n=reference_count(df,item)
        lines.append(f'- **{item["label"]}:** {item["oxygen"]*100:g}% oxygen at {item["psi"]:g} psia ({psi_to_pressure(item["psi"]):.1f} mmHg). '
                     f'**{n}** FLEX rows meet the broad two-condition query O₂ ≥ {item["oxygen"]*100:g}% and pressure ≤ {item["psi"]:g} psia. '
                     f'The query is **not** a verified physical testing atmosphere band. [NASA source]({item["url"]}).')
    return '\n'.join(lines)
