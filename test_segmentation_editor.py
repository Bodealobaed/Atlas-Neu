import numpy as np
from PIL import Image
from segmentation_editor import mask_measurements,mask_png,overlay_mask,mask_from_canvas

def test_mask_measurements():
    m=np.zeros((10,10),bool);m[2:4,3:6]=True
    assert mask_measurements(m,[.5,.5])=={'pixels':6,'percent':6.0,'area_mm2':1.5}

def test_mask_png_overlay():
    m=np.zeros((12,12),bool);m[2:4,2:4]=True
    assert mask_png(m)[:8]==b'\x89PNG\r\n\x1a\n'
    assert overlay_mask(Image.new('L',(12,12)),m).size==(12,12)

def test_canvas_alpha():
    a=np.zeros((5,6,4),dtype=np.uint8);a[1,2,3]=255
    assert mask_from_canvas(a,(5,6)).sum()==1
