# Awels MCP Server - PDF Processing Tool

## Overview
This MCP server exposes a single tool `convert_pdf()` that processes PDF files in a directory using docling to extract text as Markdown and images. The server is designed to run in an isolated environment using `uvx --isolated` to avoid permission issues.

## Architecture

### MCP Server Structure
```
awels/
├── src/
│   └── awels_mcp/
│       ├── __init__.py
│       ├── server.py          # Main MCP server implementation
│       └── pdf_processor.py   # PDF processing logic adapted from original
├── pyproject.toml             # Package configuration
├── README.md                  # Usage instructions
└── PLAN.md                    # This file
```

### Tool Definition
**Tool Name**: `convert_pdf`

**Input Parameters**:
- `directory` (str): Directory path to search for PDF files
- `recursive` (bool, default=True): Whether to search recursively in subdirectories
- `markdown_output_path` (str, optional): Directory to save markdown files
- `images_dir` (str, optional): Directory to extract images

**Output**: Structured JSON with:
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
      "size": 1024000,
      "modified": 1640995200.0,
      "pages": 10,
      "metadata": {...},
      "extracted_images": ["/path/to/images/file1-page-1.png", ...],
      "markdown_file": "/path/to/markdown/file1.md",
      "content": "# Document Title\n..."
    },
    "/path/to/file2.pdf": {
      "error": "Failed to convert PDF: Permission denied"
    }
  }
}
```

## Implementation Details

### Dependencies
- `mcp[cli]`: MCP Python SDK
- `docling`: PDF processing library
- `docling-core`: Core docling types
- Standard library: `os`, `glob`, `logging`, `pathlib`

### Key Features
1. **Isolated Execution**: Designed to run with `uvx --isolated` for permission isolation
2. **Structured Output**: Returns JSON with file metadata and processing results
3. **Error Handling**: Graceful handling of permission errors and processing failures
4. **Progress Reporting**: Uses MCP context for logging and progress updates
5. **Flexible Configuration**: Supports optional markdown and image extraction

### Security Considerations
- Runs in isolated environment to prevent permission issues
- Validates input paths to prevent directory traversal
- Handles file system errors gracefully

## Deployment

### GitHub Repository
The tool will be published to the `awels-mcp` private GitHub repository and can be installed directly using:

```bash
uvx --python=3.12 --isolated --from=git+https://github.com/your-org/awels-mcp.git awels-mcp-server
```

### Local Development
For development and testing:
```bash
cd awels/
uv run mcp dev src/awels_mcp/server.py
```

## Usage Scenarios
1. **Batch PDF Processing**: Process all PDFs in a document directory
2. **Content Extraction**: Extract text and images for further processing
3. **Document Analysis**: Get metadata and statistics about PDF collections
4. **Automated Workflows**: Integration with other MCP tools for document pipelines