"""Consent-gated research memory and reproducible evidence retrieval.

No autonomous clinical training, no PHI, and no unvalidated diagnostic scores.
"""
import hashlib
import json
import math
import sqlite3
from pathlib import Path
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc).isoformat()


def _tokens(text):
    import re
    return set(re.findall(r'\w{3,}', (text or '').casefold(), flags=re.UNICODE))


class ResearchMemory:
    """Private durable SQLite-backed library; operator must supply persistent path.

    Saves only deidentified research summaries and numerical model artifacts, not patient images.
    """
    def __init__(self, path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS studies (
                id TEXT PRIMARY KEY, title TEXT NOT NULL, domain TEXT NOT NULL,
                summary TEXT NOT NULL, provenance TEXT NOT NULL, license TEXT NOT NULL,
                expert_reviewed INTEGER NOT NULL, created_at TEXT NOT NULL)''')
            db.execute('''CREATE TABLE IF NOT EXISTS models (
                id TEXT PRIMARY KEY, title TEXT NOT NULL, domain TEXT NOT NULL,
                provenance TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL)''')

    def connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def add_study(self, title, domain, summary, provenance, license, *, expert_reviewed=False, permission=False):
        if not (permission and expert_reviewed):
            raise ValueError('Documented permission and independent expert review are required')
        fields = [title, domain, summary, provenance, license]
        if any(not str(f).strip() for f in fields):
            raise ValueError('All study fields are required')
        if len(summary) > 12000:
            raise ValueError('Summary exceeds 12,000 characters')
        identifier = hashlib.sha256(('\x00'.join(fields)).encode('utf-8')).hexdigest()
        with self.connect() as db:
            db.execute('INSERT OR REPLACE INTO studies VALUES (?,?,?,?,?,?,?,?)',
                       (identifier, title, domain, summary, provenance, license, 1, _now()))
        return identifier

    def retrieve(self, query, domain=None, limit=8):
        terms = _tokens(query)
        if not terms:
            return []
        with self.connect() as db:
            if domain:
                rows = db.execute('SELECT id,title,domain,summary,provenance FROM studies WHERE domain=? AND expert_reviewed=1', (domain,)).fetchall()
            else:
                rows = db.execute('SELECT id,title,domain,summary,provenance FROM studies WHERE expert_reviewed=1').fetchall()
        results = []
        for ident, title, group, summary, provenance in rows:
            title_words = _tokens(title)
            words = _tokens(summary)
            score = (3 * len(terms & title_words) + len(terms & words)) / max(len(terms), 1)
            if score > 0:
                results.append({'id': ident[:12], 'title': title, 'domain': group,
                                'summary': summary[:2500], 'provenance': provenance,
                                'relevance_score': round(score, 3)})
        return sorted(results, key=lambda v: v['relevance_score'], reverse=True)[:max(1, min(int(limit), 30))]

    def save_model(self, title, domain, provenance, fitted_model, *, permission=False):
        if not permission:
            raise ValueError('Explicit permission to retain model results is required')
        if not all(str(x).strip() for x in (title, domain, provenance)):
            raise ValueError('Title, domain and provenance required')
        # Only finite numerical/scalar model metadata; never source patient data.
        payload = json.dumps(fitted_model, allow_nan=False, ensure_ascii=False)
        if len(payload) > 100000:
            raise ValueError('Model payload too large')
        identifier = hashlib.sha256((title + domain + provenance + payload).encode()).hexdigest()
        with self.connect() as db:
            db.execute('INSERT OR REPLACE INTO models VALUES (?,?,?,?,?,?)',
                       (identifier, title, domain, provenance, payload, _now()))
        return identifier

    def list_models(self, domain=None):
        with self.connect() as db:
            if domain:
                rows = db.execute('SELECT title,domain,provenance,payload FROM models WHERE domain=? ORDER BY created_at DESC LIMIT 30', (domain,)).fetchall()
            else:
                rows = db.execute('SELECT title,domain,provenance,payload FROM models ORDER BY created_at DESC LIMIT 30').fetchall()
        return [{'title': a, 'domain': b, 'provenance': c, 'model': json.loads(d)} for a,b,c,d in rows]


def evidence_assessment(reference_matches, literature):
    """Explain provenance and abstain from diagnosis; never transform similarity into disease probability."""
    references = [r for r in (reference_matches or []) if r.get('source') and r.get('reference_label')]
    papers = [p for p in (literature or []) if p.get('pmid') and p.get('title')]
    labels = sorted({r['reference_label'] for r in references})
    return {
        'reference_count': len(references), 'publication_count': len(papers),
        'reference_labels_observed': labels,
        'assessment': ('Research references and literature are available for manual review; '
                       'they do not establish patient-level pathology.' if (references or papers)
                       else 'Insufficient verified evidence; no disease inference.'),
        'diagnosis': None,
        'limitations': 'Not a validated clinical classifier. Expert review, modality-specific models and external validation required.'
    }
