# Task 3 — AI assistance record (3.1, 3.2)

Tool: OpenAI ChatGPT, used 25 November 2026. It was selected to interpret a lengthy rubric, develop Python/Streamlit code, review ETL decisions and draft evidence-based communication. The learner must review and understand all code and may need to add their own subsequent prompt/response history under institutional rules.

Actual user prompt: “Understand this assignment and provide complete solution so that I can get maximum marks”. Assistant interpreted the brief, selected three business questions, built shared functions, tests, dashboard and notebook, and recommended retaining repeated valid rows and high charges. No confidential records were provided. Dataset acquisition failed; synthetic fixtures were used explicitly for verification. No actual numerical finding has been claimed.

## Validation and review of suggestions
- Accepted: preserve raw data; use count/mean/median, stratify by smoking; test empty dashboard selections and compare summary arithmetic.
- Modified: the initial CSV reload assumed only `age_band` needed an explicit string dtype. The test failed because sex/smoker/region were pandas string fields; revised reload specifies all categorical strings. Roundtrip test now checks types and values.
- Modified: initial exclusion-reason `.apply` ran on an empty DataFrame and failed for all-valid data. Revised branch creates an empty reason Series when no invalid rows exist. Boundary test checks all-valid data.
- Rejected: inventing an official dataset licence or using the fictional test dataset as final evidence; direct download failed. Predictive extension omitted as not necessary and temporal validation impossible.

## AI-assisted narrative — draft and revision
Draft wording (generated during this work, not a separate claimed conversation): “Compare the mean and median charge by smoking status and region. Use the largest differences to identify groups for investigation.”
Revised wording: use `analysis.narrative`, which calculates selected record count, mean, median, smoking difference and regional median directly. It states that observed differences are not causal and cannot be used for individual pricing. One-group and empty selections have separate wording. The notebook displays the exact same narrative as the dashboard for identical selections. `test_filters` checks selection count and edge cases; `test_group_reconciliation` independently verifies group arithmetic. Actual data validation and learner review remain mandatory.

After obtaining the real data, record the actual generated narrative, verify each number against the tables and add date, reviewer and any revisions. Do not claim the learner personally wrote prompts or conducted checks they have not performed. A live AI API is not required and no records are sent to an AI service by the app.
