"""
PDF processing module for handling PDF to Markdown conversion with image extraction.
"""

import os
import glob
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from docling_core.types.doc import ImageRefMode, PictureItem, TableItem
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

_log = logging.getLogger(__name__)

IMAGE_RESOLUTION_SCALE = 2.0


def process_pdf_files(
    directory: str,
    recursive: bool = True,
    markdown_output_path: Optional[str] = None,
    images_dir: Optional[str] = None
) -> Dict[str, Any]:
    """Find PDF files in a directory and convert them to Markdown.
    
    This function combines the functionality of searching for PDF files and converting them to Markdown.
    It first searches for all PDF files in the specified directory (and subdirectories if recursive is True),
    then converts each found PDF to Markdown format.
    
    Args:
        directory: The directory path to search for PDF files.
        recursive: Whether to search recursively in subdirectories. Defaults to True.
        markdown_output_path: Path to the target directory where to save the markdown files.
            The files will be saved with the same name as the PDFs but with .md extension.
            If None, the files will be saved in the current directory. Defaults to None.
        images_dir: Directory where to extract images from the PDFs.
            If None, images are not extracted. Defaults to None.
    
    Returns:
        A dictionary containing the results of the conversion for each file.
        Returns a dict with file paths as keys and their respective conversion results as values,
        plus a 'summary' key with overall stats (total files, successful/failed counts, etc.).
    """
    # PART 1: Search for PDF files
    files = []
    
    if not os.path.exists(directory):
        return {"error": f"Directory not found: {directory}"}
    
    if not os.path.isdir(directory):
        return {"error": f"Not a directory: {directory}"}
    
    # Pattern for finding PDF files
    pattern = os.path.join(directory, "**/*.pdf" if recursive else "*.pdf")
    
    # Find all PDF files
    for pdf_path in glob.glob(pattern, recursive=recursive):
        if os.path.isfile(pdf_path):
            # Get file stats
            stats = os.stat(pdf_path)
            
            # Add file info to results
            files.append({
                'path': pdf_path,
                'name': os.path.basename(pdf_path),
                'size': stats.st_size,
                'modified': stats.st_mtime
            })
    
    if not files:
        return {"summary": {"total_files": 0, "message": "No PDF files found in the specified directory"}}
    
    # PART 2: Convert PDF files to Markdown
    # Create a unique temporary directory for this process
    tmp_dir = "/tmp/docling_awels"
    os.makedirs(tmp_dir, exist_ok=True)
    _log.info(f"Using temporary directory: {tmp_dir}")

    # Critical: Override the HOME environment variable to redirect .cache
    os.environ["HOME"] = tmp_dir

    # Redirect all cache directories to /tmp
    os.environ["EASYOCR_MODULE_PATH"] = f"{tmp_dir}/easyocr"
    os.environ["DOCLING_ARTIFACTS_PATH"] = f"{tmp_dir}/docling/artifacts"
    # Hugging Face
    os.environ["HF_HOME"] = f"{tmp_dir}/huggingface"
    os.environ["HF_HUB_CACHE"] = f"{tmp_dir}/huggingface/cache"
    os.environ["HF_DATASETS_CACHE"] = f"{tmp_dir}/huggingface/datasets"
    os.environ["TRANSFORMERS_CACHE"] = f"{tmp_dir}/huggingface/transformers"

    # Create all necessary directories
    for path in [
        os.environ["EASYOCR_MODULE_PATH"],
        os.environ["TRANSFORMERS_CACHE"],
        os.environ["HF_HOME"],
        os.environ["DOCLING_ARTIFACTS_PATH"],
        os.environ["HF_HUB_CACHE"],
        os.environ["HF_DATASETS_CACHE"],
    ]:
        os.makedirs(path, exist_ok=True)
    
    # Process multiple files
    results = {}
    summary = {
        "total_files": len(files),
        "successful": 0,
        "failed": 0,
        "total_pages": 0,
        "total_images_extracted": 0
    }
    
    for file_info in files:
        pdf_path = file_info['path']
        _log.info(f"Processing file: {pdf_path}")
        
        # Process the individual PDF file
        pdf_path_obj = Path(pdf_path)
        
        try:
            # Create result dictionary
            file_result = {
                "filename": pdf_path_obj.name,
                "name": file_info['name'],
                "size": file_info['size'],
                "modified": file_info['modified']
            }
            
            # Setup images directory if specified
            images_dir_path = None
            if images_dir:
                try:
                    images_dir_path = Path(images_dir)
                    images_dir_path.mkdir(parents=True, exist_ok=True)
                except PermissionError:
                    _log.warning(f"Permission denied when creating images directory: {images_dir}")
                    results[pdf_path] = {"error": f"Permission denied when creating images directory: {images_dir}"}
                    summary["failed"] += 1
                    continue
                except Exception as e:
                    _log.warning(f"Error creating images directory: {str(e)}")
                    results[pdf_path] = {"error": f"Error creating images directory: {str(e)}"}
                    summary["failed"] += 1
                    continue
            
            # Configure PDF pipeline options
            pipeline_options = PdfPipelineOptions()
            pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
            pipeline_options.generate_page_images = False  # Disable page images
            pipeline_options.generate_picture_images = True  # Only extract embedded images
            
            # Set artifacts path for OCR model to use our custom directory
            artifacts_path = os.environ["DOCLING_ARTIFACTS_PATH"]
            try:
                os.makedirs(artifacts_path, exist_ok=True)
            except PermissionError:
                _log.warning(f"Permission denied when creating artifacts directory: {artifacts_path}")
                # Try a fallback location in /tmp
                artifacts_path = os.path.join("/tmp", f"docling_artifacts_{os.getuid()}")
                try:
                    os.makedirs(artifacts_path, exist_ok=True)
                except Exception as e:
                    _log.error(f"Failed to create fallback artifacts directory: {str(e)}")
                    results[pdf_path] = {"error": f"Permission issues with model directories. Please check application permissions."}
                    summary["failed"] += 1
                    continue
            
            # Initialize document converter with proper options
            doc_converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(
                        pipeline_options=pipeline_options,
                        artifacts_path=artifacts_path
                    )
                }
            )
            
            # Convert the PDF document
            _log.info(f"Converting PDF: {pdf_path}")
            try:
                conv_result = doc_converter.convert(pdf_path)
                document = conv_result.document
            except PermissionError as e:
                _log.error(f"Permission error during PDF conversion: {str(e)}")
                results[pdf_path] = {"error": f"Permission denied during PDF conversion. Please check application permissions."}
                summary["failed"] += 1
                continue
            except Exception as e:
                _log.error(f"Error during PDF conversion: {str(e)}", exc_info=True)
                results[pdf_path] = {"error": f"Failed to convert PDF: {str(e)}"}
                summary["failed"] += 1
                continue
            
            # Extract metadata
            try:
                file_result["metadata"] = document.metadata.export_to_dict()
            except (AttributeError, TypeError):
                # If metadata export not supported, try direct access
                try:
                    file_result["metadata"] = {
                        "title": getattr(document.metadata, "title", ""),
                        "author": getattr(document.metadata, "author", ""),
                        "subject": getattr(document.metadata, "subject", ""),
                        "keywords": getattr(document.metadata, "keywords", "")
                    }
                except (AttributeError, TypeError):
                    file_result["metadata"] = {}
            
            # Get page count
            try:
                file_result["pages"] = len(document.pages)
            except (AttributeError, TypeError):
                file_result["pages"] = 0
            
            # Extract images if a directory is specified
            extracted_images = []
            
            if images_dir_path:
                doc_filename = pdf_path_obj.stem
                
                # Skip saving page images - we only want embedded images
                
                # Save images of figures and tables
                table_counter = 0
                picture_counter = 0
                
                for element, _level in document.iterate_items():
                    try:
                        if isinstance(element, TableItem):
                            table_counter += 1
                            element_image_filename = images_dir_path / f"{doc_filename}-table-{table_counter}.png"
                            with open(element_image_filename, "wb") as fp:
                                element.get_image(document).save(fp, "PNG")
                            extracted_images.append(str(element_image_filename))
                        
                        if isinstance(element, PictureItem):
                            picture_counter += 1
                            element_image_filename = images_dir_path / f"{doc_filename}-picture-{picture_counter}.png"
                            with open(element_image_filename, "wb") as fp:
                                element.get_image(document).save(fp, "PNG")
                            extracted_images.append(str(element_image_filename))
                    except PermissionError:
                        _log.warning(f"Permission denied when saving element image")
                    except Exception as e:
                        _log.warning(f"Error extracting image from document element: {e}")
                
                if extracted_images:
                    file_result["extracted_images"] = extracted_images
            
            # Extract tables if available
            try:
                tables = []
                for table_idx, table in enumerate(document.tables):
                    table_data = table.export_to_dict()
                    tables.append(table_data)
                
                if tables:
                    file_result["tables"] = tables
            except (AttributeError, TypeError):
                # No tables found or tables not supported
                pass
            
            # Generate markdown content
            if markdown_output_path:
                md_output_path = Path(markdown_output_path)
                md_output_path.mkdir(parents=True, exist_ok=True)
                markdown_file_path = md_output_path / f"{pdf_path_obj.stem}.md"
                try:
                    # Save markdown with appropriate image mode
                    if images_dir_path:
                        document.save_as_markdown(
                            markdown_file_path, 
                            image_mode=ImageRefMode.REFERENCED
                        )
                    else:
                        document.save_as_markdown(
                            markdown_file_path, 
                            image_mode=ImageRefMode.EMBEDDED
                        )
                    
                    file_result["markdown_file"] = str(markdown_file_path)
                except PermissionError:
                    _log.warning(f"Permission denied when saving markdown file: {markdown_file_path}")
                    file_result["markdown_file_error"] = f"Permission denied when saving markdown file"
                except Exception as e:
                    _log.warning(f"Error saving markdown file: {str(e)}")
                    file_result["markdown_file_error"] = f"Error saving markdown file: {str(e)}"
            
            # Get markdown content for return value
            try:
                # Use StringIO to capture markdown content
                from io import StringIO
                output = StringIO()
                
                if images_dir_path:
                    document.save_as_markdown(
                        output, 
                        image_mode=ImageRefMode.REFERENCED
                    )
                else:
                    document.save_as_markdown(
                        output, 
                        image_mode=ImageRefMode.EMBEDDED
                    )
                
                markdown_content = output.getvalue()
                output.close()
            except (AttributeError, TypeError):
                # Fallback to older API if needed
                try:
                    markdown_content = document.export_to_markdown(
                        images_dir=images_dir if images_dir else None
                    )
                except TypeError:
                    markdown_content = document.export_to_markdown()
            
            file_result["content"] = markdown_content
            
            # Store the result and update summary
            results[pdf_path] = file_result
            summary["successful"] += 1
            summary["total_pages"] += file_result.get("pages", 0)
            if "extracted_images" in file_result:
                summary["total_images_extracted"] += len(file_result["extracted_images"])
            
        except PermissionError as e:
            _log.error(f"Permission error: {str(e)}", exc_info=True)
            results[pdf_path] = {"error": f"Permission denied: {str(e)}. Please check application permissions."}
            summary["failed"] += 1
        except Exception as e:
            _log.error(f"Failed to convert PDF to Markdown: {str(e)}", exc_info=True)
            results[pdf_path] = {"error": f"Failed to convert PDF to Markdown: {str(e)}"}
            summary["failed"] += 1
    
    # Add summary to results
    results["summary"] = summary
    return results
