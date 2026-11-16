"""Provenance and source-integrity tests for multi-investigation raw data lab."""
import pytest
import numpy as np
import pandas as pd
from modules.psi_lab import (psi_catalog, read_psi_csv, numeric_cell,
    column_audit, measurement_view, study_data_answer, source_coverage)


def example():
    csv=b'Test #,Calibrated initial O2 % by vol,Final CO2 % by vol\nB1,22.2,0.44\nB2,~22.1,n/a\nB3,22.2,0.51\n'
    return read_psi_csv(csv,'PSI-25_Experimental table_BASS-II.csv','BASS-II')


def test_sources_primary_nasa():
    sources=psi_catalog()
    assert len(sources)==7
    assert sources.nasa_source.str.startswith('https://psi.nasa.gov/').all()
    assert len(sources[sources.study=='FLEX'])==1


def test_source_bytes_preserved_and_auditable():
    src=example()
    assert src.raw_bytes.startswith(b'Test #,')
    assert src.sha256==__import__('hashlib').sha256(src.raw_bytes).hexdigest()
    assert len(src.frame)==3
    assert src.manifest()['provenance'].startswith('User-uploaded')


def test_qualified_values_are_not_fabricated_exact_numbers():
    assert numeric_cell('~22.1')[1]=='qualified-not-exact'
    assert numeric_cell('<0.5')[1]=='qualified-not-exact'
    assert numeric_cell('Complete')[1]=='unparsed'
    assert numeric_cell('22.2 %')==(22.2,'exact')
    assert numeric_cell('n/a')[1]=='missing'


def test_numeric_audit_source_rows_preserved():
    src=example()
    table=measurement_view(src,'Calibrated initial O2 % by vol')
    assert len(table)==3
    assert table.parse_status.tolist()==['exact','qualified-not-exact','exact']
    assert table.value.notna().sum()==2
    assert table.source_row.tolist()==[1,2,3]
    audit=column_audit(src)
    oxygen=audit[audit.column=='Calibrated initial O2 % by vol'].iloc[0]
    assert oxygen.exact_numeric==2 and oxygen.qualified==1


def test_different_studies_not_pooled_or_auto_authenticated():
    src=example()
    coverage=source_coverage({'BASS-II':src})
    assert coverage.loc[coverage.study=='BASS-II','session_rows'].iloc[0]==3
    assert coverage.loc[coverage.study=='Saffire-II','session_rows'].iloc[0]==0
    assert 'unverified' in coverage.loc[coverage.study=='BASS-II','coverage_note'].iloc[0]


def test_refuses_invalid_source_or_non_csv():
    with pytest.raises(ValueError):read_psi_csv(b'a,b\n1,2\n','bad.csv','Not NASA')
    with pytest.raises(ValueError):read_psi_csv(b'a,b\n1,2\n','bad.txt','BASS-II')


def test_source_qa_counts_rows_not_experiments():
    reply=study_data_answer('How many BASS-II observations?',{'BASS-II':example()})
    assert '3 rows' in reply and 'not automatically a count' in reply
    assert study_data_answer('How many Saffire-II records?',{'BASS-II':example()}) is None
