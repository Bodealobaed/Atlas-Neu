"""Run: python tests/test_v30_exports.py"""
from pathlib import Path
import sys, fitz
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PIL import Image
from medical_pdf import build_medical_pdf
from book import build_book_pdf

pdf=build_medical_pdf(Image.new('RGB',(240,180),'white'),{'file_type':'png','statistics':{'pixel_count':43200}},'Research only',language='English')
assert pdf.startswith(b'%PDF-')
with fitz.open(stream=pdf,filetype='pdf') as f:
    content='\n'.join(page.get_text() for page in f)
    assert 'Medical Image Research Report' in content
    assert 'pixel_count' in content

book={'language':'German','title':'Wissenschaftliche Analyse von Eisenmangel','preface':['Eine eigenständige Einführung in das Thema.'],'chapters':[{'heading':'Einleitung','page':1,'paragraphs':['Die untersuchte Fragestellung wird wissenschaftlich beschrieben.']}],'conclusion':['Grenzen der Forschung.']}
output=build_book_pdf({'name':'source.pdf','tables':[],'images':[]},book,author='Researcher')
with fitz.open(stream=output,filetype='pdf') as f:
    texts=[page.get_text() for page in f]
    assert 'Vorwort' in texts[1]
    assert 'Eine eigenständige Einführung' in texts[1]
    assert all('Originalquelle' not in t and 'KI-gestützte Buchbearbeitung' not in t for t in texts)
print('PASS: medical PDF and book cover/introduction PDF')
