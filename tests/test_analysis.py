import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
import pytest
import matplotlib.pyplot as plt
from analysis import ROOT, BANDS, clean_data, read_raw, load_roundtrip, summary, filter_data, narrative, chart, correlations, digest

@pytest.fixture
def raw():
    return read_raw(ROOT / 'examples/synthetic_fixture.csv')

@pytest.fixture
def data(raw):
    return clean_data(raw)[0]

def test_etl(raw):
    before = raw.copy(deep=True)
    clean, rejected, audit = clean_data(raw)
    pd.testing.assert_frame_equal(raw, before)
    assert (len(raw), len(clean), len(rejected)) == (51, 50, 1)
    assert audit['cleaned_match_excess_retained'] == 1
    assert clean.charges.max() == 70000
    assert 'charges_rule' in rejected.reason.iloc[0]
    assert clean.isna().sum().sum() == 0

def test_roundtrip(data, tmp_path):
    loaded = load_roundtrip(data, tmp_path/'clean.csv')
    assert np.isclose(loaded.charges.sum(), data.charges.sum())

def test_group_reconciliation(data):
    for group in ['region', 'smoker', ['region','smoker']]:
        s = summary(data, group)
        assert s.n.sum() == len(data)
        assert np.isclose(np.average(s['mean'], weights=s.n), data.charges.mean())
    yes = data.loc[data.smoker.eq('yes'), 'charges'].tolist()
    assert np.isclose(sum(yes)/len(yes), summary(data,'smoker').set_index('smoker').loc['yes','mean'])

def test_filters(data):
    subset = filter_data(data, BANDS, ['yes'], ['northeast'])
    assert len(subset) > 0 and subset.smoker.eq('yes').all() and subset.region.eq('northeast').all()
    assert len(filter_data(data, [], ['yes'], ['northeast'])) == 0
    assert 'No records' in narrative(subset.iloc[:0])
    assert 'Only one smoking group' in narrative(subset)
    assert f'{len(data):,} records' in narrative(data)

def test_age_boundaries(raw):
    df = pd.concat([raw.iloc[[0]]]*5, ignore_index=True)
    df['age'] = [18,30,40,50,60]
    assert list(clean_data(df)[0].age_band) == BANDS

def test_schema(raw):
    with pytest.raises(ValueError): clean_data(raw.drop(columns='charges'))

def test_nonfinite(raw):
    df=raw.copy(); df.loc[0,'charges']=np.inf
    assert len(clean_data(df)[1]) == 2

def test_charts(data):
    for kind in ['histogram','smoking','age','bmi','region','stratified','heatmap']:
        fig=chart(data,kind); fig.canvas.draw(); assert fig.axes[0].get_title(); plt.close(fig)
    assert len(correlations(data)) == 3

def test_missing_file(tmp_path):
    with pytest.raises(ValueError, match='Cannot read'): read_raw(tmp_path/'missing.csv')

def test_raw_hash(raw):
    path=ROOT/'examples/synthetic_fixture.csv'; old=digest(path); clean_data(raw); assert digest(path)==old

def test_single_group_charts(data):
    one = filter_data(data, BANDS, ['yes'], ['northeast'])
    for kind in ['histogram','smoking','age','bmi','region','stratified','heatmap']:
        fig = chart(one, kind)
        fig.canvas.draw()
        plt.close(fig)


def test_narrative_values(data):
    text = narrative(data)
    assert f'{data.charges.mean():,.2f}' in text
    assert f'{data.charges.median():,.2f}' in text
    assert f'{data.age.corr(data.charges):.3f}' in text
    assert f'{data.bmi.corr(data.charges):.3f}' in text
    assert f'{summary(data,"region")["median"].max():,.2f}' in text
