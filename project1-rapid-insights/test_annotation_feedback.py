import csv
import os

ANNOTATION_FILE = "sentiment_annotations.csv"
FEEDBACK_FILE = "sentiment_feedback.csv"

def check_csv(file_path, expected_headers):
    if not os.path.exists(file_path):
        print(f"❌ {file_path} not found.")
        return False
    with open(file_path, newline="") as f:
        reader = csv.reader(f)
        headers = next(reader, None)
        if headers != expected_headers:
            print(f"❌ {file_path} headers mismatch. Found: {headers}")
            return False
        rows = list(reader)
        if not rows:
            print(f"⚠️ {file_path} exists but has no data rows.")
            return False
        print(f"✅ {file_path} found with {len(rows)} data rows.")
        for row in rows[-2:]:
            print("  Last row:", row)
    return True

def main():
    print("--- Testing annotation and feedback CSVs ---")
    annotation_ok = check_csv(
        ANNOTATION_FILE,
        ["text", "model_sentiment", "user_label", "prompt_template"]
    )
    feedback_ok = check_csv(
        FEEDBACK_FILE,
        ["text", "model_sentiment", "user_label", "feedback", "comment", "prompt_template"]
    )
    if annotation_ok and feedback_ok:
        print("\n🎉 All tests passed! Annotation and feedback features are working.")
    else:
        print("\n⚠️ Please test the app and submit at least one annotation and feedback.")

if __name__ == "__main__":
    main()
