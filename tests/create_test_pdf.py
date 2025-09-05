"""
Create a simple PDF file for testing the Awels PDF Processor.
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def create_test_pdf(output_path):
    """Create a simple PDF file with text and a simple table."""
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    # Add a title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "Test PDF Document")
    
    # Add some text
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 150, "This is a test PDF document created for testing the Awels PDF Processor.")
    c.drawString(100, height - 170, "It contains some text and a simple table.")
    
    # Add a simple table
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, height - 220, "Simple Table:")
    
    # Table headers
    c.setFont("Helvetica-Bold", 10)
    c.drawString(100, height - 250, "ID")
    c.drawString(150, height - 250, "Name")
    c.drawString(250, height - 250, "Value")
    
    # Table rows
    c.setFont("Helvetica", 10)
    for i in range(5):
        y_pos = height - 270 - (i * 20)
        c.drawString(100, y_pos, f"{i+1}")
        c.drawString(150, y_pos, f"Item {i+1}")
        c.drawString(250, y_pos, f"${(i+1) * 10}.00")
    
    # Add a second page
    c.showPage()
    
    # Add content to the second page
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "Page 2")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 150, "This is the second page of the test PDF document.")
    
    # Save the PDF
    c.save()
    print(f"Created test PDF at {output_path}")

if __name__ == "__main__":
    # Create the test_pdfs directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), "artifacts/test_pdfs")
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a test PDF file
    output_file = os.path.join(output_dir, "test_document.pdf")
    create_test_pdf(output_file)
    print(f"Created test PDF: {output_file}")
