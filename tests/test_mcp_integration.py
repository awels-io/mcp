"""
Integration test for the MCP server.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_request(method: str, params: dict) -> dict:
    """Send a request to the MCP server via stdio."""
    # Create a request object
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }
    
    # Convert to JSON and add Content-Length header
    request_json = json.dumps(request)
    message = f"Content-Length: {len(request_json)}\r\n\r\n{request_json}"
    
    # Print the message to stdout (which is connected to the server's stdin)
    print(message, file=sys.stdout, flush=True)
    
    # Read the response
    response = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
    return json.loads(response)

async def test_process_pdf():
    """Test the process_pdf method."""
    # Set up test directories
    test_dir = os.path.join(os.path.dirname(__file__), "artifacts/test_pdfs")
    md_output = os.path.join(os.path.dirname(__file__), "artifacts/test_output_md")
    img_output = os.path.join(os.path.dirname(__file__), "artifacts/test_output_images")
    
    # Create output directories if they don't exist
    os.makedirs(md_output, exist_ok=True)
    os.makedirs(img_output, exist_ok=True)
    
    # Send the process_pdf request
    response = await send_request("process_pdf", {
        "directory": test_dir,
        "recursive": True,
        "markdown_output_path": md_output,
        "images_dir": img_output
    })
    
    print("Response:", json.dumps(response, indent=2))
    
    # Check if the request was successful
    if "result" in response and response["result"].get("status") == "success":
        print("Test passed!")
    else:
        print("Test failed!")
        print("Error:", response.get("error", "Unknown error"))

async def main():
    """Run the test."""
    try:
        await test_process_pdf()
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
