# SupplyChain Sentinel audit report

## Scope and architecture

The repository implements a local end-to-end workflow for inventory planners: CSV/synthetic input → validation → cleaning → leakage-aware features → saved-model probability → deterministic risk decision → Streamlit/CSV output, with batch results persisted to SQLite. Core entry points are `run_pipeline.py` and `streamlit_app.py`.

Fully implemented features include deterministic data generation, cleaning reports, EDA outputs, model comparison, chronological evaluation, saved inference, risk scoring, SQL tables/queries, upload mapping, five Streamlit pages, session-state activation, and downloads. There are no external APIs or credentials. The UI’s decorative hero values illustrate the type of signal and are not live KPIs; actual KPIs below it are data-driven. There is no public deployment, user authentication, scheduled scoring, real ERP integration, or production monitoring.

Essential files are the entry points, `src/`, `app_pages/`, `components/`, `state.py`, `app_utils.py`, `.streamlit/config.toml`, requirements, tests, generated model/data/metric artifacts, and README. Empty `.gitkeep` files are intentional. The empty `notebooks/` directory is nonessential and can be omitted when publishing. Local logs, caches, and `.venv` are nonessential and ignored.

## ML correctness

The target is a future seven-day event and current `stockout_event` is excluded from predictors. Rolling demand and stockout history are shifted. Splits follow time, and Scikit-learn pipelines fit imputers, encoders, scalers, and models only on training data. Class weighting addresses imbalance for applicable models. Random seeds are fixed. The persisted model is loaded by inference and the Streamlit pages use its outputs.

The selected model is Logistic Regression, chosen by validation F1 with recall as a tie-breaker. Verified untouched-test metrics are precision 0.5191, recall 0.8651, F1 0.6488, and ROC-AUC 0.8705. The operational risk score and replenishment recommendation are deterministic rules and are not described as learned ML outputs.

## Security and reproducibility

Uploads are CSV-only in the UI, parsed in memory, limited to 10 MB, checked for empty data and duplicate normalized headers, and validated for required date/numeric fields. Uploaded data is not written to the database. Secrets files and `.env` are ignored, no credentials or machine-specific paths were found in project source, and database URLs come from an environment variable. Dependencies are pinned to the versions used in the verified environment.

Generated production artifacts were previously ignored even though the app requires them. The ignore rules now keep the data, saved model, metrics, figures, and SQLite demo eligible for inclusion in a future Git repository. This directory itself is not currently a Git repository, so history scanning and tracked-file verification could not be performed.

## Input scenario results

- **Normal:** the bundled clean CSV was submitted through `prepare_uploaded_csv`; 1,000 rows were cleaned/featured successfully and produced model-ready features.
- **Edge case:** common alternate headers such as `SKU`, `Stock_On_Hand`, `Demand`, and `Lead_Days` were resolved by the mapper; optional fields are defaulted and derived.
- **Invalid:** empty, oversized, missing-column, invalid-date, nonnumeric, and duplicate-normalized-header paths return explicit errors. Automated tests cover empty, oversized, and missing-schema cases.

## Deployment status

The app runs locally with `streamlit run streamlit_app.py` and uses project-relative paths. Streamlit Community Cloud is the simplest deployment option. A public URL was not created or verified. The owner must initialize/push a GitHub repository, add personal links/license identity, deploy, and smoke-test the public URL.

## Standout assessment

Compared with Titanic, house-price, basic chatbot, simple dashboard, or CRUD projects, the distinctive work is the time-aware operational simulation, explicit data-quality decisions, leakage controls, real saved-model inference, separate transparent decision engine, flexible user schema mapping, SQL persistence, and exportable action plan. The most valuable realistic enhancement added during this audit is the downloadable planner action queue. Real data validation or probability calibration would improve differentiation further. Deep learning, microservices, paid APIs, and an LLM recommendation layer would add complexity without addressing the current evidence gap.

## Strict score

| Category | Before | After | Maximum |
|---|---:|---:|---:|
| Core functionality | 18 | 19 | 20 |
| Genuine end-to-end workflow | 13 | 14 | 15 |
| Code quality | 8 | 9 | 10 |
| ML/data correctness | 13 | 14 | 15 |
| Testing and reliability | 7 | 9 | 10 |
| User experience | 4 | 5 | 5 |
| GitHub documentation | 6 | 9 | 10 |
| Deployment readiness | 2 | 4 | 5 |
| Interview explainability | 2 | 5 | 5 |
| Originality and portfolio value | 4 | 5 | 5 |
| **Total** | **77** | **93** | **100** |

The remaining seven points require public-deployment verification, a real Git repository/history audit, real operational data, calibration/cost validation, and broader end-to-end upload interaction testing in a rendered browser.
