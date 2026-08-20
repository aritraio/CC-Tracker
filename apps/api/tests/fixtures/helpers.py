import io

import pymupdf


def create_pdf_from_text(pages_text: list[str] | str) -> io.BytesIO:
    """
    Generate an in-memory PDF stream from given text pages using PyMuPDF.
    Adheres strictly to privacy rules: 100% in-memory BytesIO buffer, zero disk writes.
    """
    if isinstance(pages_text, str):
        pages_text = [pages_text]

    doc = pymupdf.open()
    for text in pages_text:
        page = doc.new_page(width=595, height=842)  # A4 standard
        # Insert multiline text
        page.insert_text((50, 50), text, fontsize=10)

    pdf_bytes = doc.write()
    doc.close()

    stream = io.BytesIO(pdf_bytes)
    stream.seek(0)
    return stream
