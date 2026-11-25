# Task 4 — Data management (4.1, 4.2)

Source: assigned Kaggle Healthcare Insurance dataset, secondary data in CSV format. Download the exact assigned dataset manually; record original filename, date, description, licence/permission, units and coverage in `data/source_metadata.json`. A publicly visible page does not grant redistribution rights. Neither licence nor raw file could be verified by this assistant. Do not guess the currency, year or representativeness. If the source does not confirm a field, explicitly enter 'Not stated by source'. Permission must genuinely be confirmed before deployment.

## Expected data dictionary (confirm against source)
| Field | Type after ETL | Meaning / units | Validation |
|---|---|---|---|
| age | integer | age in years (expected) | integer 18–120, project adult cohort assumption |
| sex | string | recorded category, not inferred gender identity | female/male, expected source categories |
| bmi | float | body mass index, kg/m² (expected) | finite >0; outside 10–80 review only |
| children | integer | covered children/dependants; count | nonnegative integer |
| smoker | string | recorded smoking status | yes/no |
| region | string | broad geographic category | northeast, northwest, southeast, southwest |
| charges | float | recorded medical insurance charges, units from source | finite, nonnegative; IQR extremes retained |
| age_band | string | derived age segment | [18,30), [30,40), [40,50), [50,60), [60,∞) |

## Lineage and quality controls
Source download → unchanged raw CSV and SHA-256 → pandas profile → normalized labels / parsed numeric fields → validation and quarantined rows (with source row and reason) → age band → separate cleaned CSV → reload and equality check → group summaries and dashboard. Report raw, retained and excluded counts. Reject unexpected schema; investigate and fix documented assumptions rather than silently coercing unknown categories. Missing required values are quarantined; if material, compare excluded and included characteristics and request correction. No imputation because replacing target charges invents observed expenditure and replacing attributes risks biased grouping. No encoding needed for exploratory analysis; numeric categories would imply artificial order. Valid extremes remain; use robust summaries. Preserve identical rows because no unique ID, report sensitivity to removing them without changing the primary dataset. Review age/BMI bounds with source documentation; they are analytic flags/rules, not medical diagnostic criteria.

| Dimension | Measurable check / limitation | Action |
|---|---|---|
| Completeness | missing per column, parse failures, complete row rate | record exclusions and review proportion |
| Consistency | allowed category values, normalization count, matching types | standardize whitespace/case; investigate unexpected labels |
| Accuracy | external clinical/billing truth cannot be checked; internal range checks only | request data dictionary and source reconciliation |
| Timeliness | acquisition date recorded; observation period may be unknown | no forecasts or current cost claims without dates |
| Uniqueness | count exact repeated rows, no person identifier | retain and compare sensitivity; request ID if authorized |
| Validity | schema, finite values, allowed categories, plausible project bounds | quarantine failed rows; log reasons; stop if none valid |

CSV is readable, portable, suitable for a small static file and auditable with hashes; it lacks enforced types, constraints, concurrent transactions and row-level permissions. SQLite would offer typed schemas, checks, SQL queries and transactional updates for a growing single-user project; a governed database with access control would be better for multi-user clinical operations. CSV plus explicit code validation is proportionate here. Keep raw separate from derived data; never overwrite it. Do not publish quarantine files; they may include unexpected content. Restrict access to private source copies, keep credentials out of Git, use HTTPS and authorized sharing, and agree retention/deletion periods with the institution. Publish only permitted artifacts. Public data with no direct identifiers may still allow reidentification through combinations; avoid row-level public downloads and consider suppressing small groups for real sensitive data. Do not apply these patterns to individual eligibility, pricing or discrimination. Evaluate representativeness and group fairness before operational use.

HL7 FHIR is an electronic health information exchange standard [3]; it would be relevant for integrating governed clinical/claim resources, not a requirement to convert this static CSV. ICD diagnosis coding would be useful for case-mix adjustment if diagnoses existed; none are expected here. Privacy obligations such as GDPR or HIPAA depend on jurisdiction, entity and identifiability; no blanket claim of compliance is possible. Data minimization and secure sharing remain appropriate regardless.

[3] HL7, FHIR Overview, https://www.hl7.org/fhir/overview.html (accessed 25 November 2026).
