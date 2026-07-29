import re


def split_sentences(text):
    paragraphs = re.split(r'\n\s*\n', text)
    sentences = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        para = re.sub(r'\s*\n\s*', ' ', para)
        parts = re.split(r'(?<=[.!?])\s+', para)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if part and not part[-1] in '.!?':
                part += '.'
            sentences.append(part)
    return sentences
