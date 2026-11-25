"""Generate fictional rows for software verification only, never submission results."""
from pathlib import Path
import pandas as pd

rows = []
for i in range(48):
    age = 18 + (i * 7) % 47
    bmi = 19 + (i * 3.17) % 22
    smoker = 'yes' if i % 5 in (0, 1) else 'no'
    region = ['northeast', 'northwest', 'southeast', 'southwest'][i % 4]
    charges = round(850 + 95 * age + 33 * bmi + (9000 if smoker == 'yes' else 0) + (i % 7) * 137, 2)
    rows.append([age, ['female', 'male'][i % 2], round(bmi, 2), i % 4, smoker, region, charges])
rows.append(rows[0].copy())  # matching row deliberately retained
rows.append([40, ' female ', 27, 1, ' YES ', 'NORTHEAST', 70000])  # valid extreme
rows.append([40, 'female', 27, 1, 'unknown', 'northeast', -5])  # invalid
out = Path(__file__).resolve().parent / 'synthetic_fixture.csv'
pd.DataFrame(rows, columns=['age','sex','bmi','children','smoker','region','charges']).to_csv(out, index=False)
print(out)
