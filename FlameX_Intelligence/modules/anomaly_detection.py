import pandas as pd
import numpy as np
from .data_loader import composition_diagnostics

def audit_flags(df,residuals=None):
    """Flag for inspection, not deletion or correction."""
    flags=[]
    def push(id_,reason,observed,priority='Review'):
        flags.append({'Record':str(id_),'Reason':reason,'Observed':str(observed),'Status':'Flagged, not proven erroneous','Priority':priority})
    sums=composition_diagnostics(df)
    for i,row in df.iterrows():
        rid=row['record_id']
        if pd.notna(row['pressure']) and row['pressure']<=0:push(rid,'Nonpositive pressure',row['pressure'],'High')
        if pd.notna(sums.loc[i]) and abs(sums.loc[i]-1)>.011:push(rid,'Gas fractions do not sum to ~1',round(float(sums.loc[i]),4))
        if pd.notna(row['diameter']) and row['diameter']<=0:push(rid,'Nonpositive initial diameter',row['diameter'])
        if pd.notna(row['extinction_diameter']) and row['extinction_diameter']==0:push(rid,'Zero visible extinction diameter (interpretation uncertain)',row['extinction_diameter'])
    if residuals is not None and not residuals.empty:
        for _,row in residuals[residuals['flag_cooks']].iterrows():
            push(row['record_id'],'Cook’s distance > 4/n within fuel',round(float(row['cooks_d']),4))
    if 'identifier' in df:
        duplicates=df[df['identifier'].duplicated(keep=False) & df['identifier'].notna()]
        for _,row in duplicates.iterrows():push(row['record_id'],'Repeated FLEX Identifier (test numbers distinct)',row['identifier'])
    return pd.DataFrame(flags,columns=['Record','Reason','Observed','Status','Priority'])
