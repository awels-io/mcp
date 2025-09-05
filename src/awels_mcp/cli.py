"""
Command-line interface for the AWELS PDF Processor.
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List, Union

from mcp.server.stdio import stdio_server
from mcp.server import Server
from mcp.types import Tool, TextContent

from awels_mcp.pdf_processor import process_pdf_files

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the MCP server
server = Server("awels-pdf-processor")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="process_pdf",
            description="Process PDF files in a directory and convert them to Markdown with image extraction",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory containing PDF files to process"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Whether to search for PDFs in subdirectories",
                        "default": True
                    },
                    "markdown_output_path": {
                        "type": "string",
                        "description": "Directory to save Markdown output (optional)"
                    },
                    "images_dir": {
                        "type": "string", 
                        "description": "Directory to save extracted images (optional)"
                    }
                },
                "required": ["directory"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle tool calls."""
    if name == "process_pdf":
        try:
            directory = arguments.get("directory")
            recursive = arguments.get("recursive", True)
            markdown_output_path = arguments.get("markdown_output_path")
            images_dir = arguments.get("images_dir")
            
            if not directory:
                raise ValueError("Directory parameter is required")
                
            # Process the PDF files
            results = process_pdf_files(
                directory=directory,
                recursive=recursive,
                markdown_output_path=markdown_output_path,
                images_dir=images_dir
            )
            
            return [TextContent(
                type="text",
                text=json.dumps({"status": "success", "data": results}, indent=2)
            )]
            
        except Exception as e:
            logger.error(f"Error processing PDFs: {str(e)}", exc_info=True)
            return [TextContent(
                type="text", 
                text=json.dumps({"status": "error", "message": str(e)}, indent=2)
            )]
    else:
        raise ValueError(f"Unknown tool: {name}")


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(description="AWELS PDF Processor")
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Process command
    process_parser = subparsers.add_parser("process", help="Process PDF files")
    process_parser.add_argument(
        "directory", 
        type=str, 
        help="Directory containing PDF files to process"
    )
    process_parser.add_argument(
        "--recursive", 
        action="store_true", 
        default=True,
        help="Search for PDFs in subdirectories (default: True)"
    )
    process_parser.add_argument(
        "--markdown-output", 
        type=str, 
        help="Directory to save Markdown output"
    )
    process_parser.add_argument(
        "--images-dir", 
        type=str, 
        help="Directory to save extracted images"
    )
    
    # Server command
    server_parser = subparsers.add_parser("serve", help="Start the MCP server")
    
    return parser


async def run_server():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command == "process":
        # Process PDFs directly
        results = process_pdf_files(
            directory=args.directory,
            recursive=args.recursive,
            markdown_output_path=args.markdown_output,
            images_dir=args.images_dir
        )
        print(json.dumps(results, indent=2))
    elif args.command == "serve":
        # Start the MCP server
        asyncio.run(run_server())
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
