"""
Example: Run the LLMHarmfulGenerator Pipeline
================================================
This script demonstrates a full end-to-end run of the synthetic data
generation pipeline with a small sample dataset.

Prerequisites:
    1. Set your OPENAI_API_KEY environment variable
    2. Install dependencies: pip install -r requirements.txt
    3. Run from the repository root: python example_run.py

What this example does:
    - Creates a sample JSONL chunk file in data/chunks/
    - Generates a temporary override config for fast testing
    - Runs instruction synthesis (Stage 1)
    - Runs response synthesis (Stage 2)
    - Prints the generated (instruction, response) pairs
"""

import sys
import json
from pathlib import Path

# ──────────────────────────────────────────────────────────────────
# 1.  Create a small sample dataset
# ──────────────────────────────────────────────────────────────────
SAMPLE_CHUNKS = [
    {
        "context": (
            "The East Sea (Biển Đông) is a critical maritime region for Vietnam, "
            "with significant economic and strategic importance. Vietnam asserts "
            "its sovereignty over the Hoang Sa (Paracel) and Truong Sa (Spratly) "
            "archipelagos in accordance with international law, particularly the "
            "UNCLOS 1982."
        )
    }
]

# Create the chunk file
chunks_dir = Path("data/chunks")
chunks_dir.mkdir(parents=True, exist_ok=True)

chunk_file_name = "example.jsonl"
chunk_file = chunks_dir / chunk_file_name

print("=" * 70)
print("LLMHarmfulGenerator – Example Run")
print("=" * 70)

print(f"\n[1/4] Creating sample chunk file: {chunk_file}")
with open(chunk_file, "w", encoding="utf-8") as f:
    for item in SAMPLE_CHUNKS:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")
print(f"       Wrote {len(SAMPLE_CHUNKS)} records.")

# ──────────────────────────────────────────────────────────────────
# 2.  Create a temporary override config for faster testing
# ──────────────────────────────────────────────────────────────────
override_config = {
    "data": {
        "chunks": "data/chunks",
        "instructions": "data/instructions/tmp",
        "responses": "data/responses/tmp",
        "sft_data": "data/sft_data/tmp",
    },
    "domain": "Vietnamese history and politics",
    "output_language": "Vietnamese",
    "instruction_requirements": "",
    "response_requirements": "",
    "number_questions_per_openai_call": 1,      # keep small for demo
    "number_questions_per_chunk": 1,            # keep small for demo
    "filter_instructions_first": True,
    "llm": "gpt-4o-mini",                       # cost-effective model
    "batch_size": 30,
}

override_dir = Path("configs/override_example")
override_dir.mkdir(parents=True, exist_ok=True)
override_config_path = override_dir / "config.yml"

print(f"\n[2/4] Creating override config: {override_config_path}")
# We write it as a small YAML by hand so the YAML reader can load it.
yaml_lines = [
    "data:",
    '  chunks: "data/chunks"',
    '  instructions: "data/instructions/tmp"',
    '  responses: "data/responses/tmp"',
    '  sft_data: "data/sft_data/tmp"',
    f'domain: {override_config["domain"]}',
    f'output_language: {override_config["output_language"]}',
    'instruction_requirements: ""',
    'response_requirements: ""',
    f'number_questions_per_openai_call: {override_config["number_questions_per_openai_call"]}',
    f'number_questions_per_chunk: {override_config["number_questions_per_chunk"]}',
    f'filter_instructions_first: {str(override_config["filter_instructions_first"]).lower()}',
    f'llm: {override_config["llm"]}',
    f'batch_size: {override_config["batch_size"]}',
]
with open(override_config_path, "w", encoding="utf-8") as f:
    f.write("\n".join(yaml_lines) + "\n")
print(f"       Config written with small values for fast demo.")

# ──────────────────────────────────────────────────────────────────
# 3.  Run the pipeline
# ──────────────────────────────────────────────────────────────────
print(f"\n[3/4] Running the synthesis pipeline ...")
print(f"       Command:")
print(f"       python synthesize-pipeline.py --override_default_config configs/override_example/config.yml")
print(f"       (This example script delegates to the main entry point)\n")

# We need to copy sys.argv so the main pipeline sees our override argument.
# We'll use subprocess to keep things clean.
import subprocess

cmd = [
    sys.executable,
    "synthesize-pipeline.py",
    "--override_default_config",
    str(override_config_path),
]

print(f"       Running: {' '.join(cmd)}\n")
result = subprocess.run(cmd, capture_output=False)

if result.returncode != 0:
    print(f"\n[!] Pipeline exited with code {result.returncode}")
    sys.exit(result.returncode)

# ──────────────────────────────────────────────────────────────────
# 4.  Inspect the generated results
# ──────────────────────────────────────────────────────────────────
print(f"\n[4/4] Inspecting generated results ...\n")

instructions_file = Path("data/instructions/tmp") / chunk_file_name
responses_file = Path("data/responses/tmp") / chunk_file_name

print(f"    Instructions: {instructions_file}")
print(f"    Responses:    {responses_file}\n")

if instructions_file.exists():
    with open(instructions_file, "r", encoding="utf-8") as f:
        instructions = [json.loads(line) for line in f if line.strip()]
    print(f"    → {len(instructions)} instruction(s) generated.\n")
    for i, inst in enumerate(instructions, 1):
        print(f"      [{i}] Type: {inst['instruction_type']}")
        print(f"          Instruction: {inst['instruction'][:120]}...")
        print()
else:
    print("    [!] No instructions file found. Stage 1 may have failed.\n")

if responses_file.exists():
    with open(responses_file, "r", encoding="utf-8") as f:
        responses = [json.loads(line) for line in f if line.strip()]
    print(f"    → {len(responses)} response(s) generated.\n")
    for i, resp in enumerate(responses, 1):
        print(f"      [{i}] Instruction: {resp['instruction'][:80]}...")
        print(f"          Response:   {resp['response'][:150]}...")
        print()

# ──────────────────────────────────────────────────────────────────
# Done
# ──────────────────────────────────────────────────────────────────
print("=" * 70)
print("Example run complete!")
print("=" * 70)
print(f"\nGenerated files saved to:")
print(f"  - {instructions_file}")
print(f"  - {responses_file}")
print(f"\nTip: Inspect the raw JSONL files for full (instruction, response) pairs.")