import logging
from ebooklib import epub

def parse_ebook(file_path):
    try:
        book = epub.read_epub(file_path)
        text = ""
        for item in book.get_items():
            if item.get_type() == 'text/html':  # The type for document items in EPUB
                text += item.get_body_content().decode('utf-8')
        return text
    except Exception as e:
        logging.error(f"Failed to parse eBook: {e}")
        raise
