import os
from weasyprint import HTML, CSS
from app.core.config import settings

def generate_pdf_from_html(html_content: str, output_filename: str) -> str:
    """
    Renders HTML content to a PDF file using WeasyPrint and returns the path.
    """
    # Ensure the directory exists
    os.makedirs(settings.PDF_OUTPUT_DIR, exist_ok=True)
    
    output_path = os.path.join(settings.PDF_OUTPUT_DIR, output_filename)
    
    # Generate the PDF
    # WeasyPrint supports CSS paged media for page-break-inside, sizes, margins, etc.
    # base_url is set to current directory to resolve local assets if any
    html = HTML(string=html_content, base_url=".")
    html.write_pdf(output_path)
    
    # Return the relative path for web access (e.g. static/pdfs/filename.pdf)
    # The actual saved path relative to project root is app/static/pdfs/filename.pdf,
    # but the URL served by FastAPI static files is /static/pdfs/filename.pdf.
    relative_path = f"/static/pdfs/{output_filename}"
    return relative_path
