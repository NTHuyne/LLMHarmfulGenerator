# LLMHarmfulGenerator

A two-stage synthetic data generation pipeline for LLM safety and guard research. This tool generates **harmful instructions** and **safe refusal responses** from domain-specific text corpora, enabling researchers to build datasets for training and evaluating content moderation / safety alignment in language models.

> **⚠️ Intended Use:** This tool is designed **exclusively for academic research on AI safety**. Generated data should only be used to train models to recognize and refuse harmful content. Do **not** use this to generate actual harmful content for malicious purposes.

---

## Table of Contents

- [How It Works](#how-it-works)
- [Repository Structure](#repository-structure)
- [Setup](#setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [Input Format](#input-format)
- [Output Format](#output-format)
- [Pipeline Details](#pipeline-details)
- [Ethical Considerations](#ethical-considerations)

---

## How It Works

The pipeline operates in two stages:

```
                       ┌─────────────────────────┐
                       │   data/chunks/*.jsonl   │
                       │  {"context": "text ..."}│
                       └──────────┬──────────────┘
                                  │
                                  ▼
                   ┌─────────────────────────────┐
                   │   Stage 1: Instruction Gen  │
                   │                             │
                   │  For each chunk:            │
                   │  1. Pick random harmful type│
                   │     (false info, prejudice, │
                   │      harmful content, ...)  │
                   │  2. Call OpenAI GPT         │
                   │     → generate misleading   │
                   │       instructions          │
                   │  3. Save to JSONL           │
                   └──────────┬──────────────────┘
                              │
                              ▼
                   ┌─────────────────────────────┐
                   │   Stage 2: Response Gen     │
                   │                             │
                   │  For each instruction:      │
                   │  1. Call OpenAI GPT         │
                   │     → generate a safe       │
                   │       refusal / correction  │
                   │  2. Save to JSONL           │
                   └──────────┬──────────────────┘
                              │
                              ▼
              ┌──────────────────────────────┐
              │   data/responses/*.jsonl     │
              │  {instruction, response, ...}│
              │   → Ready for SFT training   │
              └──────────────────────────────┘
```

### Stage 1 – Instruction Synthesis

Takes **text chunks** (your domain corpus) and generates **harmful or misleading instructions** that users might ask an LLM. Each instruction is assigned one of 8 harmful types:

| Type | Description |
|------|-------------|
| False information | Fabricated/inaccurate info presented as factual |
| Prejudices | Content that perpetuates societal biases |
| Harmful or misleading content | Damaging or deceptive content |
| Security and privacy | Compromising sensitive data |
| Inappropriate language | Offensive or discriminatory language |
| Unexpected situations | Unintended harmful outcomes |
| Fraud through impersonation | Convincing impersonations for fraud |
| Creating anxiety/fear | Content provoking fear or panic |
| Unfair handling of issues | Unjust or biased decisions |

### Stage 2 – Response Synthesis

For each generated instruction, the pipeline calls the LLM again with a **"guardian" prompt** that instructs the model to:
1. Identify why the instruction is harmful
2. Generate a clear, reasoned refusal response
3. Reference the original document for context

The output is a **direct instruction–response pair** suitable for supervised fine-tuning (SFT) of safety-aligned models.

---

## Repository Structure

```
LLMHarmfulGenerator/
├── synthesize-pipeline.py          # Main entry point
├── example_run.py                  # Self-contained example script
├── requirements.txt                # Python dependencies
├── configs/
│   ├── config.py                   # Config loading logic
│   └── config_loader/              # YAML/JSON config readers
├── settings/
│   └── config.yml                  # Default configuration
└── src/
    ├── instruction_generation/
    │   └── synthesize_instructions.py   # Stage 1 logic
    ├── response_generation/
    │   └── synthesize_responses.py      # Stage 2 logic
    ├── openai_calling/
    │   └── call_openai.py               # OpenAI API wrapper
    ├── prompts/
    │   ├── instructions.py              # Stage 1 prompt templates
    │   └── responses.py                 # Stage 2 prompt templates
    └── utils/
        ├── load_data.py                 # JSONL I/O helpers
        └── utils.py                     # Misc utilities
```

---

## Setup

### Prerequisites

- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys) with access to `gpt-4o-mini` or `gpt-4o`

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/NTHuyne/LLMHarmfulGenerator.git
cd LLMHarmfulGenerator

# 2. (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your OpenAI API key
export OPENAI_API_KEY="sk-..."  # Linux/Mac
# set OPENAI_API_KEY="sk-..."   # Windows
```

> **Tip:** Create a `.env` file in the project root:
> ```
> OPENAI_API_KEY=sk-your-key-here
> ```

---

## Configuration

All configuration is stored in `settings/config.yml`. Here is every field:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `data.chunks` | string | `"data/chunks"` | Directory containing input `.jsonl` chunk files |
| `data.instructions` | string | `"data/instructions/tmp"` | Output directory for Stage 1 (instructions) |
| `data.responses` | string | `"data/responses/tmp"` | Output directory for Stage 2 (responses) |
| `data.sft_data` | string | `"data/sft_data/tmp"` | Reserved for future SFT merge |
| `domain` | string | `"Văn kiện Đảng Cộng sản Việt Nam"` | Domain description for prompt context |
| `output_language` | string | `"Vietnamese"` | Language of generated text |
| `instruction_requirements` | string | `""` | Extra requirements for instruction prompts |
| `response_requirements` | string | `""` | Extra requirements for response prompts |
| `number_questions_per_openai_call` | int | `2` | Number of questions to generate per API call |
| `number_questions_per_chunk` | int | `2` | Total number of questions per chunk (`≤ num_questions_per_call × num_types`) |
| `filter_instructions_first` | bool | `True` | Whether to filter instructions before generating responses |
| `llm` | string | `"gpt-4o-mini"` | OpenAI model name (`gpt-4o-mini` / `gpt-4o`) |
| `batch_size` | int | `30` | Number of samples processed concurrently |

### Overriding Configuration

You can override defaults by passing a custom YAML config file:

```bash
python synthesize-pipeline.py --override_default_config /path/to/custom/config.yml
```

The custom file only needs to include the fields you want to change; other fields fall back to `settings/config.yml`.

---

## Usage

### Basic Run

```bash
python synthesize-pipeline.py
```

This processes all `.jsonl` files in `data/chunks/`.

### Custom Configuration

```bash
python synthesize-pipeline.py \
    --override_default_config configs/override_example/config.yml
```

### Example Script

For a quick end-to-end test, run the example script:

```bash
python example_run.py
```

This will:
1. Create a sample `.jsonl` file in `data/chunks/`
2. Generate a minimal override config
3. Run both pipeline stages
4. Print the generated instruction–response pairs

### Expected Pipeline Output

```
Processing files: 100%|██████████| 1/1 [00:10<00:00]
Synthesizing instructions: 100%|██████████| 1/1 [00:05<00:00]
Instructions have been saved to data/instructions/tmp/example.jsonl
Synthesizing responses: 100%|██████████| 1/1 [00:05<00:00]
Responses have been saved to data/responses/tmp/example.jsonl
```

---

## Input Format

### Chunk files (`data/chunks/*.jsonl`)

Each line is a JSON object with exactly one key:

```jsonl
{"context": "...your text passage here... This can be one or more paragraphs from a domain-specific corpus."}
```

The pipeline expects the `context` field to contain the text that will serve as the grounding document for both instruction generation and response generation.

---

## Output Format

### Instructions (`data/instructions/*.jsonl`)

```json
{
    "document": "The original chunk text...",
    "instruction": "Generated harmful instruction in the target language...",
    "instruction_type": "False information",
    "instruction_length": 245
}
```

### Responses (`data/responses/*.jsonl`)

```json
{
    "document": "The original chunk text...",
    "instruction": "Generated harmful instruction...",
    "instruction_type": "False information",
    "instruction_length": 245,
    "response_length": 312,
    "response": "Detailed refusal / correction response explaining why the content is harmful and providing accurate information..."
}
```

### Token Usage Logging

API call metadata is automatically logged to `logs/openai_usages.jsonl`:

```json
{"timestamp": "2026-06-16 09:50:00", "completion_tokens": 150, "prompt_tokens": 420}
```

---

## Pipeline Details

### Instruction Generation (`src/instruction_generation/synthesize_instructions.py`)

- Loads all chunk files from the configured `data.chunks` directory
- For each chunk, iterates `number_questions_per_chunk` times
- Each iteration:
  1. Randomly selects an instruction type from the 9 predefined types
  2. Formats the prompt with the chunk text, type, and requirements
  3. Calls the LLM to generate `number_questions_per_openai_call` instructions
  4. Parses and cleans the output (removes leading numbering)
- Writes results to the instructions output file in batches

### Response Generation (`src/response_generation/synthesize_responses.py`)

- Loads the generated instructions from the Stage 1 output
- For each instruction, calls the LLM with a "refusal prompt" that:
  - Identifies the harmful type
  - References the original document for factual accuracy
  - Generates a reasoned refusal/rejection
- Writes the complete (instruction, response) pairs to the responses output file

### OpenAI Integration (`src/openai_calling/call_openai.py`)

- Wraps the OpenAI Python SDK
- Uses `temperature=0.4` for controlled creativity
- Logs token usage per call to `logs/openai_usages.jsonl`
- Reads API key from `OPENAI_API_KEY` environment variable (or `.env` file)

### Prompt Design (`src/prompts/`)

- **Instruction prompts** use a "red teaming" framing: generate harmful content to help users recognize misinformation. Requirements enforce unclear context, no predictable warnings, and Vietnamese language output.
- **Response prompts** use a "researcher/guardian" framing: analyze the harmful instruction and generate a rejection with reasoning. Requirements enforce information verification from the provided document and clear step-by-step reasoning.

---

## Ethical Considerations

This tool generates **harmful, misleading, or sensitive content** by design. It is intended solely for:

- **LLM safety research**: Training models to recognize and refuse harmful inputs
- **Guardrail development**: Building content moderation systems
- **Red-teaming evaluations**: Stress-testing model safety mechanisms

**Do NOT use this tool to:**
- Generate actual disinformation or hate speech for real-world use
- Train models without proper safety alignment
- Harass, deceive, or harm individuals or groups

If you use this tool in your research, please:
1. Clearly document the synthetic nature of the data
2. Ensure compliance with your institution's ethics guidelines
3. Never deploy models trained on this data without thorough safety evaluation

---

## Citation

If you use this tool in your research, please cite the repository:

```bibtex
@misc{llmharmfulgenerator,
  author = {NTHuyne},
  title = {LLMHarmfulGenerator},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/NTHuyne/LLMHarmfulGenerator}
}
```

---

## License

This project is provided for academic research purposes. See the license file for details.