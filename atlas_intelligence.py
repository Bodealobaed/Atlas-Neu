"""ATLAS EAST research intelligence: auditable retrieval, not a clinical diagnostic model.
No images, patient identifiers or private text are sent to literature APIs.
"""
import re
from dataclasses import dataclass
from typing import Callable
from literature_intelligence import federated_search

@dataclass(frozen=True)
class EvidenceFinding:
    statement: str
    evidence_url: str
    relevance: float
    status: str = 'research lead; not verified against this case'

MEDICAL = {'chest':'chest radiograph pulmonary findings', 'lung':'chest radiograph pulmonary findings',
           'brain':'brain MRI radiology findings', 'knee':'knee radiograph musculoskeletal findings',
           'heart':'cardiac imaging radiology findings', 'bone':'musculoskeletal radiograph findings'}

NUMERIC = re.compile(r'(?<!\w)([-+]?\d+(?:[.,]\d+)?)\s*(mg/mL|µg/mL|mg|µg|mmHg|kPa|MPa|GPa|mV|V|mA|A|mm|cm|nm|°C|%|Hz|kHz|mol/L|mM|µM)\b',re.I)
EQUATIONS = re.compile(r'(?m)^.{0,100}(?:[A-Za-zα-ωΑ-Ω][\wα-ωΑ-Ω]{0,12}\s*=\s*[^\n]{2,100}).{0,20}$')

def extract_quantitative_evidence(text: str, max_items=80):
    """Extract source-anchored measurements and equations, without fabricating values."""
    text = str(text or '')
    measurements = []
    for match in NUMERIC.finditer(text):
        context = text[max(0,match.start()-110):min(len(text),match.end()+110)].replace('\n',' ')
        measurements.append({'value':match.group(1),'unit':match.group(2),'source_excerpt':context.strip(), 'offset':match.start()})
        if len(measurements)>=max_items: break
    equations = []
    for match in EQUATIONS.finditer(text):
        expr=match.group(0).strip()
        if len(expr)>5 and len(expr)<160: equations.append({'expression':expr,'offset':match.start()})
        if len(equations)>=max_items: break
    return {'measurements':measurements,'equations':equations,
            'limitations':'Extracted candidates require verification against the original tables, units, methods and source pages.'}

def automatic_evidence(visual_terms, domain='medical', retrieval:Callable=federated_search):
    """Use de-identified image observations, never uploaded pixels, for background literature retrieval."""
    observations=visual_terms.get('observations',[]) if isinstance(visual_terms,dict) else []
    terms=[str(t).strip() for t in observations if isinstance(t,str) and len(t.strip())>3]
    anatomy=str(visual_terms.get('anatomy','') if isinstance(visual_terms,dict) else '').lower()
    topic=next((v for k,v in MEDICAL.items() if k in anatomy), 'medical imaging research') if domain=='medical' else domain+' scientific methods'
    # Avoid identifiable or unbounded input; only use short model-generated descriptors.
    cleaned=[re.sub(r'[^\w\s-]',' ',t)[:55] for t in terms[:3]]
    query=' '.join([topic]+cleaned)[:160]
    result=retrieval(query,domain=domain)
    leads=[EvidenceFinding(r['title'],r['url'],float(r.get('relevance_score',0))) for r in result.get('records',[]) if r.get('url')]
    return {'query':query,'findings':[f.__dict__ for f in leads], 'provider_errors':result.get('provider_errors',[]),
            'assessment':'Scientific context only. Article similarity does not validate an image finding or predict disease. A validated modality-specific model and external testing are required.'}
