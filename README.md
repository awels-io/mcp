# Awels MCP Server - PDF Processing Tool

A Model Context Protocol (MCP) server that provides PDF processing capabilities using docling. This server exposes a single tool to convert PDF files to Markdown format with optional image extraction, designed to run in isolated environments to avoid permission issues.

## Project Structure

```
awels-mcp/
├── src/
│   └── awels_mcp/
│       ├── pdf_processor/     # PDF processing functionality
│       │   └── __init__.py    # PDFProcessor implementation
│       ├── __init__.py        # Package initialization
│       ├── run_server.py      # Server entry point
│       └── server.py          # MCP server implementation
├── tests/                     # Test files
│   ├── artifacts/             # Test artifacts (PDFs, outputs)
│   │   ├── test_output_md/    # Generated markdown files
│   │   ├── test_output_images/# Extracted images
│   │   └── test_pdfs/         # Sample PDFs for testing
│   ├── test_client.py         # Test MCP client
│   ├── test_pdf_processor.py  # Unit tests for PDF processing
│   └── test_server.py         # Server tests
├── .gitignore
├── INSTALL.md                 # Installation instructions
├── LICENSE
├── PLAN.md
├── README.md                  # This file
├── pyproject.toml             # Project metadata and dependencies
└── requirements.txt           # Development dependencies
```

## Features

- **PDF to Markdown Conversion**: Convert PDF files to clean Markdown format using docling
- **Image Extraction**: Extract images from PDFs (page images, tables, figures)
- **Batch Processing**: Process multiple PDF files in a directory (with recursive search)
- **Structured Output**: Returns detailed JSON results with file metadata and processing statistics
- **Isolated Execution**: Designed to run with `uvx --isolated` to prevent permission issues
- **Error Handling**: Graceful handling of permission errors and processing failures

## Installation

See [INSTALL.md](INSTALL.md) for detailed installation instructions using `uv`.

## Quick Start

1. Install the package in development mode:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

2. Run the tests to verify the installation:

```bash
pytest tests/
```

3. Start the MCP server:

```bash
python -m src.awels_mcp.run_server
```

4. In a separate terminal, run the test client:

```bash
python tests/test_client.py
```

## Running Tests

The test suite includes:

- Unit tests for the PDF processor
- Integration tests for the MCP server
- End-to-end tests with the client

To run all tests:

```bash
pytest tests/
```

Test artifacts (generated markdown and images) are saved in the `tests/artifacts/` directory.

## Development

### Project Structure

- `src/awels_mcp/`: Main package source code
  - `pdf_processor/`: PDF processing functionality
  - `server.py`: MCP server implementation
  - `run_server.py`: Entry point for the MCP server

### Adding New Features

1. Create a new branch for your feature
2. Add tests for your feature in the appropriate test file
3. Implement your feature
4. Run tests to ensure everything works
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Integration with MCP Clients

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "awels-pdf-processor": {
      "command": "uvx",
      "args": [
        "--python=3.12",
        "--isolated", 
        "--from=git+https://github.com/your-org/awels-mcp.git",
        "awels-mcp-server"
      ]
    }
  }
}
```

## Tool Reference

### `convert_pdf`

Converts PDF files in a directory to Markdown with optional image extraction.

**Parameters:**
- `directory` (string, required): Directory path to search for PDF files
- `recursive` (boolean, optional): Whether to search recursively in subdirectories (default: true)
- `markdown_output_path` (string, optional): Directory to save markdown files
- `images_dir` (string, optional): Directory to extract images from PDFs

**Returns:**
Structured JSON with processing results:

```json
{
  "summary": {
    "total_files": 5,
    "successful": 4,
    "failed": 1,
    "total_pages": 120,
    "total_images_extracted": 25
  },
  "files": {
    "/path/to/file1.pdf": {
      "filename": "file1.pdf",
      "name": "file1.pdf",
      "size": 1024000,
      "modified": 1640995200.0,
      "pages": 10,
      "metadata": {
        "title": "Document Title",
        "author": "Author Name",
        "subject": "Document Subject"
      },
      "extracted_images": [
        "/path/to/images/file1-page-1.png",
        "/path/to/images/file1-table-1.png"
      ],
      "markdown_file": "/path/to/markdown/file1.md",
      "content": "# Document Title\n\nDocument content in markdown..."
    },
    "/path/to/file2.pdf": {
      "error": "Failed to convert PDF: Permission denied"
    }
  }
}
```

## Usage Examples

### Basic PDF Conversion

```bash
# Convert all PDFs in a directory to markdown (content returned in response)
convert_pdf(directory="/path/to/pdfs")
```

### Save Markdown Files

```bash
# Convert PDFs and save markdown files to disk
convert_pdf(
  directory="/path/to/pdfs",
  markdown_output_path="/path/to/output/markdown"
)
```

### Extract Images

```bash
# Convert PDFs and extract all images
convert_pdf(
  directory="/path/to/pdfs",
  markdown_output_path="/path/to/output/markdown",
  images_dir="/path/to/output/images"
)
```

### Non-Recursive Search

```bash
# Only process PDFs in the specified directory (no subdirectories)
convert_pdf(
  directory="/path/to/pdfs",
  recursive=false
)
```

## Architecture

The server uses:
- **FastMCP**: High-level MCP server framework for easy tool definition
- **docling**: Advanced PDF processing library for text and image extraction
- **Pydantic**: Data validation and structured output
- **Isolated execution**: Runs in isolated environment to prevent permission issues

## Error Handling

The server gracefully handles:
- Permission errors (designed to run in isolated environments)
- Missing directories
- Corrupted PDF files
- Processing failures
- File system errors

All errors are reported in the structured output with detailed error messages.

## Development

### Project Structure

```
awels/
├── src/
│   └── awels_mcp/
│       ├── __init__.py
│       ├── server.py          # Main MCP server implementation
│       └── pdf_processor.py   # PDF processing logic
├── pyproject.toml             # Package configuration
├── README.md                  # This file
└── PLAN.md                    # Development plan
```

### Running Tests

```bash
# Install development dependencies
uv sync --group dev

# Run tests (when available)
uv run pytest
```

### Code Formatting

```bash
# Format code
uv run black src/
uv run isort src/

# Type checking
uv run mypy src/
```

## Requirements

- Python 3.10+
- docling and docling-core libraries
- MCP Python SDK
- Sufficient disk space for temporary files and model downloads

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
- GitHub Issues: https://github.com/your-org/awels-mcp/issues
- Documentation: See PLAN.md for technical details