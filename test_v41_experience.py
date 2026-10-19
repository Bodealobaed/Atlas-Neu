from medical_experience import localized, explain_stats, summarize_evidence

def test_german_labels():
    assert 'Evidenz' in localized('Deutsch','automatic_title')
    assert 'Pixel' in explain_stats({'pixel_count':150,'mean_intensity':32},'Deutsch')

def test_arabic_labels():
    assert 'تحليل' in localized('العربية','analyze_button')
    assert 'تقنية' in explain_stats({},'العربية')

def test_evidence_is_not_diagnosis():
    text=summarize_evidence({'literature':{'records':[{'title':'a'}]}},'English')
    assert '1' in text and 'Not clinical confirmation' in text
