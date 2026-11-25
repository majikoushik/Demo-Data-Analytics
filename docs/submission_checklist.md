# Submission and verification record — learner to complete

The following is a checklist, not a claim that these actions have already been performed. The included test output covers the fictional fixture only. Complete the real-data checks yourself and record actual evidence.

| Check | Evidence to capture | Status |
|---|---|---|
| Source downloaded | exact Kaggle URL, filename, date, licence/permission, units, coverage | Pending |
| Real notebook Run All | saved outputs and no errors | Pending |
| Data checks | raw/cleaned counts, exclusions, matching rows, raw SHA-256 | Pending |
| Calculations | reconcile group counts and means, check sample arithmetic | Pending |
| Narrative | compare each number, correlation and regional spread with notebook | Pending |
| Core tests | actual pytest output | Pending real environment |
| UI all filters default | KPIs agree with notebook; charts display | Pending |
| UI smoker selection | count and mean match pandas filtered data | Pending |
| UI region and age selection | combined subset matches notebook | Pending |
| UI one group | no unsupported two-group comparison | Pending |
| UI empty selection | warning, no misleading KPI | Pending |
| UI reset to defaults | original counts/KPIs restored | Pending |
| Git history | review meaningful commits; capture log and explain version-control approach | Pending learner review |
| Deploy | working Streamlit URL; repeat UI checks online | Pending |
| Assessor access | assessor can open repository and dashboard | Pending |
| Attribution | all sources and AI help acknowledged; learner can explain work | Pending |

## Real findings to record in README and notebook after execution
| Question | Record actual observed values | Interpretation / decision |
|---|---|---|
| Overall | record count, mean, median, SD, skewness | describe typical versus average recorded charge |
| BQ1 | smoker and non-smoker n, mean and median, difference | describe association; identify groups for further investigation |
| BQ2 | age and BMI Pearson r overall and within smoking categories | compare strength/sign; note nonlinear patterns and confounding |
| BQ3 | region n, means, medians, smoker shares, within-group median ranks/spreads | discuss whether aggregate ordering changes by smoking group |
| Sensitivity | retained-versus-deduplicated count and change in mean/median | explain why chosen retention remains reasonable |

For each result, include a table or figure reference, actual numeric value, plain-language interpretation, limitation and management action. Mark an unanswered question honestly if groups are absent. Record review date, reviewer and actual test outcomes. Do not claim causality.

## Learner comprehension / oral review prompts
What is ETL? Why preserve the raw copy? Why are exact matching rows not necessarily duplicate people? What is the difference between the mean and median? Why does a boxplot show outliers? Why does a Pearson coefficient not establish causation? Why compare regions within smoking groups? Why avoid encoding region labels as continuous numbers? Why use a shared function across notebook and app? How did the two genuine test failures get corrected? What does SHA-256 verify and what does it not verify? Why are FHIR and clinical diagnosis codes relevant only to future integrations? How do you test an empty dashboard selection? What did ChatGPT contribute and how did you validate it?
