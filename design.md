# SynthGen – High‑Level Design

_Last updated: 2025‑05‑13_

---

## 1 Overview

This document describes the architecture and agent‑based design for **SynthGen**, a synthetic‑data generator for SQL Server domain schemas. It complements the _Requirements_ document and details how a pipeline of LLM‑centric agents, orchestrated by a lightweight Python script, transforms inputs into realistic, constraint‑valid datasets.

## 2 Confirmed Assumptions

| ID  | Assumption                                                                                                    | Notes                          |
| --- | ------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| A‑1 | **Pipeline architecture**—linear, ordered stages.                                                             | See §3.2 for stage list.       |
| A‑2 | **Light Python orchestrator** with a single `Agent` base class; each stage subclasses it.                     | Keeps non‑LLM logic minimal.   |
| A‑3 | **Intermediate Representation (IR) = JSON** capturing tables, columns, PK/FK, constraints, and rule bindings. | Spec in §4.                    |
| A‑4 | **Prompt Engineering Standards adopted**—reflection, reasoning, JSON‑only outputs.                            | Template in §5.                |
| A‑5 | **Stage artifacts** saved as `prompt.md` and `error.md` (if applicable) plus machine‑readable outputs.        | Directory layout in §6.        |
| A‑6 | **No real PII** will appear in generated data.                                                                | Data‑privacy guardrails in §7. |
| A‑7 | **External LLM API calls allowed for PoC**; offline open‑source models are a future goal.                     | Aligns with NFR‑4.             |

## 3 Technical Architecture

### 3.1 Component Diagram

```mermaid
flowchart LR
    CLI["CLI / Python API"] -->|"schema.sql
reference CSVs
rules.json"| ORCH["Orchestrator"]
    ORCH -->|"DDL + IR template"| PARSER["Canonical Parser
(SchemaParseAgent)"]
    PARSER -->|"canonical IR (JSON)"| REF["RefDataAgent"]
    REF -->|"IR with lookups"| SYNTH["DataSynthAgent"]
    SYNTH -->|"generated CSV data"| VAL["ValidationAgent"]
    VAL -->|"validation report"| ART["ArtifactWriter"]
```

### 3.2 Agent Pipeline

_(PoC configuration – one-step canonical parser)_ Agent Pipeline
_(PoC configuration – one-step canonical parser)_

| Stage                   | Agent Class        | Inputs                                    | Outputs                               |
| ----------------------- | ------------------ | ----------------------------------------- | ------------------------------------- |
| **1. Canonical Parser** | `SchemaParseAgent` | SQL CREATE script + canonical-IR template | **Canonical IR (JSON)**               |
| **2. Reference Loader** | `RefDataAgent`     | IR + CSV dir                              | IR with lookups JSON                  |
| **3. Data Synthesizer** | `DataSynthAgent`   | Enriched IR + Rules                       | Generated rows (CSV)                  |
| **4. Validator**        | `ValidationAgent`  | Generated rows + IR + Rules               | Validation report                     |
| **5. Artifact Writer**  | `ArtifactAgent`    | All stage outputs                         | Directory of prompts, errors, outputs |

> **Note — Future Option:** If parsing accuracy or maintainability suffers, we will re‑introduce a dedicated `IRBuilderAgent` that transforms a raw parse tree into the canonical IR. The downstream stages already rely solely on the canonical IR, so this change would be non‑breaking.

## 4 Intermediate Representation (IR) – Draft JSON Schema _(excerpt)_ Intermediate Representation (IR) – Draft JSON Schema _(excerpt)_

```json
{
  "schema": "Participant",
  "tables": [
    {
      "name": "Participant",
      "columns": [
        {"name": "ParticipantID", "type": "INT", "pk": true},
        {"name": "FirstName", "type": "NVARCHAR", "length": 50, "nullable": false},
        ...
      ],
      "fks": [
        {"column": "StatusCode", "ref_table": "ParticipantStatus", "ref_col": "StatusCode"}
      ],
      "checks": []
    },
    {
      "name": "ParticipantStatus",
      "columns": [
        {"name": "StatusCode", "type": "CHAR", "length": 1, "pk": true},
        {"name": "StatusDescription", "type": "NVARCHAR", "length": 50, "nullable": false}
      ],
      "reference_data": {
        "distribution_strategy": "weighted_random",
        "description": "Active statuses should be dominant in generated data",
        "rows": [
          {"StatusCode": "A", "StatusDescription": "Active", "weight": 0.70},
          {"StatusCode": "I", "StatusDescription": "Inactive", "weight": 0.20},
          {"StatusCode": "D", "StatusDescription": "Deleted", "weight": 0.10}
        ]
      }
    }
  ],
  "rules": []
}
```

### 4.1 Reference Data with Distribution Weights

Reference data in the IR can include distribution parameters that guide how values should be distributed in generated data:

1. **Table-level distribution metadata**:

   - `distribution_strategy`: The algorithm for applying weights ("weighted_random", "fixed_ratio", etc.)
   - `description`: Human-readable explanation of the intended distribution

2. **Row-level weights or frequencies**:
   - `weight`: A relative probability/weight for each reference value
   - `frequency`: An absolute count or percentage (for "fixed_ratio" strategy)

These distribution parameters help bridge structured reference data with intelligent LLM generation, allowing:

- Control over the relative frequency of reference values
- Natural language descriptions that guide generation
- Consistent output across multiple runs

Example distributions:

- Countries might use weights reflecting global population distribution
- Order status codes might represent typical lifecycle frequencies (80% Complete, 15% Processing, 5% Cancelled)
- Product categories might be distributed according to business focus areas

_(Complete JSON Schema to be elaborated.)_

## 5 Prompt Engineering Standards

1. **System preamble**: role, goal, and JSON‑only output directive.
2. **Reflection block**: agent must think step‑by‑step in hidden section (`<scratchpad>`).
3. **Deterministic seed**: pass `seed=<run_id>` when provider supports seeding.
4. **Error handling**: if parsing/generation fails, output `error.md` with description and suggested retry strategy.

## 6 Artifact Directory Structure

```
artifacts/
  20250513_153045/
    Parser/
      prompt.md
      response.json
      error.md (optional)
    IR_Builder/
      prompt.md
      ir.json
    RefLoader/
      prompt.md
      ir_with_refs.json
    DataSynth/
      prompt.md
      dataset.csv
    Validator/
      prompt.md
      validation_report.md
```

## 7 Data‑Privacy Guardrails

- All synthetic values derived from public faker patterns or model hallucination—never copied from reference PII.
- Optional mask: IR may label columns as `pii": true`; DataSynthAgent avoids realistic real‑world combos (e.g., SSN).

## 8 Extensibility Points

- **Plugin registry** (`plugins/`) auto‑discovers custom generators via entry points.
- **Rule evaluators** pluggable: start with row‑level constraints; plug in cross‑row evaluators later.

## 9 Performance & Resilience Targets

| Metric                  | Target                                   |
| ----------------------- | ---------------------------------------- |
| Throughput              | 100 K rows ≤ 10 min (M2 Max, GPT‑4o API) |
| Single LLM call timeout | 60 s (retry ×3 exponential backoff)      |
| Memory footprint        | ≤ 4 GB RAM peak                          |

## 10 Open Items

1. **Chunking strategy** for DDL > context window.
2. **Cross‑schema FK linking** approach for Phase 2.
3. **JSON Schema versioning** for Generation Rules.

---

_End of design skeleton. Sections will expand iteratively._
