import os
import re
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import pdfplumber

class BookParser:
    @staticmethod
    def parse_txt(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def parse_epub(file_path):
        book = epub.read_epub(file_path)
        text_content = []
        
        # Lọc qua các item chứa nội dung văn bản trong EPUB
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            soup = BeautifulSoup(item.get_body_content(), 'html.parser')
            # Lấy text và loại bỏ khoảng trắng thừa
            page_text = soup.get_text()
            if page_text.strip():
                text_content.append(page_text)
                
        return "\n\n".join(text_content)

    @staticmethod
    def parse_pdf(file_path):
        text_content = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
        return "\n\n".join(text_content)

    @classmethod
    def get_text(cls, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.txt':
            return cls.parse_txt(file_path)
        elif ext == '.epub':
            return cls.parse_epub(file_path)
        elif ext == '.pdf':
            return cls.parse_pdf(file_path)
        else:
            raise ValueError(f"Định dạng {ext} hiện chưa được hỗ trợ.")
