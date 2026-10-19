"""Deterministic, non-diagnostic, image-guided region refinement from a manual seed.
No disease labels, model claims or external data transfer.
"""
import numpy as np
from scipy.ndimage import binary_propagation, binary_opening, binary_closing, label

def refine_region(image, seed_mask, tolerance=0.20, max_fraction=0.35):
    a=np.asarray(image.convert('L') if hasattr(image,'convert') else image,dtype=np.float32)
    seed=np.asarray(seed_mask,dtype=bool)
    if a.ndim!=2 or seed.shape!=a.shape: raise ValueError('Image and seed dimensions must match')
    if not seed.any(): raise ValueError('Mark a region with the brush first')
    if not (0<tolerance<=1) or not (0<max_fraction<=1): raise ValueError('Invalid refinement parameters')
    # Robust local intensity envelope from the user-selected seed; does not infer disease.
    values=a[seed]
    center=float(np.median(values))
    spread=max(float(np.percentile(a,99)-np.percentile(a,1)),1.0)
    allowed=np.abs(a-center)<=spread*tolerance
    allowed|=seed
    grown=binary_propagation(seed,mask=allowed)
    if grown.mean()>max_fraction:
        # Fail closed rather than silently selecting most of the image.
        return seed.copy(), {'limited':True,'seed_pixels':int(seed.sum()),'selected_pixels':int(seed.sum())}
    grown=binary_closing(grown,iterations=1)|seed
    # Retain only components touching seed after morphological operations.
    components,count=label(grown)
    ids=np.unique(components[seed]);ids=ids[ids!=0]
    result=np.isin(components,ids)|seed
    return result,{'limited':False,'seed_pixels':int(seed.sum()),'selected_pixels':int(result.sum())}
