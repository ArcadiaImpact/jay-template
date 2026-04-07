# Reference Stubs

This directory contains annotated example evaluations that demonstrate common patterns. **Do not edit these files in place** — copy them into your `src/` and `tests/` directories and adapt them for your evaluation.

## Available Stubs

### `simple_qa/` — Simple Q&A Evaluation

The most common pattern. Loads a dataset from HuggingFace, presents questions to the model, and scores responses with `match()`.

**When to use:** Multiple-choice, short-answer, or factual Q&A evaluations.

**Key patterns demonstrated:**

- Loading and pinning HuggingFace datasets with `hf_dataset()`
- `record_to_sample()` conversion
- Prompt templates as module-level constants
- `match()` scorer with numeric extraction
- Few-shot prompting
- End-to-end tests with `mockllm/model`

### `llm_judge/` — LLM-as-Judge Evaluation

Uses a language model to score open-ended responses. Demonstrates model-graded scoring with custom rubrics.

**When to use:** Evaluations where responses are open-ended and cannot be scored with exact match (e.g., writing quality, helpfulness, safety).

**Key patterns demonstrated:**

- `model_graded_qa()` scorer with custom templates
- Model roles for the judge model
- Score explanations
- Testing CORRECT/INCORRECT paths

### `agentic/` — Agentic Evaluation with Docker Sandbox

Agent-based evaluation where the model uses tools in a sandboxed environment. Demonstrates the full agentic eval pattern with Docker.

**When to use:** Evaluations where the model needs to take actions (run code, use tools, navigate an environment).

**Key patterns demonstrated:**

- `basic_agent()` solver with tools
- Docker sandbox via `compose.yaml`
- `bash()` and `python()` tools
- Message limits and turn management
- `@pytest.mark.docker` test markers
- Sandbox mocking in tests

## How to Use

1. Choose the stub that best matches your evaluation pattern
2. Copy the files into your `src/<eval_name>/` and `tests/<eval_name>/` directories
3. Rename files and update imports to match your eval name
4. Replace placeholder values (marked with `# STUB:` comments)
5. Run `make check` and `make test` to verify
