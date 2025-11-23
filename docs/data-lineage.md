# Data Lineage

High-level lineage from raw seed files to serving layers (analytics dashboard & RAG application).

```mermaid
flowchart LR
    subgraph Seeds
        A1[hr_policy.csv]
        A2[arbitration_subrogation.csv]
        A3[ml_concepts.csv]
    end

    subgraph Staging Models
        S1[stg_hr_policy]
        S2[stg_arbitration_subrogation]
        S3[stg_ml_concepts]
    end

    subgraph Feature / Derived
        F1[hr_policy_features]
        F2[arbitration_timelines]
    end

    subgraph Curated Mart
        M1[document_index]
    end

    subgraph Quality Gates
        Q1[dbt tests]
        Q2[GE expectations]
        Q3[Semantic checks]
    end

    subgraph Embeddings & Vector Store
        E1[(refresh_embeddings.py)]
        E2[Chroma Collection]
    end

    subgraph Serving Layers
        R1[RAG App]
        D1[Analytics Dashboard]
    end

    A1 --> S1
    A2 --> S2
    A3 --> S3
    S1 --> F1
    S2 --> F2
    S3 --> M1
    F1 --> M1
    F2 --> M1

    M1 --> Q1
    M1 --> Q2
    M1 --> Q3

    Q1 --> E1
    Q2 --> E1
    Q3 --> E1
    E1 --> E2
    E2 --> R1
    M1 --> D1
```

## Notes
- All transformations executed via dbt; tests applied post-build.
- Great Expectations and semantic checks gate the embedding refresh.
- Chroma persistent store consumed directly by RAG application; dashboard queries DuckDB marts.
- Future: add drift & anomaly checks between Quality Gates and Embedding step.
