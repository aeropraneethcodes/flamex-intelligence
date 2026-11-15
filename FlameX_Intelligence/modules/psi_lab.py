"""Transparent, source-aware ingest of NASA PSI experimental-table CSV exports.

No cross-study numerical pooling. Source files are byte-preserved, provenance is explicit,
unsupported measurements remain missing, and approximate values are not silently treated
as exact numbers. This module does not infer undocumented physical units or fire safety.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib, io, re
import pandas as pd
import numpy as np

PSI_STUDIES = [
 dict(study='FLEX', id='PSI-69', family='Liquid droplet combustion', doi='10.60555/mbq8-0451', file='PSI-69_Experimental table_FLEX.csv', status='Bundled: team-supplied table; original PSI file identity pending independent check', rows=274),
 dict(study='BASS-II', id='PSI-25', family='Solid-fuel spread / airflow', doi='10.60555/4qc4-de67', file='PSI-25_Experimental table_BASS-II.csv', status='Official NASA PSI table not bundled; upload authentic export', rows=None),
 dict(study='Saffire-I', id='PSI-98', family='Large-scale spacecraft material fire', doi='10.60555/0t15-1z43', file='PSI-98_Experimental table_SAFFIRE-1.csv', status='Official NASA PSI table not bundled; upload authentic export', rows=None),
 dict(study='Saffire-II', id='PSI-99', family='Material comparison in microgravity', doi='', file='PSI-99_Experimental table_SAFFIRE-2.csv', status='Official NASA PSI table not bundled; upload authentic export', rows=None),
 dict(study='Saffire-III', id='PSI-100', family='Large-scale spacecraft material fire', doi='', file='PSI-100_Experimental table_SAFFIRE-3.csv', status='Official NASA PSI table not bundled; upload authentic export', rows=None),
 dict(study='SAME-R', id='PSI-101', family='Smoke aerosol / detection', doi='10.60555/2np7-jv14', file='PSI-101_Experimental table_SAME-R.csv', status='Official NASA PSI table not bundled; upload authentic export', rows=None),
 dict(study='SAME', id='PSI-102', family='Smoke aerosol / detection', doi='10.60555/gd4k-8h62', file='PSI-102_Experimental table_SAME.csv', status='Official NASA PSI table not bundled; upload authentic export', rows=None),
]


def psi_catalog():
    rows=[]
    for spec in PSI_STUDIES:
        rows.append({**spec, 'nasa_source':f'https://psi.nasa.gov/physci/repo/data/investigations/{spec["id"]}'})
    return pd.DataFrame(rows)


@dataclass
class SourceTable:
    study: str
    filename: str
    frame: pd.DataFrame
    sha256: str
    source_url: str
    raw_bytes: bytes

    def manifest(self):
        return dict(study=self.study, rows=len(self.frame), columns=len(self.frame.columns),
                    sha256=self.sha256, filename=self.filename, source_url=self.source_url,
                    provenance='User-uploaded CSV; source not independently authenticated')


def read_psi_csv(content: bytes, filename: str, study: str) -> SourceTable:
    catalog=psi_catalog().set_index('study')
    if study not in catalog.index:
        raise ValueError('Unrecognized NASA PSI investigation label.')
    if not str(filename).lower().endswith('.csv'):
        raise ValueError('Only experimental-table CSV files are accepted.')
    if not isinstance(content,bytes) or not (10<=len(content)<=15_000_000):
        raise ValueError('CSV must be a nonempty file no larger than 15 MB.')
    # A parser may decode legacy UTF-8 BOM or Latin-1 data; never overwrite the source bytes.
    last_error=None
    for encoding in ('utf-8-sig','latin-1'):
        try:
            frame=pd.read_csv(io.BytesIO(content),encoding=encoding,low_memory=False)
            break
        except (UnicodeError,pd.errors.ParserError) as exc:
            last_error=exc
    else:
        raise ValueError(f'Cannot parse CSV: {last_error}')
    if frame.empty or len(frame.columns)<2 or len(frame.columns)>250:
        raise ValueError('Expected an experimental table with at least one data row and two columns.')
    if len(frame)>100_000:
        raise ValueError('Unexpectedly large CSV; review before ingesting.')
    return SourceTable(study,str(filename),frame,hashlib.sha256(content).hexdigest(),
                       str(catalog.loc[study,'nasa_source']),content)


def numeric_cell(value):
    """Return numeric value only for a clearly numeric source cell.

    Returns (number, status). Tilde or comparison qualifiers are explicitly tagged and
    not cast to exact observations. No conversion of 'Complete', durations or narratives.
    """
    if pd.isna(value):return np.nan,'missing'
    if isinstance(value,(int,float,np.integer,np.floating)):
        return (float(value),'exact') if np.isfinite(value) else (np.nan,'missing')
    t=str(value).strip()
    if not t or t.lower() in {'n/a','na','none','nan','-','not reported'}:
        return np.nan,'missing'
    if re.match(r'^[~≈<>≤≥]',t) or re.search(r'\b(approx|about|roughly)\b',t,re.I):
        return np.nan,'qualified-not-exact'
    if re.fullmatch(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?\s*(?:%|mm|cm/s|ppm)?',t):
        return float(re.match(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?',t).group()),'exact'
    return np.nan,'unparsed'


def column_audit(table: SourceTable):
    """Per-column record coverage plus exact/qualified flags, without guessing a unit."""
    entries=[]
    for col in table.frame.columns:
        parsed=[numeric_cell(x) for x in table.frame[col]]
        statuses=pd.Series([s for _,s in parsed]).value_counts()
        entries.append(dict(column=col, nonmissing=int(table.frame[col].notna().sum()),
                            exact_numeric=int(statuses.get('exact',0)),
                            qualified=int(statuses.get('qualified-not-exact',0)),
                            unparsed=int(statuses.get('unparsed',0)),
                            dtype=str(table.frame[col].dtype)))
    return pd.DataFrame(entries)


def measurement_view(table: SourceTable, column: str):
    """Single native column. Never pool values from different investigations."""
    if column not in table.frame.columns:raise ValueError('Unknown source column.')
    parsed=[numeric_cell(v) for v in table.frame[column]]
    return pd.DataFrame({'source_row':range(1,len(parsed)+1),
                         'original_value':table.frame[column].astype('string'),
                         'value':[v for v,_ in parsed],
                         'parse_status':[s for _,s in parsed]})


def source_coverage(tables):
    """Accept dict[str, SourceTable] and report status without implying NASA authentication."""
    result=psi_catalog().copy()
    result['loaded_in_session']=result.study.map(lambda s:s=='FLEX' or s in tables)
    result['session_rows']=result.study.map(lambda s:len(tables[s].frame) if s in tables else (274 if s=='FLEX' else 0))
    result['coverage_note']=result.study.map(lambda s:'Team-provided CSV bundled' if s=='FLEX' else
                                               'User upload, provenance unverified' if s in tables else 'NASA metadata only')
    return result


def study_data_answer(question: str, tables):
    """Narrow deterministic Q&A for *uploaded* observation files. No invented measurements."""
    q=question.lower()
    target=next((study for study in sorted(tables,key=len,reverse=True) if study.lower() in q),None)
    if target is None:return None
    item=tables[target]
    if re.search(r'\b(count|how many|number of|rows|records|observations|tests)\b',q):
        return (f'**OBSERVED · Session CSV inventory:** The uploaded **{target}** file has '
                f'**{len(item.frame)} rows** and **{len(item.frame.columns)} columns**. '
                f'This is a count of CSV rows, not automatically a count of distinct experimental tests. '
                f'Source-file SHA-256: `{item.sha256}`. The upload is not independently NASA-authenticated. '
                f'[NASA investigation]({item.source_url}).')
    return (f'**OBSERVED · {target} session data available.** This upload contains '
            f'{len(item.frame)} source rows. Choose a column in **NASA data lab** to inspect its exact numerical values '
            f'and qualifiers; I cannot infer its physical unit or reconstruct missing measurements. '
            f'[NASA investigation]({item.source_url}).')
