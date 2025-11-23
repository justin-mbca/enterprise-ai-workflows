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

    subgraph Monitoring & Safety
        MON1[Row Count Anomaly Check]
        MON2[Embedding Drift Detection]
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

    Q1 --> MON1
    Q2 --> MON1
    Q3 --> MON1
    MON1 --> E1
    E1 --> E2
    E2 --> MON2
    MON2 -->|Pass| R1
    MON2 -->|Fail| R1
    M1 --> D1

    style MON1 fill:#fff3cd
    style MON2 fill:#fff3cd
```

## Notes
- All transformations executed via dbt; tests applied post-build.
- Great Expectations and semantic checks gate the embedding refresh.
- **Row Count Anomaly Check**: Statistical monitoring (Z-score) detects unexpected volume changes in marts before embeddings.
- **Embedding Drift Detection**: Monitors L2 norm distribution post-embedding to catch model/input quality degradation; blocks pipeline on drift.
- Chroma persistent store consumed directly by RAG application; dashboard queries DuckDB marts.
- Daily validation workflow (06:00 UTC) runs full test suite + monitoring checks proactively.
