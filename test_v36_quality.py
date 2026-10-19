from table_quality import audit_table,compare_ocr_passes

def test_arabic_cells_preserved():
    x=audit_table([['الدواء','الجرعة'],['كلوزابين','١٢٫٥ ملغ']])
    assert x['rows'][1][1]=='١٢٫٥ ملغ'
    assert not x['requires_review']
    assert x['verified'] is False

def test_corrupt_and_ragged_flagged():
    x=audit_table([['العنوان','الكمية'],['�']])
    assert x['requires_review']
    assert 'ragged_columns' in x['issues']

def test_disagreement_numeric():
    assert compare_ocr_passes('١٢٫٥','١٣٫٥')['requires_review']
