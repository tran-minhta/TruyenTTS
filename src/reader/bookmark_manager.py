import json
import os


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
BOOKMARKS_FILE = os.path.join(DATA_DIR, 'bookmarks.json')
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_bookmarks():
    ensure_data_dir()
    if not os.path.exists(BOOKMARKS_FILE):
        return []
    with open(BOOKMARKS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_bookmarks(bookmarks):
    ensure_data_dir()
    with open(BOOKMARKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(bookmarks, f, ensure_ascii=False, indent=2)


def add_bookmark(file_path, chapter_index, sentence_index, chapter_title, text_preview):
    bookmarks = load_bookmarks()
    entry = {
        'file_path': file_path,
        'chapter_index': chapter_index,
        'sentence_index': sentence_index,
        'chapter_title': chapter_title,
        'text_preview': text_preview[:80],
        'timestamp': None,
    }
    bookmarks.append(entry)
    save_bookmarks(bookmarks)
    return entry


def load_config():
    ensure_data_dir()
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_config(config):
    ensure_data_dir()
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
