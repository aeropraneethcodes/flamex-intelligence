"""Evidence-classified portable research brief in HTML and Markdown."""
from datetime import datetime,timezone
from html import escape

def build_markdown(scenario, neighbors, prediction, findings, model_results, source_hash):
    s=scenario
    lines=['# FlameX Intelligence · Evidence-grounded Research Brief',
      f'Generated: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}',
      '\n> **USER-DEFINED SCENARIO — NOT AN OBSERVED NASA EXPERIMENT**',
      f'Fuel: {s["fuel"]}; O₂ mole fraction: {s["oxygen"]:.3f}; pressure: {s["pressure"]:.1f} mmHg; droplet diameter: {s["diameter"]:.2f} mm.',
      f'Original FLEX CSV SHA256: `{source_hash}`',
      '\n## Domain coverage',f'**{neighbors["domain"]}** — {neighbors["reason"]}',
      '\n## Experimental neighbors (OBSERVED)']
    if neighbors['neighbors'].empty:lines.append('None for the selected fuel.')
    else:
      for _,r in neighbors['neighbors'].iterrows():
        lines.append(f'- {r["record_id"]}: O₂={r["oxygen"]:.3f}; P={r["pressure"]:.1f} mmHg; diameter={r["diameter"]:.2f} mm; rate={r.get("burn",float("nan"))}; outcome={r["outcome"]}; normalized distance={r["normalized_distance"]:.3f}.')
    lines.extend(['\n## Exploratory model'])
    if prediction.get('prediction') is None:lines.append('**UNKNOWN / WITHHELD:** '+prediction.get('reason','No supported prediction.'))
    else:
      lines.append(f'**CALCULATED, EXPLORATORY:** prediction={prediction["prediction"]:.4f}; empirical band [{prediction["lower"]:.4f},{prediction["upper"]:.4f}].')
      lines.append(prediction['method'])
    lines.append('\n## Ranked findings (CALCULATED / OBSERVED)')
    for _,r in findings.head(5).iterrows():
      lines.append(f'- {r["Title"]} [{r["Class"]}]: {r["Evidence"]} Rank score {r["Rank score / 100"]:.1f}/100 (editorial relevance rubric). Limitation: {r["Limits"]}')
    lines.extend(['\n## Limitations / evidence boundaries',
      '- FLEX liquid-droplet results cannot alone establish fire safety for solid interior materials.',
      '- The uploaded CSV is only one research dataset, not the full NASA archive.',
      '- Original column `Burning rate; mm` needs confirmation of its intended unit against source metadata.',
      '- Flow, hardware, soot diagnostics, habitat-specific materials and repeated tests are not all represented in this table.',
      '- Empirical bands are not independently calibrated for out-of-domain use; no safe/unsafe verdict is produced.',
      '\n## Follow-up research priorities',
      '1. Verify source metadata and burning-rate units with NASA FLEX documentation.',
      '2. Obtain independently documented solids/fire-spread and smoke-detection investigations from NASA PSI.',
      '3. Compare measured atmospheres with the intended habitat band and identify missing coverage.',
      '4. Check repeated conditions, independent test sets, and instrument-level uncertainty before drawing engineering conclusions.',
      '\n## Sources',
      '- Original team-supplied FLEX experimental CSV (SHA256 above).',
      '- https://psi.nasa.gov/physci/repo/data/investigations/PSI-69',
      '- https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/',
      '- https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/',
      '\n**No NASA endorsement is implied. NASA and the original investigation teams retain credit for the source research.**'])
    return '\n\n'.join(lines)+'\n'

def markdown_to_html(md):
    # Plain-text preformatted, safe offline and no external assets
    return '<!doctype html><html><head><meta charset="utf-8"><title>FlameX research brief</title><style>body{max-width:900px;margin:42px auto;font-family:Arial,Helvetica,sans-serif;color:#17324d;background:#f7f9fb;line-height:1.55}pre{white-space:pre-wrap;word-wrap:break-word;background:white;border:1px solid #dce4eb;border-top:4px solid #2878b5;padding:32px;border-radius:10px}a{color:#2878b5}</style></head><body><pre>'+escape(md)+'</pre></body></html>'
