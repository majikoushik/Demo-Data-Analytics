"""Run with Streamlit installed. Fixtures are fictional and isolated from project data."""
import json
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import analysis as a

streamlit = pytest.importorskip('streamlit', reason='Streamlit not installed in this test environment')
from streamlit.testing.v1 import AppTest


def test_dashboard_filters(monkeypatch, tmp_path):
    original = a.ROOT
    cleaned = a.clean_data(a.read_raw(original/'examples/synthetic_fixture.csv'))[0]
    clean_path = tmp_path/'data/cleaned/insurance_cleaned.csv'
    a.load_roundtrip(cleaned, clean_path)
    metadata = {'source_url':'https://www.kaggle.com/datasets/willianoliveiragibin/healthcare-insurance',
                'original_filename':'synthetic test fixture only', 'download_date':'synthetic test',
                'description':'software test only', 'license_or_permission':'local synthetic test',
                'permission_confirmed': True, 'currency_or_units':'fictional units', 'coverage':'synthetic',
                'cleaned_sha256':a.digest(clean_path)}
    (tmp_path/'data/source_metadata.json').write_text(json.dumps(metadata))
    monkeypatch.setattr(a,'ROOT',tmp_path)
    monkeypatch.setattr(a,'CLEAN',clean_path)
    at = AppTest.from_file(str(original/'app.py'), default_timeout=40).run()
    assert not at.exception
    assert at.metric[0].value == str(len(cleaned))
    at.sidebar.multiselect[1].set_value(['yes']).run()
    assert not at.exception
    assert at.metric[0].value == str(cleaned.smoker.eq('yes').sum())
    at.sidebar.multiselect[2].set_value(['northeast']).run()
    assert not at.exception
    assert at.metric[0].value == str((cleaned.smoker.eq('yes') & cleaned.region.eq('northeast')).sum())
    at.sidebar.multiselect[0].set_value([]).run()
    assert not at.exception
    assert any('No records' in w.value for w in at.warning)
