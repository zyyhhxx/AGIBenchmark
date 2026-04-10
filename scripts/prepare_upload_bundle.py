#!/usr/bin/env python3
"""
Manual batch upload helper for Ian.

Generates a .zip file containing all notebooks + metadata files,
ready for manual upload via Kaggle web UI.

Usage:
  python scripts/prepare_upload_bundle.py
  # Creates: upload_bundle.zip

Then on kaggle.com:
  1. Go to kaggle.com/code → New Notebook → File → Upload Notebook
  2. Upload each .ipynb file
  3. Set title, make public, enable internet
  4. Save
"""
import json, os, zipfile, shutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NB_DIR = os.path.join(REPO, "notebooks")
OUT_DIR = os.path.join(REPO, "upload_bundle")
OUT_ZIP = os.path.join(REPO, "upload_bundle.zip")

# Notebooks that need uploading (not yet on Kaggle or need update)
NOTEBOOKS = {
    "metacog_error_detection.ipynb": "AGI Bench: Error Detection (Metacognition)",
    "metacog_learning_monitoring.ipynb": "AGI Bench: Learning Monitoring (Metacognition)",
    "metacog_control.ipynb": "AGI Bench: Metacognitive Control",
    "metacog_epistemic_revision.ipynb": "AGI Bench: Epistemic Revision",
    "metacog_canary.ipynb": "AGI Bench: Contamination Canary",
    "metacog_epistemic_humility.ipynb": "AGI Bench: Epistemic Humility",
    "attention_vigilance.ipynb": "AGI Bench: Vigilance (Sustained Attention)",
    "attention_divided.ipynb": "AGI Bench: Divided Attention",
    "attention_instruction_update.ipynb": "AGI Bench: Instruction Update (Attention)",
    "exec_func_wcst.ipynb": "AGI Bench: Wisconsin Card Sorting",
    "exec_func_tol.ipynb": "AGI Bench: Tower of London (Planning)",
    "exec_func_task_switch.ipynb": "AGI Bench: Task Switching",
    "exec_func_nback.ipynb": "AGI Bench: N-back Working Memory",
    "exec_func_crt.ipynb": "AGI Bench: Cognitive Reflection Test",
    "social_cog_false_belief.ipynb": "AGI Bench: False Belief Theory of Mind",
    "social_cog_pragmatic.ipynb": "AGI Bench: Pragmatic Inference",
    "social_cog_sarcasm.ipynb": "AGI Bench: Sarcasm Detection",
    "social_cog_emotional_prosody.ipynb": "AGI Bench: Emotional Prosody",
    "metacog_fok_submetrics.ipynb": "AGI Bench: FOK Sub-metrics",
    "metacog_jol_submetrics.ipynb": "AGI Bench: JOL Sub-metrics",
    "metacog_error_detection_submetrics.ipynb": "AGI Bench: Error Detection Sub-metrics",
#    "submission_overview.ipynb": "AGI Bench: Submission Overview",  # REMOVED: merged into SUBMISSION_NARRATIVE.md
}

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    
    # Create instruction file
    instructions = ["# Upload Instructions\n"]
    instructions.append("Upload each notebook to Kaggle via: kaggle.com/code → New Notebook → File → Upload Notebook\n")
    instructions.append("For each notebook:\n1. Upload the .ipynb file\n2. Set the title as shown below\n3. Settings: Make PUBLIC, Enable INTERNET\n4. Competition source: kaggle-measuring-agi\n5. Save\n\n")
    instructions.append("| # | Filename | Title |\n|---|----------|-------|\n")
    
    with zipfile.ZipFile(OUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zf:
        for i, (filename, title) in enumerate(NOTEBOOKS.items(), 1):
            src = os.path.join(NB_DIR, filename)
            if os.path.exists(src):
                zf.write(src, filename)
                instructions.append(f"| {i} | `{filename}` | {title} |\n")
                print(f"✓ Added: {filename}")
            else:
                print(f"✗ Missing: {filename}")
        
        # Add instructions
        zf.writestr("UPLOAD_INSTRUCTIONS.md", "".join(instructions))
    
    # Also write instructions standalone
    with open(os.path.join(REPO, "UPLOAD_INSTRUCTIONS.md"), 'w') as f:
        f.writelines(instructions)
    
    size_mb = os.path.getsize(OUT_ZIP) / (1024 * 1024)
    print(f"\n✓ Created: upload_bundle.zip ({size_mb:.1f} MB)")
    print(f"  Contains {len(NOTEBOOKS)} notebooks + instructions")
    
    # Cleanup temp dir
    shutil.rmtree(OUT_DIR, ignore_errors=True)

if __name__ == "__main__":
    main()
