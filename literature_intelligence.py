"""Evidence retrieval and audit for medical and engineering research; never a diagnostic classifier."""
import re
import math
import requests
from urllib.parse import quote

STOP = {'with','from','that','this','study','research','image','medical','using','the','and','for','von','und','eine','einer','على','في','من','هذا','هذه'}

def sanitize_query(value):
    value = ' '.join(str(value or '').split())[:160]
    if not value or len(value) < 3:
        raise ValueError('Enter an anatomy, finding, scientific method or research topic.')
    if re.search(r'@|\b\d{5,}\b|(?:patient|name|dob|birth|address)\s*[:=]',value,re.I):
        raise ValueError('Potential identifying information detected. Use research terms only.')
    return value

def tokens(value):
    return set(w for w in re.findall(r'[^\W_]{3,}',str(value).lower(),re.U) if w not in STOP)

def _score(record, query):
    q=tokens(query)
    if not q:return 0.0
    title=tokens(record.get('title',''))
    abstract=tokens(record.get('abstract',''))
    return round((2*len(q & title)+len(q & abstract))/(2*len(q)),3)

def search_europe_pmc(query,limit=6,timeout=12,session=None):
    query=sanitize_query(query)
    s=session or requests
    response=s.get('https://www.ebi.ac.uk/europepmc/webservices/rest/search',params={'query':query,'format':'json','pageSize':min(15,max(1,int(limit))),'resultType':'core'},timeout=timeout)
    response.raise_for_status()
    results=[]
    for item in response.json().get('resultList',{}).get('result',[]):
        pmid=str(item.get('id','')) if item.get('source')=='MED' else ''
        doi=str(item.get('doi') or '')
        url=('https://pubmed.ncbi.nlm.nih.gov/'+pmid+'/' if pmid else ('https://doi.org/'+quote(doi,safe='/') if doi else ''))
        if not url:continue
        results.append({'source':'Europe PMC','title':item.get('title',''),'abstract':re.sub('<[^>]+>',' ',item.get('abstractText') or '')[:2200], 'doi':doi,'pmid':pmid,'url':url,'year':str(item.get('pubYear',''))})
    return results

def search_crossref(query,limit=6,timeout=12,session=None):
    query=sanitize_query(query)
    s=session or requests
    response=s.get('https://api.crossref.org/works',params={'query.bibliographic':query,'rows':min(15,max(1,int(limit))),'select':'DOI,title,abstract,published,URL,type'},headers={'User-Agent':'ATLAS-EAST/3.4 (research evidence retrieval)'},timeout=timeout)
    response.raise_for_status()
    results=[]
    for item in response.json().get('message',{}).get('items',[]):
        doi=item.get('DOI','')
        if not doi:continue
        title=item.get('title', [''])
        year=((item.get('published') or {}).get('date-parts') or [[None]])[0][0]
        results.append({'source':'Crossref','title':title[0] if title else '', 'abstract':re.sub('<[^>]+>',' ',item.get('abstract') or '')[:2200], 'doi':doi,'pmid':'','url':'https://doi.org/'+quote(doi,safe='/'),'year':str(year or '')})
    return results

def federated_search(query,domain='medical',limit=8,timeout=12,providers=None):
    """Retrieve public scholarly metadata, deduplicate, rank; return explicit provider failures."""
    query=sanitize_query(query)
    sources=providers or ([search_europe_pmc,search_crossref] if domain=='medical' else [search_crossref,search_europe_pmc])
    records=[]; errors=[]; seen=set()
    for source in sources:
        try:
            for item in source(query,limit=limit,timeout=timeout):
                key=(item.get('doi') or item.get('pmid') or item.get('url') or '').lower().strip()
                if not key or key in seen:continue
                seen.add(key)
                item=dict(item); item['relevance_score']=_score(item,query)
                records.append(item)
        except (requests.RequestException,ValueError,KeyError,TypeError) as exc:
            errors.append(f'{getattr(source,"__name__","provider")}: {type(exc).__name__}')
    records.sort(key=lambda r:r['relevance_score'],reverse=True)
    return {'query':query,'domain':domain,'records':records[:limit],'provider_errors':errors,'notice':'Literature relevance is not patient-specific diagnostic evidence; article metadata is not an image reference standard.'}

def evidence_brief(records,observations,domain='medical'):
    """Create auditable non-diagnostic research prompts with grounded citations only."""
    observations=sanitize_query(observations)
    matches=[r for r in records if r.get('relevance_score',0)>0 and r.get('url')]
    return {'observations':observations,'domain':domain,'candidate_topics':[{'title':r['title'],'source':r['source'],'url':r['url'],'relevance_score':r['relevance_score']} for r in matches[:5]],'conclusion':'Research leads only. Do not diagnose disease, assert causality, or infer image findings from article similarity. Independent specialist assessment and validated models are required.'}
