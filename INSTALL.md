# Installation Guide

This guide will help you set up and install the Awels MCP PDF Processor.

## Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

## Installation with uv

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd awels-mcp
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

## Development Setup

1. Install development dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```

2. Run tests:
   ```bash
   pytest tests/
   ```

## Running the Server

To start the MCP server:

```bash
python -m src.awels_mcp.run_server
```

## Using the Client

To run the test client:

```bash
python tests/test_client.py
```

## Package Management with uv

- List installed packages:
  ```bash
  uv pip list
  ```

- Add a new dependency:
  ```bash
  uv pip install <package-name>
  ```

- Update all dependencies:
  ```bash
  uv pip compile --upgrade
  ```

- Freeze dependencies:
  ```bash
  uv pip freeze > requirements.txt
  ```

## Troubleshooting

If you encounter any issues:

1. Make sure all dependencies are installed
2. Check that you're using the correct Python version
3. Ensure you've activated the virtual environment
4. Check the test output for any error messages
