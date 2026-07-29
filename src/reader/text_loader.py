import os
import re
from bs4 import BeautifulSoup


def load_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.txt':
        return load_txt(path)
    elif ext == '.epub':
        return load_epub(path)
    else:
        raise ValueError(f"Không hỗ trợ định dạng: {ext}")


def load_txt(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    name = os.path.splitext(os.path.basename(path))[0]
    return [(name, text)]


def load_epub(path):
    import ebooklib
    from ebooklib import epub
    book = epub.read_epub(path)
    chapters = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), 'lxml')
            for tag in soup(['script', 'style', 'nav']):
                tag.decompose()
            text = soup.get_text()
            text = re.sub(r'\s*\n\s*', '\n', text)
            text = re.sub(r'[ \t]+', ' ', text)
            text = text.strip()
            if not text:
                continue
            title_tag = soup.find('title')
            chapter_title = title_tag.get_text().strip() if title_tag else item.get_name()
            chapters.append((chapter_title, text))
    return chapters
