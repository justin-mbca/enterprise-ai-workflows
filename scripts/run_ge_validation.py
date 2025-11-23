"""
Run Great Expectations validation checkpoint for document_index
"""
import os
import sys
from great_expectations.data_context import FileDataContext

# Set repo root
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.environ["REPO_ROOT"] = repo_root

# Initialize context
context_root = os.path.join(repo_root, "great_expectations")
context = FileDataContext(context_root_dir=context_root)

# Build batch request using RuntimeBatchRequest
from great_expectations.core.batch import RuntimeBatchRequest

batch_request = RuntimeBatchRequest(
    datasource_name="duckdb_warehouse",
    data_connector_name="default_runtime_data_connector",
    data_asset_name="document_index",
    runtime_parameters={
        "query": "SELECT id, domain, text FROM main_marts.document_index"
    },
    batch_identifiers={"default_identifier_name": "manual_run"}
)

# Get validator
print(f"📊 Loading document_index data from {repo_root}/data-platform/dbt/warehouse/data.duckdb...")
validator = context.get_validator(
    batch_request=batch_request,
    expectation_suite_name="document_index_suite"
)

print(f"✅ Data loaded successfully")
print("\n🔍 Running Great Expectations validation suite...\n")

# Run validation
results = validator.validate()

# Print results
print("=" * 80)
print(f"Validation Results: {'✅ SUCCESS' if results.success else '❌ FAILURE'}")
print("=" * 80)

print(f"\nExpectations evaluated: {results.statistics['evaluated_expectations']}")
print(f"✅ Successful: {results.statistics['successful_expectations']}")
print(f"❌ Failed: {results.statistics['unsuccessful_expectations']}")
print(f"Success rate: {results.statistics['success_percent']:.1f}%\n")

# Detail failures
if not results.success:
    print("\n❌ Failed Expectations (detailed):")
    for result in results.results:
        if not result.success:
            print(f"\n  - {result.expectation_config.expectation_type}")
            print(f"    Column: {result.expectation_config.kwargs.get('column', 'N/A')}")
            if "observed_value" in result.result:
                print(f"    Observed: {result.result['observed_value']}")
            if "unexpected_count" in result.result:
                print(f"    Unexpected count: {result.result['unexpected_count']}")
            if "unexpected_list" in result.result and result.result["unexpected_list"]:
                print(f"    Sample unexpected: {result.result['unexpected_list'][:3]}")
            print(f"    Result details: {result.result}")
    print()

# Save validation results
context.add_or_update_expectation_suite(expectation_suite=validator.get_expectation_suite())
print("💾 Validation results stored")

# Build Data Docs
print("\n📄 Building Data Docs...")
context.build_data_docs()
print("✅ Data Docs updated")

# Exit with appropriate code
sys.exit(0 if results.success else 1)
