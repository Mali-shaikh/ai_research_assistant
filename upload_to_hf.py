"""
Upload all project files to Hugging Face Space via Python API.
Run: python upload_to_hf.py
"""
from huggingface_hub import HfApi
import os

# ── EDIT THESE ─────────────────────────────────────────────────────────────
HF_TOKEN   = input("Paste your Hugging Face WRITE token (hf_...): ").strip()
REPO_ID    = "hrmis66/ai_research_assistant"
# ───────────────────────────────────────────────────────────────────────────

api = HfApi()

# Files to upload (source → destination path in the repo)
FILES = {
    "main_app.py":                  "main_app.py",
    "requirements.txt":             "requirements.txt",
    "README.md":                    "README.md",
    "app/main.py":                  "app/main.py",
    "app/frontend/gradio_ui.py":    "app/frontend/gradio_ui.py",
}

print("\nUploading files to HF Space...\n")
for local_path, repo_path in FILES.items():
    if os.path.exists(local_path):
        api.upload_file(
            path_or_fileobj=local_path,
            path_in_repo=repo_path,
            repo_id=REPO_ID,
            repo_type="space",
            token=HF_TOKEN,
            commit_message=f"Update {repo_path}",
        )
        print(f"  ✅ Uploaded: {repo_path}")
    else:
        print(f"  ⚠️  Skipped (not found): {local_path}")

print("\n✅ Done! Your HF Space will rebuild automatically.")
