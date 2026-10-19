"""Auditable research algorithms. No unvalidated disease classifier or autonomous self-training."""
from __future__ import annotations
import hashlib, io, json, math, sqlite3
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps

SCHEMA_VERSION=1

def image_descriptor(image):
    """Illumination-normalized multiscale intensity/edge descriptor; NOT a pathology embedding."""
    im=ImageOps.grayscale(image).resize((64,64),Image.Resampling.BILINEAR)
    a=np.asarray(im,dtype=np.float64)/255
    p1,p99=np.percentile(a,[1,99]); a=np.clip((a-p1)/max(p99-p1,1e-8),0,1)
    gy,gx=np.gradient(a)
    edge=np.hypot(gx,gy)
    features=[]
    for mat in (a,edge):
        for grid in (1,4,8):
            for block in np.array_split(mat,grid,axis=0):
                for cell in np.array_split(block,grid,axis=1):
                    features.append(float(cell.mean()))
    v=np.asarray(features,dtype=np.float64)
    norm=np.linalg.norm(v)
    return v/max(norm,1e-12)

def mask_metrics(predicted,reference,spacing_mm=None):
    """Evaluate a proposed segmentation against a trusted pixel-aligned reference mask."""
    a=np.asarray(predicted,dtype=bool); b=np.asarray(reference,dtype=bool)
    if a.shape!=b.shape or a.ndim!=2:raise ValueError('Masks must be aligned 2D arrays of equal shape')
    intersection=int(np.logical_and(a,b).sum()); na=int(a.sum()); nb=int(b.sum())
    dice=2*intersection/(na+nb) if na+nb else 1.0
    union=int(np.logical_or(a,b).sum()); iou=intersection/union if union else 1.0
    result={'dice':float(dice),'iou':float(iou),'predicted_pixels':na,'reference_pixels':nb,
            'interpretation':'Agreement with supplied reference only; not clinical accuracy.'}
    if spacing_mm is not None:
        sy,sx=map(float,spacing_mm[:2]);result['predicted_area_mm2']=na*sy*sx
    return result

class ReferenceLibrary:
    """Explicit opt-in, verified, non-identifiable research references only.

    Local SQLite is ephemeral on many cloud deployments. Mount durable private storage
    for persistence. Images are not stored; only noninvertible fingerprints and descriptors.
    """
    def __init__(self,path):
        self.path=str(path)
        Path(path).parent.mkdir(parents=True,exist_ok=True)
        with self._connect() as con:
            con.execute('''CREATE TABLE IF NOT EXISTS reference_cases
              (case_id TEXT PRIMARY KEY, modality TEXT NOT NULL, anatomy TEXT NOT NULL,
               label TEXT NOT NULL, source TEXT NOT NULL, license TEXT NOT NULL,
               verified INTEGER NOT NULL, descriptor TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    def _connect(self):return sqlite3.connect(self.path,timeout=10)
    def add(self,image,*,modality,anatomy,label,source,license,verified=False,consent=False):
        if not (consent and verified):raise ValueError('Explicit permission and verified reference label required')
        if not all(str(s).strip() for s in (modality,anatomy,label,source,license)):
            raise ValueError('Modality, anatomy, reference label, provenance and license required')
        descriptor=image_descriptor(image)
        raw=np.asarray(ImageOps.grayscale(image)).tobytes()
        case_id=hashlib.sha256(raw).hexdigest()
        with self._connect() as con:
            con.execute('INSERT OR REPLACE INTO reference_cases(case_id,modality,anatomy,label,source,license,verified,descriptor) VALUES(?,?,?,?,?,?,1,?)',
                        (case_id,modality,anatomy,label,source,license,json.dumps(descriptor.tolist())))
        return case_id
    def search(self,image,*,modality,anatomy,limit=5):
        q=image_descriptor(image)
        with self._connect() as con:
            rows=con.execute('SELECT case_id,label,source,license,descriptor FROM reference_cases WHERE modality=? AND anatomy=? AND verified=1',
                             (modality,anatomy)).fetchall()
        found=[]
        for case_id,label,source,license,vector in rows:
            v=np.asarray(json.loads(vector),dtype=float)
            if v.shape!=q.shape:continue
            found.append({'case_id':case_id[:12],'reference_label':label,'source':source,'license':license,
                          'visual_similarity':round(float(np.dot(q,v)/max(np.linalg.norm(v),1e-12)),4),
                          'warning':'Image appearance similarity is not disease probability or diagnosis.'})
        return sorted(found,key=lambda x:x['visual_similarity'],reverse=True)[:max(1,min(int(limit),20))]

def fit_quantitative_model(x,y,*,degree=1,seed=42,bootstrap=200):
    """Polynomial least-squares with held-out CV, coefficient bootstrap and limitations.

    Requires independent numeric observations; neither causal inference nor extrapolation.
    """
    x=np.asarray(x,dtype=float).reshape(-1);y=np.asarray(y,dtype=float).reshape(-1)
    if x.shape!=y.shape:raise ValueError('X and Y must have same length')
    good=np.isfinite(x)&np.isfinite(y);x=x[good];y=y[good]
    degree=int(degree)
    if degree not in (1,2):raise ValueError('Supported model degrees: 1 or 2')
    if len(x)<max(8,3*(degree+1)):raise ValueError('At least 8 paired observations required')
    if len(np.unique(x))<degree+2:raise ValueError('Insufficient unique X values')
    rng=np.random.default_rng(seed)
    # Center and scale to reduce numerical instability.
    xm=float(x.mean()); xs=float(x.std())
    if xs<=1e-12:raise ValueError('X has no meaningful variation')
    z=(x-xm)/xs
    coeff=np.polyfit(z,y,degree)
    pred=np.polyval(coeff,z)
    rmse=float(np.sqrt(np.mean((y-pred)**2)))
    denom=float(np.sum((y-y.mean())**2))
    r2=1-float(np.sum((y-pred)**2))/denom if denom>0 else None
    folds=min(5,len(x)//3)
    indices=rng.permutation(len(x)); split=np.array_split(indices,folds)
    errors=[]
    for test in split:
        train=np.setdiff1d(np.arange(len(x)),test)
        c=np.polyfit(z[train],y[train],degree)
        errors.extend((y[test]-np.polyval(c,z[test])).tolist())
    cv_rmse=float(np.sqrt(np.mean(np.square(errors))))
    draws=[]
    for _ in range(max(0,min(int(bootstrap),1000))):
        ids=rng.integers(0,len(x),size=len(x))
        if len(np.unique(z[ids]))<degree+1:continue
        draws.append(np.polyfit(z[ids],y[ids],degree))
    ci=np.percentile(draws,[2.5,97.5],axis=0).T.tolist() if len(draws)>=20 else None
    return {'n':len(x),'degree':degree,'coefficients_scaled_x':coeff.tolist(),'x_center':xm,'x_scale':xs,
            'training_rmse':rmse,'cross_validation_rmse':cv_rmse,'training_r2':r2,
            'coefficient_bootstrap_95pct_intervals':ci,'x_observed_range':[float(x.min()),float(x.max())],
            'method':'Polynomial least squares; shuffled 5-fold (max) cross-validation; nonparametric bootstrap',
            'limitations':'Associational model, not causal. Do not extrapolate. Cross-validation assumes independent samples; grouped/time-series data require other splitting. Check units, sample selection, residuals and source quality.'}

def predict_quantitative(model,x_values):
    x=np.asarray(x_values,dtype=float)
    lo,hi=model['x_observed_range']
    if np.any((x<lo)|(x>hi)):raise ValueError('Prediction outside observed X range is disabled')
    z=(x-model['x_center'])/model['x_scale']
    return np.polyval(model['coefficients_scaled_x'],z).tolist()
