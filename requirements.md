# SynthGen – Requirements

## 1 Purpose

SynthGen creates **realistic, constraint‑valid synthetic data** for SQL Server schemas so that teams can develop, test, and demonstrate solutions without exposing production data.

## 2 Scope

The MVP processes **one domain schema at a time**, ingesting:

1. A SQL Server **CREATE script** for the target schema.
2. **Reference‑data CSVs** (one per lookup table).
3. A **Generation‑Rules JSON** document with structured natural‑language rules.

Outputs include generated data files plus debug artifacts (intermediate representations, validation reports, agent traces).

## 3 Definitions

| Term                | Meaning                                                                    |
| ------------------- | -------------------------------------------------------------------------- |
| **Domain Schema**   | A cohesive SQL Server schema (e.g., `Participant`) within a DDD landscape. |
| **Reference Table** | A lookup table whose codes seed foreign keys.                              |
| **Generation Rule** | A JSON‑hosted, structured‑NL statement that constrains generated data.     |

## 4 Overall Description

SynthGen orchestrates a **team of LLM‑centric agents** supported by lightweight Python helpers when indispensable (e.g., file I/O, CSV merging). Each stage logs prompts, reasoning, and outputs under `/artifacts/<run‑id>/<stage>/` to maximise transparency and prompt‑engineering feedback.

## 5 User Cases (Stories)

| ID                               | User Story                                                                                                                                                                                  | Key Acceptance Criteria                                                                                                                                  |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **UC‑1 Parse Schema**            | _As a **\*\*\*\***Data Modeler**\*\*\*\***, I want to provide a SQL Server CREATE script so that SynthGen can build an internal model of tables, columns, keys, and constraints._           | – Script is interpreted without error (LLM‑driven parsing)– Resulting IR exposes PK/FK, indexes, CHECKs                                                  |
| **UC‑2 Load Reference Data**     | _As a **\*\*\*\***QA Engineer**\*\*\*\***, I want to supply CSV files that match reference tables so that lookup values populate foreign keys accurately._                                  | – CSV columns align with table definition– Missing lookups raise a clear error                                                                           |
| **UC‑3 Generate Random Data**    | _As a **\*\*\*\***Developer**\*\*\*\***, I want non‑reference columns auto‑filled with realistic values that respect data types and nullability so that test cases behave like production._ | – Generated rows satisfy data types & nullability– Values produced primarily through LLM reasoning, complemented by minimal Python utilities if required |
| **UC‑4 Apply Business Rules**    | _As a **\*\*\*\***Business Architect**\*\*\*\***, I want to express generation rules in JSON using structured NL so that domain constraints are enforced._                                  | – Rules validated against schema– Violations reported as failures                                                                                        |
| **UC‑5 Deterministic Runs**      | _As a **\*\*\*\***QA Engineer**\*\*\*\***, I want to pass a random‑seed value so that datasets are reproducible for debugging._                                                             | – Same seed ⇒ identical output (via LLM temperature control / seed)                                                                                      |
| **UC‑6 Validate & Report**       | _As a **\*\*\*\***Solution Architect**\*\*\*\***, I want SynthGen to validate generated data and emit a summary report so that I can trust the dataset._                                    | – Zero constraint/rule violations– Report saved to artifacts dir                                                                                         |
| **UC‑7 Incremental Domains**     | _As a **\*\*\*\***Data Engineer**\*\*\*\***, I want to generate one schema at a time while preserving FK linkages to prior runs so that datasets can be assembled gradually._               | – FK values match prior domain rows– Tool accepts dependency graph                                                                                       |
| **UC‑8 Observability Artifacts** | _As a **\*\*\*\***Prompt Engineer**\*\*\*\***, I want every agent to persist its prompt, reasoning, and outputs so that I can refine prompts over time._                                    | – Files written per stage– Trace readable and timestamped                                                                                                |
| **UC‑9 CLI & API**               | _As a **\*\*\*\***DevOps Engineer**\*\*\*\***, I want both a CLI and importable Python API so that SynthGen integrates into CI/CD pipelines._                                               | – `synthgen generate …` command– `import synthgen` exposes builder                                                                                       |

## 6 Non‑Functional Requirements

| ID                      | Requirement                                                                                                                                                                            |     |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --- |
| **NFR‑1 Performance**   | Generate 100K rows across ≤50 tables in under 10 minutes on an M2 Max laptop.                                                                                                          |     |
| **NFR‑2 Extensibility** | Agent roster and helper scripts are modular so that new data types or rules can be added via prompt or plugin without core rewrites.                                                   |     |
| **NFR‑3 Observability** | Structured logging, progress metrics, artifact directory per run.                                                                                                                      |     |
| **NFR‑4 Security**      | For the PoC, SynthGen may call approved frontier‑LLM APIs over secure channels; the longer‑term aspiration is to support fully offline execution on locally hosted open‑source models. |     |
| **NFR‑5 Portability**   | Works on macOS, Windows, Linux with Python 3.12 venv.                                                                                                                                  |     |

## 7 Assumptions

1. CREATE scripts are syntactically valid.
2. Reference CSVs cover all lookup values.
3. Generation Rules conform to the JSON Schema (Appendix A).

## 8 Constraints & Dependencies

- Python 3.12 runtime for orchestration and lightweight data utilities (CSV reading, file management).
- Access to LLMs (OpenAI, Anthropic, or locally hosted) with reproducible seeding controls.
- Any third‑party Python packages should be introduced **only** if an LLM‑only approach proves insufficient for that stage.

## 9 Acceptance Criteria

- All user cases UC‑1 → UC‑9 satisfied on sample database schema.
- Validation report shows **0** violations.
- Runtime meets NFR‑1 benchmark.

## 10 Out‑of‑Scope (Phase 2+)

- Direct DB insertion (initial output is file‑based).
- GUI frontend.
- Non‑SQL Server dialects.

## 11 Appendices

- **A. Generation Rules JSON Schema** (TBD)
- **B. Sample CLI Invocations** (TBD)
- **C. Benchmark Datasets** (TBD)

---

_Updated ↔ 2025‑05‑13_
