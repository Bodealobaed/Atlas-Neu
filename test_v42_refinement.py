import numpy as np
import pytest
from assisted_segmentation import refine_region

def test_region_refines_similar_connected_pixels():
    a=np.zeros((32,32),dtype=np.uint8);a[8:24,8:24]=180
    seed=np.zeros_like(a,dtype=bool);seed[14:17,14:17]=True
    mask,info=refine_region(a,seed,tolerance=.1,max_fraction=.4)
    assert mask.sum()>seed.sum() and mask.sum()<400 and not info['limited']

def test_region_guard_prevents_runaway():
    a=np.ones((30,30),dtype=np.uint8)*100
    seed=np.zeros_like(a,dtype=bool);seed[10:12,10:12]=True
    mask,info=refine_region(a,seed)
    assert info['limited'] and mask.sum()==seed.sum()

def test_invalid_mask_rejected():
    with pytest.raises(ValueError):refine_region(np.zeros((5,5)),np.zeros((4,4),bool))
