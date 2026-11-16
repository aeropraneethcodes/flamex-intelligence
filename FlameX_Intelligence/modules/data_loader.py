"""Immutable experiment-table loading and explicit, auditable views."""
import hashlib
import io
from pathlib import Path
import numpy as np
import pandas as pd

FIELD_MAP = {
    'id': 'FLEX Test #', 'identifier': 'FLEX Identifier', 'date': 'Test Date', 'time': 'Test GMT',
    'fuel': 'Fuel', 'pressure': 'Ambient pressure; mmHg',
    'oxygen': 'O initial ambient composition; mole fraction',
    'nitrogen': 'N initial ambient composition; mole fraction',
    'co': 'CO initial ambient composition; mole fraction',
    'helium': 'He initial ambient composition; mole fraction',
    'diameter': 'Droplet initial diameter; mm',
    'extinction_diameter': 'Visible flame extinction diameter; mm',
    'burn': 'Burning rate; mm', 'burntime': 'Burn time; s', 'outcome': 'Test end',
}
NUMERIC = ['id','pressure','oxygen','nitrogen','co','helium','diameter','extinction_diameter','burn','burntime']
CATEGORICAL = ['fuel','outcome']
PSI_FLEX = 'https://psi.nasa.gov/physci/repo/data/investigations/PSI-69'


def fingerprint(data: bytes):
    return hashlib.sha256(data).hexdigest()


def read_raw(source):
    if isinstance(source, bytes):
        b = source
    elif hasattr(source, 'getvalue'):
        b = source.getvalue()
    else:
        b = Path(source).read_bytes()
    raw = pd.read_csv(io.BytesIO(b))
    if len(raw) == 0:
        raise ValueError('The uploaded CSV is empty.')
    return raw, fingerprint(b)


def suggest_mapping(cols):
    def token(s):
        return ''.join(z.lower() for z in str(s) if z.isalnum())
    by_norm = {token(c):c for c in cols}
    suggestions = {}
    for key, literal in FIELD_MAP.items():
        suggestions[key] = by_norm.get(token(literal))
    return suggestions


def normalized_view(raw, mapping=None):
    """Return derived view and a cleaning audit; never mutate or drop source rows."""
    mapping = mapping or suggest_mapping(raw.columns)
    needed = ['id','fuel','outcome','oxygen','pressure','burn','diameter','burntime']
    missing = [k for k in needed if not mapping.get(k) or mapping[k] not in raw.columns]
    if missing:
        raise ValueError('Missing required mappings: '+', '.join(missing))
    df = pd.DataFrame(index=raw.index)
    audit = [{'step':'SOURCE','detail':f'{len(raw)} rows; {len(raw.columns)} columns retained verbatim in raw.csv', 'affected_rows':len(raw)}]
    for key, col in mapping.items():
        if not col or col not in raw.columns:
            continue
        if key in NUMERIC:
            before = raw[col].notna().sum()
            df[key] = pd.to_numeric(raw[col], errors='coerce')
            new_missing = int(before-df[key].notna().sum())
            audit.append({'step':'NUMERIC_PARSE','detail':f'{col} -> {key}; invalid values become NaN, no rows removed', 'affected_rows':new_missing})
        elif key in CATEGORICAL:
            df[key] = raw[col].astype('string').str.strip()
            audit.append({'step':'CATEGORY_TRIM','detail':f'{col} -> {key}; trimmed whitespace, no categories merged', 'affected_rows':0})
        else:
            df[key] = raw[col]
    df['source_row'] = np.arange(1,len(raw)+1)
    df['record_id'] = df['id'].apply(lambda z: f'FLEX-{int(z):03}' if pd.notna(z) else 'FLEX-UNKNOWN')
    audit.append({'step':'DERIVED_IDENTIFIERS','detail':'Assigned source-row index and FLEX record key; original identifiers unchanged','affected_rows':len(raw)})
    audit.append({'step':'NO_ROW_DROPS','detail':'No rows deleted, interpolated, or imputed; missing entries remain missing','affected_rows':0})
    return df, pd.DataFrame(audit)


def filtered(df, fuels=None, outcomes=None, oxygen=None, pressure=None):
    mask = pd.Series(True,index=df.index)
    if fuels is not None: mask &= df['fuel'].isin(fuels)
    if outcomes is not None: mask &= df['outcome'].isin(outcomes)
    if oxygen is not None: mask &= df['oxygen'].between(*oxygen)
    if pressure is not None: mask &= df['pressure'].between(*pressure)
    return df.loc[mask].copy()


def completeness(df):
    return pd.DataFrame({
        'Field':df.columns,
        'Present': [int(df[c].notna().sum()) for c in df],
        'Missing': [int(df[c].isna().sum()) for c in df],
        'Coverage (%)':[round(100*df[c].notna().mean(),1) for c in df],
    })


def composition_diagnostics(df):
    species = [x for x in ('oxygen','nitrogen','co','helium') if x in df]
    if len(species) != 4: return pd.Series(np.nan,index=df.index)
    return df[species].sum(axis=1,min_count=4)


def pressure_to_psi(mm_hg):
    return float(mm_hg) * 14.6959488 / 760.0


def psi_to_pressure(psi):
    return float(psi)*760.0/14.6959488
