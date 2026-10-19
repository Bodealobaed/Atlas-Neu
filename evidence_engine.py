"""Public literature evidence retrieval. No patient identifiers or images sent to PubMed."""
import re
import requests
from xml.etree import ElementTree as ET

ANATOMY_TERMS = {'Brain':'brain neuroimaging','Chest / Lung':'chest lung radiology','Heart':'cardiac imaging','Knee':'knee radiography','Other bone':'musculoskeletal radiology','Other':'medical imaging'}

def search_pubmed(anatomy, finding, limit=5, timeout=12):
    """Return cited public abstracts/metadata; NOT diagnostic labels or image matches."""
    finding = re.sub(r'[^\w\s\-]', ' ', str(finding or ''), flags=re.UNICODE).strip()[:110]
    if len(finding) < 3:
        raise ValueError('Enter a non-identifying disease, imaging finding or research term.')
    if any(ch in finding for ch in ('@','/','\\')):
        raise ValueError('Do not enter patient identifiers.')
    query = f'({ANATOMY_TERMS.get(anatomy, "medical imaging")}) AND ({finding}) AND (imaging OR radiology)'
    session = requests.Session()
    base='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    result=session.get(base+'esearch.fcgi',params={'db':'pubmed','term':query,'retmax':min(max(int(limit),1),10),'retmode':'json'},timeout=timeout)
    result.raise_for_status()
    ids=result.json().get('esearchresult',{}).get('idlist',[])
    if not ids:return []
    response=session.get(base+'efetch.fcgi',params={'db':'pubmed','id':','.join(ids),'rettype':'abstract','retmode':'xml'},timeout=timeout)
    response.raise_for_status()
    root=ET.fromstring(response.content)
    records=[]
    for article in root.findall('.//PubmedArticle'):
        pmid=article.findtext('.//MedlineCitation/PMID')
        title=' '.join(''.join(article.find('.//ArticleTitle').itertext()).split()) if article.find('.//ArticleTitle') is not None else ''
        abstracts=[' '.join(''.join(node.itertext()).split()) for node in article.findall('.//Abstract/AbstractText')]
        if pmid:records.append({'pmid':pmid,'title':title,'abstract':' '.join(abstracts)[:1800], 'url':'https://pubmed.ncbi.nlm.nih.gov/'+pmid+'/'})
    return records
