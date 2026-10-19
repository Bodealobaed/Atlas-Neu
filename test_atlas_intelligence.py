from atlas_intelligence import extract_quantitative_evidence, automatic_evidence

def test_units_are_grounded():
    r=extract_quantitative_evidence('Dose was 15 mg and pressure 120 mmHg.\nE = m*c**2')
    assert [m['unit'] for m in r['measurements']]==['mg','mmHg']
    assert '15 mg' in r['measurements'][0]['source_excerpt']

def test_no_fake_measurements():
    assert extract_quantitative_evidence('No measurements were reported.')['measurements']==[]

def test_automatic_query_and_audit():
    captured={}
    def fake(query,domain):
        captured['query']=query
        return {'records':[{'title':'Radiology review','url':'https://example.org/1','relevance_score':0.5}]}
    result=automatic_evidence({'anatomy':'lung','observations':['lower lobe opacity']},retrieval=fake)
    assert 'chest radiograph' in captured['query']
    assert len(result['findings'])==1
    assert 'does not validate' in result['assessment']
