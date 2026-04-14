# sparktest — AI Creativity Tester. Benchmark for measuring AI creative capabilities across domains

AI Creativity Tester. Benchmark for measuring AI creative capabilities across domains. sparktest gives you a focused, inspectable implementation of that idea.

## Why sparktest

sparktest exists to make this workflow practical. Ai creativity tester. benchmark for measuring ai creative capabilities across domains. It favours a small, inspectable surface over sprawling configuration.

## Features

- CLI command `sparktest`
- Included test suite
- Worked examples included

## Tech Stack

- **Runtime:** Python
- **Frameworks:** Click
- **Tooling:** Rich, Pydantic

## How It Works

The codebase is organised into `examples/`, `src/`, `tests/`. The primary entry points are `src/sparktest/cli.py`, `src/sparktest/__init__.py`. `src/sparktest/cli.py` exposes functions like `cli`, `score_uses`, `score_story`.

## Getting Started

```bash
pip install -e .
sparktest --help
```

## Usage

```bash
sparktest --help
```

## Project Structure

```
sparktest/
├── .env.example
├── CONTRIBUTING.md
├── README.md
├── config.example.yaml
├── examples/
├── index.html
├── pyproject.toml
├── src/
├── tests/
```
