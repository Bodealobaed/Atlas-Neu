"""Conservative Arabic/bilingual table quality gate; never silently repair numeric data."""
import re
import unicodedata

_ARABIC=re.compile(r'[\u0600-\u06ff]')
_BAD=re.compile(r'[\ufffd\u200b\u200c\u200d]')
_DIGIT_MAP=str.maketrans('٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹','01234567890123456789')

def normalize_cell(value):
    """Normalize encoding and presentation forms; preserve digits and punctuation."""
    value=unicodedata.normalize('NFKC',str(value if value is not None else ''))
    value=value.replace('\ufeff','').replace('\u00a0',' ')
    return re.sub(r'[ \t]+',' ',value).strip()

def audit_table(rows):
    """Return quality flags and a faithful normalized copy; never invent corrections."""
    result=[];issues=[]
    if not isinstance(rows,list):return {'rows':[],'issues':['not_a_row_list'],'requires_review':True}
    lengths=[]
    for ri,row in enumerate(rows):
        if not isinstance(row,list):
            issues.append(f'row_{ri+1}_invalid');continue
        lengths.append(len(row));clean=[]
        for ci,v in enumerate(row):
            cell=normalize_cell(v);clean.append(cell)
            if _BAD.search(cell):issues.append(f'row_{ri+1}_cell_{ci+1}_corrupt_character')
            if not cell:issues.append(f'row_{ri+1}_cell_{ci+1}_empty')
            if any(unicodedata.category(ch)=='Cc' and ch not in '\n\t' for ch in cell):
                issues.append(f'row_{ri+1}_cell_{ci+1}_control_character')
        result.append(clean)
    if lengths and len(set(lengths))!=1:issues.append('ragged_columns')
    return {'rows':result,'issues':issues,'requires_review':bool(issues),'verified':False}

def compare_ocr_passes(first,second):
    """Require exact agreement on numeric tokens across independent OCR passes."""
    numbers=lambda value:re.findall(r'(?<!\w)[+-]?\d+(?:[.,٫]\d+)?%?',str(value).translate(_DIGIT_MAP))
    a=numbers(first);b=numbers(second)
    return {'numeric_match':a==b,'first_numbers':a,'second_numbers':b,'requires_review':a!=b}
