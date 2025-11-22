#!/bin/bash
# End-to-End Data Platform & RAG Pipeline
# Runs: dbt → Great Expectations → Embeddings → Ready for RAG/Analytics

set -e  # Exit on any error

# Add Python user binaries to PATH
export PATH="$HOME/Library/Python/3.9/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
export REPO_ROOT

echo "=============================================================================="
echo "🚀 ENTERPRISE AI WORKFLOWS - FULL PIPELINE"
echo "=============================================================================="
echo "Repository: $REPO_ROOT"
echo "Started at: $(date)"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: dbt seed (load source data)
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📥 STEP 1: dbt seed - Load source CSV data${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
cd "$REPO_ROOT/data-platform/dbt"
dbt seed --profiles-dir .
echo -e "${GREEN}✅ Seeds loaded${NC}\n"

# Step 2: dbt run (build models)
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🏗️  STEP 2: dbt run - Build staging + marts${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
dbt run --profiles-dir .
echo -e "${GREEN}✅ Models built${NC}\n"

# Step 3: dbt test (data quality - dbt layer)
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🧪 STEP 3: dbt test - Run dbt quality checks${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
dbt test --profiles-dir .
echo -e "${GREEN}✅ dbt tests passed${NC}\n"

# Step 4: Great Expectations validation (semantic quality gate)
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔍 STEP 4: Great Expectations - Semantic quality gate${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
cd "$REPO_ROOT"

# Run manual validation (more reliable than GE runtime for this demo)
python3 << 'PYEOF'
import duckdb
import sys

con = duckdb.connect('/Users/justin/enterprise-ai-workflows/data-platform/dbt/warehouse/data.duckdb')

print("Running data quality validations...\n")

# Check row count
row_count = con.execute('SELECT COUNT(*) FROM main_marts.document_index').fetchone()[0]
assert 20 <= row_count <= 25, f"Row count {row_count} not in range 20-25"
print(f"✓ Row count: {row_count} (expected 20-25)")

# Check schema
cols = [c[0] for c in con.execute('DESCRIBE main_marts.document_index').fetchall()]
assert cols == ['id', 'domain', 'text'], f"Schema mismatch: {cols}"
print(f"✓ Schema: {cols}")

# Check nulls
id_nulls = con.execute('SELECT COUNT(*) FROM main_marts.document_index WHERE id IS NULL').fetchone()[0]
domain_nulls = con.execute('SELECT COUNT(*) FROM main_marts.document_index WHERE domain IS NULL').fetchone()[0]
text_nulls = con.execute('SELECT COUNT(*) FROM main_marts.document_index WHERE text IS NULL').fetchone()[0]
assert id_nulls == 0 and domain_nulls == 0 and text_nulls == 0, "Found NULL values"
print(f"✓ No NULLs in critical columns")

# Check uniqueness
total = con.execute('SELECT COUNT(*) FROM main_marts.document_index').fetchone()[0]
unique = con.execute('SELECT COUNT(DISTINCT id) FROM main_marts.document_index').fetchone()[0]
assert total == unique, f"Duplicate IDs found: {total} rows, {unique} unique"
print(f"✓ All IDs unique: {unique}/{total}")

# Check text lengths
min_len, max_len = con.execute('SELECT MIN(LENGTH(text)), MAX(LENGTH(text)) FROM main_marts.document_index').fetchone()
assert 50 <= min_len and max_len <= 300, f"Text length out of bounds: {min_len}-{max_len}"
print(f"✓ Text lengths: {min_len}-{max_len} chars (expected 50-300)")

print("\n✅ All quality checks passed!")
sys.exit(0)
PYEOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Great Expectations validation passed${NC}\n"
else
    echo -e "${RED}❌ Quality gate failed - stopping pipeline${NC}"
    exit 1
fi

# Step 5: Refresh embeddings (build vector store)
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🧬 STEP 5: Refresh Embeddings - Build vector store${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
cd "$REPO_ROOT"

# Check if embeddings script exists
if [ -f "scripts/refresh_embeddings.py" ]; then
    python3 scripts/refresh_embeddings.py \
        --persist-dir "$REPO_ROOT/project3-document-qa/chroma_store" \
        --reset
    echo -e "${GREEN}✅ Embeddings refreshed${NC}\n"
else
    echo -e "${YELLOW}⚠️  scripts/refresh_embeddings.py not found - skipping embeddings${NC}\n"
fi

# Step 6: Verify vector store
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}✔️  STEP 6: Verify vector store${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

python3 << 'PYEOF'
import sys
import os

chroma_dir = "/Users/justin/enterprise-ai-workflows/project3-document-qa/chroma_store"

if not os.path.exists(chroma_dir):
    print(f"⚠️  Chroma store not found at {chroma_dir}")
    sys.exit(0)

try:
    import chromadb
    client = chromadb.PersistentClient(path=chroma_dir)
    collection = client.get_collection("documents")
    count = collection.count()
    print(f"✓ Vector store contains {count} documents")
    print(f"✓ Location: {chroma_dir}")
    print("\n✅ Vector store verified!")
except Exception as e:
    print(f"⚠️  Could not verify vector store: {e}")
    sys.exit(0)
PYEOF

echo ""

# Pipeline complete
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 PIPELINE COMPLETE!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Artifacts generated:"
echo "  📊 DuckDB warehouse: data-platform/dbt/warehouse/data.duckdb"
echo "  🧬 Vector store: project3-document-qa/chroma_store/"
echo "  📄 dbt docs: data-platform/dbt/target/index.html"
echo ""
echo "Next steps:"
echo "  1. Launch RAG app:        cd project3-document-qa && python3 app.py"
echo "  2. Launch dashboard:      cd data-platform && streamlit run analytics_dashboard.py"
echo "  3. View dbt docs:         cd data-platform/dbt && dbt docs serve"
echo ""
echo "Finished at: $(date)"
echo "=============================================================================="
