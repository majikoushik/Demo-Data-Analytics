"""Shared, deterministic ETL and analysis for the notebook and dashboard."""
from pathlib import Path
import hashlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/insurance.csv'
CLEAN = ROOT / 'data/cleaned/insurance_cleaned.csv'
FIELDS = ['age', 'sex', 'bmi', 'children', 'smoker', 'region', 'charges']
NUMERIC = ['age', 'bmi', 'children', 'charges']
CATEGORIES = {'sex': ['female', 'male'], 'smoker': ['no', 'yes'],
              'region': ['northeast', 'northwest', 'southeast', 'southwest']}
BANDS = ['18–29', '30–39', '40–49', '50–59', '60+']
COLORS = {'no': '#277D86', 'yes': '#BD613A'}


def read_raw(path=RAW):
    """Read source without writing to it; fail with an actionable message."""
    try:
        return pd.read_csv(path)
    except (OSError, pd.errors.ParserError, UnicodeError, pd.errors.EmptyDataError) as exc:
        raise ValueError(f'Cannot read {path}. Download the assigned CSV and check its format.') from exc


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def profile(df):
    return pd.DataFrame({'dtype': df.dtypes.astype(str), 'missing': df.isna().sum(),
                         'distinct_non_null': df.nunique()})


def clean_data(raw):
    """Normalize labels, validate records, quarantine invalid rows, retain matches."""
    df = raw.copy(deep=True)
    names = df.columns.str.strip().str.lower()
    if names.duplicated().any() or set(names) != set(FIELDS):
        raise ValueError(f'Unexpected schema: {list(df.columns)}; expected {FIELDS}')
    df.columns = names
    df = df[FIELDS].copy()
    changed = {}
    for col in CATEGORIES:
        old = df[col].astype('string')
        df[col] = old.str.strip().str.lower()
        changed[col] = int(old.ne(df[col]).fillna(False).sum())
    for col in NUMERIC:
        old = df[col]
        df[col] = pd.to_numeric(old, errors='coerce')
        changed[col + '_new_nulls'] = int((old.notna() & df[col].isna()).sum())
    flags = pd.DataFrame(index=df.index)
    for col in NUMERIC:
        flags[col + '_nonfinite'] = ~np.isfinite(df[col].astype(float))
    flags['age_rule'] = ~df.age.between(18, 120) | (df.age % 1 != 0)
    flags['bmi_rule'] = ~(df.bmi > 0)
    flags['children_rule'] = ~(df.children >= 0) | (df.children % 1 != 0)
    flags['charges_rule'] = ~(df.charges >= 0)
    for col, allowed in CATEGORIES.items():
        flags[col + '_category'] = ~df[col].isin(allowed)
    invalid = flags.any(axis=1)
    rejected = raw.loc[invalid].copy()
    rejected.insert(0, 'source_row', np.flatnonzero(invalid) + 2)
    if invalid.any():
        rejected['reason'] = flags.loc[invalid].apply(lambda r: '; '.join(r.index[r]), axis=1)
    else:
        rejected['reason'] = pd.Series(dtype=str)
    cleaned = df.loc[~invalid].copy().reset_index(drop=True)
    if cleaned.empty:
        raise ValueError('No valid records remain; investigate source and validation rules.')
    cleaned = cleaned.astype({'age': 'int64', 'children': 'int64', 'bmi': 'float64', 'charges': 'float64'})
    cleaned['age_band'] = pd.cut(cleaned.age, [18, 30, 40, 50, 60, np.inf],
                                 labels=BANDS, right=False).astype('string')
    # Tukey fences flag unusual observations, not invalid observations.
    q1, q3 = cleaned.charges.quantile([.25, .75])
    iqr = q3 - q1
    outliers = (cleaned.charges < q1 - 1.5 * iqr) | (cleaned.charges > q3 + 1.5 * iqr)
    audit = {'raw_rows': len(raw), 'cleaned_rows': len(cleaned), 'excluded_rows': len(rejected),
             'raw_exact_repeat_excess': int(raw.duplicated().sum()),
             'cleaned_match_excess_retained': int(cleaned[FIELDS].duplicated().sum()),
             'charge_iqr_flags_retained': int(outliers.sum()),
             'bmi_review_flags_retained': int((~cleaned.bmi.between(10, 80)).sum()),
             **changed, **{f'flag_{k}': int(v) for k, v in flags.sum().items()}}
    assert len(raw) == len(cleaned) + len(rejected)
    return cleaned, rejected, audit


def load_roundtrip(cleaned, path=CLEAN):
    path.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(path, index=False)
    loaded = pd.read_csv(path, dtype={col: 'string' for col in [*CATEGORIES, 'age_band']})
    pd.testing.assert_frame_equal(cleaned, loaded, check_exact=False, rtol=1e-12)
    return loaded


def summary(df, groups):
    """Group counts include repeated rows; standard deviation is sample SD."""
    return (df.groupby(groups, observed=True, sort=True)['charges']
            .agg(n='size', mean='mean', median='median', sd='std', minimum='min', maximum='max')
            .reset_index())


def filter_data(df, ages, smokers, regions):
    return df.loc[df.age_band.isin(ages) & df.smoker.isin(smokers) & df.region.isin(regions)].copy()


def correlations(df):
    return pd.concat([pd.DataFrame([{'group': 'all', 'n': len(df),
                                    'age_r': df.age.corr(df.charges), 'bmi_r': df.bmi.corr(df.charges)}]),
                      pd.DataFrame([{'group': k, 'n': len(g), 'age_r': g.age.corr(g.charges),
                                     'bmi_r': g.bmi.corr(g.charges)} for k, g in df.groupby('smoker')])],
                     ignore_index=True)


def narrative(df, unit='source charge units'):
    """AI-assisted wording; numeric claims calculated, not hard-coded."""
    if df.empty:
        return 'No records match these filters. Expand the selection.'
    text = [f'This selection contains {len(df):,} records. Mean charges are {df.charges.mean():,.2f} '
            f'and median charges are {df.charges.median():,.2f} ({unit}).']
    s = summary(df, 'smoker').set_index('smoker')
    if {'yes', 'no'}.issubset(s.index):
        diff = s.loc['yes', 'mean'] - s.loc['no', 'mean']
        text.append(f'Mean recorded charges for smokers ({int(s.loc["yes", "n"])} records) minus '
                    f'non-smokers ({int(s.loc["no", "n"])} records) equal {diff:,.2f} {unit}. '
                    'This is an observed difference, not a causal effect.')
    else:
        text.append('Only one smoking group is present; no between-group comparison is possible.')
    age_r = df.age.corr(df.charges) if len(df) > 1 else np.nan
    bmi_r = df.bmi.corr(df.charges) if len(df) > 1 else np.nan
    if np.isfinite(age_r) and np.isfinite(bmi_r):
        text.append(f'Age and BMI have Pearson correlations with charges of {age_r:.3f} '
                    f'and {bmi_r:.3f}, respectively. Review smoking-specific results and scatter plots '
                    'before interpreting these linear associations.')
    else:
        text.append('One or more correlations are undefined in this selection; more variation is needed.')
    r = summary(df, 'region').sort_values('median', ascending=False)
    if len(r) > 1:
        text.append(f'The highest regional median is {r.iloc[0]["region"]} ({r.iloc[0]["median"]:,.2f}); '
                    'compare within smoking groups before interpreting regional differences.')
        strata = summary(df, ['region', 'smoker'])
        spreads = []
        for key, group in strata.groupby('smoker'):
            if len(group) > 1:
                spreads.append(f'{key}: {group["median"].max()-group["median"].min():,.2f}')
        if spreads:
            text.append('Within-smoking-group regional median ranges (' + unit + ') are: '
                        + '; '.join(spreads) + '. These are unadjusted descriptive contrasts.')
    text.append('Use these summaries for aggregate planning and further investigation, not individual pricing. '
                'Dates, clinical history and coverage detail are unavailable in the expected schema.')
    return '\n\n'.join(text)


def chart(df, kind, unit='source charge units'):
    """Return labelled Matplotlib figures for the same validated selection."""
    fig, ax = plt.subplots(figsize=(8.5, 4.5), layout='constrained')
    if df.empty:
        ax.text(.5, .5, 'No matching records', ha='center'); ax.set_axis_off(); return fig
    charge_label = f'Recorded charges ({unit})'
    if kind == 'histogram':
        ax.hist(df.charges, bins=30, color='#277D86', edgecolor='white')
        for label, value, color in [('Mean', df.charges.mean(), '#BD613A'), ('Median', df.charges.median(), '#233A56')]:
            ax.axvline(value, label=label, color=color, linestyle='--')
        ax.set(xlabel=charge_label, ylabel='Number of records', title='Distribution of recorded charges'); ax.legend()
    elif kind == 'smoking':
        groups = list(df.groupby('smoker', sort=True))
        bp = ax.boxplot([g.charges for _, g in groups], patch_artist=True)
        ax.set_xticks(range(1, len(groups)+1), [f'{k} (n={len(g)})' for k, g in groups])
        for patch, (key, _) in zip(bp['boxes'], groups): patch.set_facecolor(COLORS[key])
        ax.set(xlabel='Smoking status (yes/no)', ylabel=charge_label, title='Charges by smoking status')
    elif kind == 'region':
        s = summary(df, 'region'); x = np.arange(len(s))
        ax.bar(x-.18, s['mean'], .36, label='Mean', color='#277D86')
        ax.bar(x+.18, s['median'], .36, label='Median', color='#BD613A')
        ax.set_xticks(x, [f'{k}\n(n={n})' for k, n in zip(s.region, s.n)])
        ax.set(ylabel=charge_label, title='Regional comparison'); ax.legend()
    elif kind in ('age', 'bmi'):
        for key, g in df.groupby('smoker'):
            ax.scatter(g[kind], g.charges, s=18, alpha=.55, label=f'{key} (n={len(g)})', color=COLORS[key])
        ax.set(xlabel='Age (years, expected)' if kind == 'age' else 'BMI (kg/m², expected)', ylabel=charge_label,
               title=f'{kind.upper() if kind == "bmi" else "Age"} versus recorded charges'); ax.legend()
    elif kind == 'heatmap':
        c = df[NUMERIC].corr(); image = ax.imshow(c, vmin=-1, vmax=1, cmap='coolwarm')
        ax.set_xticks(range(len(c)), c.columns); ax.set_yticks(range(len(c)), c.index)
        for i in range(len(c)):
            for j in range(len(c)): ax.text(j, i, f'{c.iloc[i,j]:.2f}', ha='center', va='center')
        fig.colorbar(image, ax=ax, label='Pearson r'); ax.set_title('Numeric correlations only')
    elif kind == 'stratified':
        s = summary(df, ['region', 'smoker']); regions = sorted(df.region.unique()); x = np.arange(len(regions))
        for offset, key in [(-.18, 'no'), (.18, 'yes')]:
            group = s.loc[s.smoker == key].set_index('region').reindex(regions)
            bars = ax.bar(x+offset, group['median'], .36, label=key, color=COLORS[key])
            for bar, n in zip(bars, group.n):
                if pd.notna(n): ax.annotate(f'n={int(n)}', (bar.get_x()+bar.get_width()/2, bar.get_height()), ha='center', va='bottom', fontsize=8)
        ax.set_xticks(x, regions); ax.set(ylabel=charge_label, title='Regional median within smoking groups'); ax.legend()
        ax.margins(y=.18)
    else:
        plt.close(fig); raise ValueError(f'Unknown chart: {kind}')
    if kind != 'heatmap': ax.grid(axis='y', alpha=.18); ax.set_axisbelow(True)
    return fig


def read_cleaned(path=CLEAN):
    """Read the notebook output and revalidate schema, rows and feature values."""
    loaded = pd.read_csv(path, dtype={col: 'string' for col in [*CATEGORIES, 'age_band']})
    if list(loaded.columns) != FIELDS + ['age_band']:
        raise ValueError('Cleaned CSV has an unexpected schema.')
    expected, rejected, _ = clean_data(loaded[FIELDS])
    if not rejected.empty:
        raise ValueError('Cleaned CSV contains invalid rows.')
    pd.testing.assert_frame_equal(expected, loaded, check_exact=False, rtol=1e-12)
    return loaded
