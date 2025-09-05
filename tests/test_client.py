"""
Simple MCP client to test the Awels PDF Processor server.
"""

import asyncio
import os
import subprocess
from mcp.client import Client

async def main():
    # Connect to the server
    print("Connecting to Awels PDF Processor server...")
    server_script = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src/awels_mcp/server.py")
    client = await Client.connect(f"python {server_script} stdio")
    
    print(f"Connected to server: {client.name}")
    print(f"Server instructions: {client.instructions}")
    
    # List available tools
    tools = await client.list_tools()
    print(f"Available tools: {[tool.name for tool in tools]}")
    
    # Create a test directory with a sample PDF
    test_dir = os.path.join(os.getcwd(), "test_pdfs")
    os.makedirs(test_dir, exist_ok=True)
    
    # Check if there are any PDFs in the test directory
    pdf_files = [f for f in os.listdir(test_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in {test_dir}. Please add some PDF files to test.")
        return
    
    # Create output directories
    md_output = os.path.join(os.path.dirname(__file__), "artifacts/test_output_md")
    img_output = os.path.join(os.path.dirname(__file__), "artifacts/test_output_images")
    
    os.makedirs(md_output, exist_ok=True)
    os.makedirs(img_output, exist_ok=True)
    
    print(f"Processing PDFs in {test_dir}...")
    print(f"Markdown output will be saved to {md_output}")
    print(f"Images will be saved to {img_output}")
    
    # Call the convert_pdf tool
    try:
        result = await client.call_tool(
            "convert_pdf",
            directory=test_dir,
            recursive=True,
            markdown_output_path=md_output,
            images_dir=img_output
        )
        
        # Print the summary
        print("\nProcessing Summary:")
        for key, value in result.summary.items():
            print(f"  {key}: {value}")
        
        # Print details for each file
        print("\nProcessed Files:")
        for file_path, file_info in result.files.items():
            print(f"\n  File: {file_path}")
            if "error" in file_info:
                print(f"  Error: {file_info['error']}")
            else:
                print(f"  Pages: {file_info.get('pages', 'N/A')}")
                print(f"  Markdown file: {file_info.get('markdown_file', 'N/A')}")
                if "extracted_images" in file_info:
                    print(f"  Extracted images: {len(file_info['extracted_images'])}")
        
    except Exception as e:
        print(f"Error calling convert_pdf: {e}")
    
    # Close the client
    await client.close()
    print("Test completed.")

if __name__ == "__main__":
    asyncio.run(main())
