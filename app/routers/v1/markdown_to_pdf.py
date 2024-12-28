import os
from datetime import datetime
from async_lru import alru_cache
from markdown_pdf import MarkdownPdf, Section

from app.utils import sanitize_filename, upload_file_to_s3


def markdown_to_pdf(markdown: str, keywords: str):

    keywords = sanitize_filename(keywords.lower())

    pdf = MarkdownPdf()
    pdf.meta["title"] = keywords
    pdf.add_section(Section(markdown, toc=False))

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = keywords+"_"+timestamp+".pdf"
    file_path = f"/tmp/{file_name}"
    pdf.save(file_path)

    return file_path


@alru_cache(maxsize=128, ttl=60*60*1)
async def generate_pdf(markdown: str, keywords: str):
    # print(markdown)
    file_path = markdown_to_pdf(markdown, keywords)
    pdf_url = upload_file_to_s3(file_path)
    os.remove(file_path)
    return pdf_url
