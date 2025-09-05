"""
Direct test of the PDF processor without MCP server.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to sys.path to import MCP modules
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    # Import the processor function
    from src.awels_mcp.pdf_processor import process_pdf_files
    
    # Set up test paths
    test_dir = os.path.join(os.path.dirname(__file__), "artifacts/test_pdfs")
    md_output = os.path.join(os.path.dirname(__file__), "artifacts/test_output_md")
    img_output = os.path.join(os.path.dirname(__file__), "artifacts/test_output_images")
    
    # Create output directories
    os.makedirs(md_output, exist_ok=True)
    os.makedirs(img_output, exist_ok=True)
    
    # Check for PDFs
    pdf_files = [f for f in os.listdir(test_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print(f"No PDF files found in {test_dir}. Please add some PDF files to test.")
        return
    
    print(f"Found PDF files: {pdf_files}")
    print(f"Processing PDFs in {test_dir}...")
    print(f"Markdown output will be saved to {md_output}")
    print(f"Images will be saved to {img_output}")
    
    try:
        # Process the PDF files
        print(f"\nCalling process_pdf_files with directory: {test_dir}")
        print(f"Markdown output path: {md_output}")
        print(f"Images output path: {img_output}")
        
        results = process_pdf_files(
            test_dir,
            markdown_output_path=md_output,
            images_dir=img_output
        )
        
        print("\nRaw results:", results)
        
        if not results:
            print("No results returned from process_pdf_files")
            return
            
        # Print the summary
        if "summary" in results:
            print("\nProcessing Summary:")
            for key, value in results["summary"].items():
                print(f"  {key}: {value}")
        else:
            print("\nNo summary found in results")
        
        # Print details for each file
        print("\nProcessed Files:")
        for file_path, file_info in results.items():
            if file_path == "summary":
                continue
                
            print(f"\n  File: {file_path}")
            if file_info is None:
                print("  No file info available")
                continue
                
            if isinstance(file_info, dict):
                if "error" in file_info:
                    print(f"  Error: {file_info['error']}")
                else:
                    print(f"  Pages: {file_info.get('pages', 'N/A')}")
                    print(f"  Markdown file: {file_info.get('markdown_file', 'N/A')}")
                    if "extracted_images" in file_info:
                        print(f"  Extracted images: {len(file_info['extracted_images'])}")
            else:
                print(f"  Unexpected file info type: {type(file_info)}")
        
    except Exception as e:
        import traceback
        print(f"\nError processing PDFs: {e}")
        print("\nTraceback:")
        traceback.print_exc()
    
    print("Test completed.")

if __name__ == "__main__":
    main()
