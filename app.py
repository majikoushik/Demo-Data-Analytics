"""Streamlit dashboard: launch from the project root."""
import json
import streamlit as st
import matplotlib.pyplot as plt
from analysis import ROOT, RAW, CLEAN, BANDS, read_cleaned, digest, filter_data, summary, chart, correlations, narrative

st.set_page_config(page_title='Healthcare Insurance | Cost Analysis', page_icon='📊', layout='wide')
st.title('Healthcare insurance | Recorded charge analysis')
st.caption('Planning intelligence • Descriptive evidence, not causal or individual pricing advice')

@st.cache_data
def prepare(path, modified):
    return read_cleaned(path)

meta_path = ROOT / 'data/source_metadata.json'
if not CLEAN.exists() or not meta_path.exists():
    st.error('Cleaned data and source metadata are required. Follow README.md; synthetic examples are not used here.')
    st.stop()
try:
    metadata = json.loads(meta_path.read_text(encoding='utf-8'))
    if metadata.get('source_url') != 'https://www.kaggle.com/datasets/willianoliveiragibin/healthcare-insurance' or metadata.get('permission_confirmed') is not True or any(not metadata.get(k) for k in ['original_filename','download_date','description','license_or_permission','currency_or_units','coverage']):
        raise ValueError('Complete verified source metadata and confirm permission first.')
    if metadata.get('cleaned_sha256') != digest(CLEAN):
        raise ValueError('Cleaned CSV hash does not match the notebook output; rerun the notebook.')
    df = prepare(str(CLEAN), CLEAN.stat().st_mtime_ns)
except (ValueError, OSError, AssertionError) as exc:
    st.error(str(exc)); st.stop()
unit = metadata['currency_or_units']
st.sidebar.header('Filter records')
ages = st.sidebar.multiselect('Age bands', [b for b in BANDS if b in set(df.age_band)], default=[b for b in BANDS if b in set(df.age_band)])
smokers = st.sidebar.multiselect('Smoking status', sorted(df.smoker.unique()), default=sorted(df.smoker.unique()))
regions = st.sidebar.multiselect('Region', sorted(df.region.unique()), default=sorted(df.region.unique()))
view = filter_data(df, ages, smokers, regions)
st.caption(f'{len(view):,} of {len(df):,} validated records • Units: {unit}')
if view.empty:
    st.warning('No records match these filters. Select at least one value in each control.'); st.stop()
cols = st.columns(4)
cols[0].metric('Records', f'{len(view):,}')
cols[1].metric('Mean charges', f'{view.charges.mean():,.2f}')
cols[2].metric('Median charges', f'{view.charges.median():,.2f}')
cols[3].metric('Smoker share', f'{view.smoker.eq("yes").mean():.1%}')
with st.expander('Management summary', expanded=True):
    st.markdown(narrative(view, unit))
tabs = st.tabs(['Overview & smoking', 'Age & BMI', 'Regional analysis', 'Methods & limitations'])

def show(kind):
    fig = chart(view, kind, unit)
    st.pyplot(fig); plt.close(fig)

with tabs[0]:
    left, right = st.columns(2)
    with left: show('histogram')
    with right: show('smoking')
    st.dataframe(summary(view, 'smoker'), hide_index=True)
    st.caption('Mean reflects total expense per record; median describes a typical record. Boxplot points are not automatically errors.')
with tabs[1]:
    left, right = st.columns(2)
    with left: show('age')
    with right: show('bmi')
    st.dataframe(correlations(view), hide_index=True)
    show('heatmap')
    st.caption('Pearson r measures linear association. Smoking-stratified values help expose different patterns; small or constant groups can produce undefined r.')
with tabs[2]:
    show('region'); st.dataframe(summary(view, 'region'), hide_index=True)
    show('stratified'); st.dataframe(summary(view, ['region','smoker']), hide_index=True)
    st.caption('Region labels are categories, not coordinates. Smoking composition can influence overall regional means.')
with tabs[3]:
    st.markdown('Data are secondary, with no unique person identifier. Matching valid rows and valid high charges are retained. Invalid records are quarantined; no imputation is used. No causal, temporal or individual pricing inference is supported.')
    st.write('Source:', metadata['source_url']); st.write('Coverage:', metadata['coverage'])
    st.write('AI assistance: ChatGPT contributed to code and narrative wording; numerical statements are computed from the selection.')
