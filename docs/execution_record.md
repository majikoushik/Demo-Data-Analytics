# Preparation-environment verification
- Python 3.13.5; pandas 2.2.3; NumPy 2.3.5; Matplotlib 3.10.8; nbformat 5.10.4; nbclient 0.10.4.
- `python -m pytest -q --disable-warnings`: see `test_results.txt` (12 passed, one Streamlit-dependent test skipped).
- `python -m compileall -q analysis.py app.py tests`: completed without syntax errors.
- Separate synthetic notebook executed in a fresh kernel: 12 code cells, seven PNG charts, zero notebook error outputs.
- Synthetic input: 51 fictional records, one invalid excluded, 50 retained, including a matching row and a valid high charge. These are deliberately generated software test scenarios, not dataset statistics.
- Not verified: actual Kaggle source bytes, licence, source-dependent numbers, Streamlit runtime/hosted deployment, GitHub assessor access. Do not treat them as completed.
