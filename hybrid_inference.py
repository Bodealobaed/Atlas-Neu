"""Hybrid research inference gateway. No diagnosis is produced without a deployed, validated model.

The remote service must provide a versioned /v1/infer endpoint; requests contain only
rendered images, never DICOM headers or patient identifiers. Explicit consent is required.
"""
import base64
import hashlib
import io
import json
from dataclasses import dataclass
from typing import Mapping

SUPPORTED = {'chest_xray', 'brain_mri', 'knee_xray', 'cardiac', 'bone_xray'}

@dataclass(frozen=True)
class ModelCard:
    model_id: str
    version: str
    task: str
    modality: str
    validation_dataset: str
    license: str
    validated: bool


def validate_result(payload: Mapping, expected_modality: str) -> dict:
    """Reject fabricated confidence and incompatible/missing model provenance."""
    if expected_modality not in SUPPORTED:
        raise ValueError('Unsupported image task; a specialist model is required.')
    card = payload.get('model_card')
    if not isinstance(card, dict) or not all(card.get(k) for k in ('model_id','version','task','modality','license')):
        raise ValueError('Missing model provenance; no disease prediction can be displayed.')
    if card['modality'] != expected_modality:
        raise ValueError('Model modality mismatch.')
    findings = payload.get('findings', [])
    if not isinstance(findings, list):
        raise ValueError('Invalid findings.')
    cleaned=[]
    for item in findings[:20]:
        if not isinstance(item, dict) or not isinstance(item.get('label'),str):
            raise ValueError('Invalid model finding.')
        score=item.get('score')
        if not isinstance(score,(float,int)) or isinstance(score,bool) or not 0 <= score <= 1:
            raise ValueError('Model score must be a number in [0,1].')
        cleaned.append({'label':item['label'][:120], 'score':float(score),
                        'explanation':str(item.get('explanation',''))[:600]})
    return {'model_card':card, 'findings':cleaned,
            'validated':bool(card.get('validated',False) and card.get('validation_dataset')),
            'limitations':str(payload.get('limitations','Research model, not a clinical diagnosis.'))[:1000]}


def infer_remote(image, modality: str, endpoint: str, token: str, consent: bool, *, post=None) -> dict:
    if not consent:
        raise PermissionError('Explicit consent required before sending an image to a remote service.')
    if modality not in SUPPORTED:
        raise ValueError('No specialist model configured for this modality.')
    if not endpoint.startswith('https://'):
        raise ValueError('Remote inference requires HTTPS.')
    if not token:
        raise ValueError('Missing server access token.')
    import requests
    from PIL import Image
    if not isinstance(image, Image.Image):
        raise TypeError('A rendered, metadata-free PIL image is required.')
    buf=io.BytesIO()
    image.convert('RGB').save(buf,format='PNG')
    image_bytes=buf.getvalue()
    if len(image_bytes)>12_000_000:
        raise ValueError('Image too large for inference request.')
    body={'modality':modality, 'image_png_base64':base64.b64encode(image_bytes).decode('ascii'),
          'sha256':hashlib.sha256(image_bytes).hexdigest()}
    transport=post or requests.post
    response=transport(endpoint.rstrip('/')+'/v1/infer',json=body,
                       headers={'Authorization':'Bearer '+token},timeout=45)
    response.raise_for_status()
    return validate_result(response.json(),modality)


def format_findings(result:dict, language='English')->str:
    labels={'German':('Forschungsbefunde','Modell','Nicht klinisch validiert','Wahrscheinlichkeit des Modells, keine Diagnose'),
            'Arabic':('نتائج بحثية','النموذج','غير متحقق منه سريريًا','درجة النموذج ليست تشخيصًا'),
            'English':('Research findings','Model','Not clinically validated','Model score is not a diagnosis')}
    heading,model,warning,note=labels.get(language,labels['English'])
    card=result['model_card']
    lines=[f'### {heading}',f'**{model}:** {card["model_id"]} ({card["version"]})']
    if not result['validated']: lines.append(f'**{warning}**')
    for f in result['findings']: lines.append(f'- {f["label"]}: {f["score"]:.1%} — {f["explanation"]}')
    lines.append(f'*{note}*')
    return '\n\n'.join(lines)
