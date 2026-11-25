# Criterion 2.2 — Code review and testing

Actual improvements observed during development on the synthetic fixture:

| Issue | Before | After | Validation |
|---|---|---|---|
| Reload lost string dtypes | `pd.read_csv(path, dtype={'age_band': 'string'})` | `pd.read_csv(path, dtype={col: 'string' for col in [*CATEGORIES, 'age_band']})` | `test_roundtrip` initially failed, then checks frame equality and charge totals. |
| Empty rejection set caused an exception | `rejected['reason'] = flags.loc[invalid].apply(..., axis=1)` always executed | only run apply when `invalid.any()`, otherwise initialize an empty Series | `test_age_boundaries` initially failed; revised test exercises all-valid data. |
| Risk of wrong group aggregation | unweighted average of regional means (illustrative anti-pattern, not used in production) | `np.average(s['mean'], weights=s.n)` | `test_group_reconciliation` independently reconciles counts and overall mean. |

Manual review: descriptive functions and docstrings; reusable `summary`, `chart`, `narrative` and `filter_data` prevent notebook/dashboard divergence; explicit data types and schema checks; pathlib makes file paths relative to the project; exceptions provide context. PEP8 review was manual, not an automated linter. Some compact lines exceed 79 characters, so style is not claimed fully compliant. No speed improvement claimed because it was not benchmarked. Tests use fictional input only; see actual console output in `test_results.txt` and run again with your environment. Review Git history after creating repository; suggested commits in README are not proof of actual learner commits.
