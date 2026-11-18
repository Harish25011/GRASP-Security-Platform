import docx
import sys

def extract_text(filename):
    doc = docx.Document(filename)
    full_text = []
    for para in doc.paragraphs:
        if para.text.strip():
            full_text.append(para.text.strip())
    
    with open(sys.argv[2], 'w', encoding='utf-8') as f:
        f.write('\n'.join(full_text))

if __name__ == '__main__':
    extract_text(sys.argv[1])
