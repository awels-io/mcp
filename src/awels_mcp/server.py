"""
Awels MCP Server - PDF Processing Tool
Exposes a single tool to convert PDF files to Markdown with image extraction.
"""

import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession
from .pdf_processor import process_pdf_files

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the MCP server
mcp = FastMCP(
    name="Awels PDF Processor",
    instructions="A PDF processing server that converts PDF files to Markdown with optional image extraction using docling."
)


class PDFProcessingResult(BaseModel):
    """Structured output for PDF processing results."""
    
    summary: Dict[str, Any] = Field(description="Summary statistics of the processing operation")
    files: Dict[str, Dict[str, Any]] = Field(description="Per-file processing results with metadata")


@mcp.tool()
async def convert_pdf(
    directory: str,
    recursive: bool = True,
    markdown_output_path: Optional[str] = None,
    images_dir: Optional[str] = None,
    ctx: Context[ServerSession, None] = None
) -> PDFProcessingResult:
    """Convert PDF files in a directory to Markdown with optional image extraction.
    
    This tool searches for PDF files in the specified directory and converts them to Markdown
    format using docling. It can optionally extract images and save markdown files to disk.
    
    Args:
        directory: Directory path to search for PDF files
        recursive: Whether to search recursively in subdirectories (default: True)
        markdown_output_path: Optional directory to save markdown files
        images_dir: Optional directory to extract images from PDFs
        
    Returns:
        Structured results containing processing summary and per-file details
    """
    if ctx:
        await ctx.info(f"Starting PDF conversion in directory: {directory}")
        await ctx.debug(f"Parameters - recursive: {recursive}, markdown_output: {markdown_output_path}, images_dir: {images_dir}")
    
    try:
        # Call the PDF processing function
        results = process_pdf_files(
            directory=directory,
            recursive=recursive,
            markdown_output_path=markdown_output_path,
            images_dir=images_dir
        )
        
        # Check if there was an error at the top level
        if "error" in results:
            if ctx:
                await ctx.error(f"PDF processing failed: {results['error']}")
            # Return error in structured format
            return PDFProcessingResult(
                summary={"total_files": 0, "successful": 0, "failed": 1, "error": results["error"]},
                files={}
            )
        
        # Extract summary and files from results
        summary = results.pop("summary", {})
        files = results
        
        if ctx:
            await ctx.info(f"Processing complete: {summary.get('successful', 0)} successful, {summary.get('failed', 0)} failed")
            if summary.get('total_images_extracted', 0) > 0:
                await ctx.info(f"Extracted {summary['total_images_extracted']} images")
        
        return PDFProcessingResult(
            summary=summary,
            files=files
        )
        
    except Exception as e:
        error_msg = f"Unexpected error during PDF processing: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        logger.exception("PDF processing failed")
        
        # Return error in structured format
        return PDFProcessingResult(
            summary={"total_files": 0, "successful": 0, "failed": 1, "error": error_msg},
            files={}
        )


def main():
    """Entry point for the MCP server."""
    import sys
    
    # Check if we're being called with specific transport
    if len(sys.argv) > 1 and sys.argv[1] in ["stdio", "sse", "streamable-http"]:
        transport = sys.argv[1]
    else:
        transport = "stdio"  # Default transport
    
    logger.info(f"Starting Awels MCP Server with {transport} transport")
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()