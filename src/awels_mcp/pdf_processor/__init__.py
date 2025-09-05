"""
PDF processing module for handling PDF to Markdown conversion with image extraction.

This module provides functionality to process PDF files, extract their content,
and convert them to Markdown format with support for embedded images and tables.
"""

from typing import Dict, Any, Optional

from .processor import process_pdf_files, IMAGE_RESOLUTION_SCALE

__all__ = ['process_pdf_files', 'IMAGE_RESOLUTION_SCALE']