from pypdf import PdfReader
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
reader = PdfReader('C:/Users/D/Downloads/SRD_CC_v5.1_ES.pdf')

# Pages 8 to 55 (0-indexed: 7 to 54)
output = BASE / 'temp_pdf_classes.txt'
with open(str(output), 'w', encoding='utf-8') as f:
    for i in range(7, min(55, len(reader.pages))):
        text = reader.pages[i].extract_text()
        f.write(f'\n=== PAGE {i+1} ===\n')
        f.write(text)

print(f'Extracted pages 8-55 to {output}')
print(f'Total chars: {output.stat().st_size}')
