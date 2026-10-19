"""Research image viewer: no disease classification or clinical segmentation."""
import io, os, tempfile
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

def load_study(name, data):
    name=name.lower()
    meta={'source':'','modality':'Unverified','privacy':'Identifiers are not displayed'}
    if name.endswith(('.dcm','.dicom')):
        import pydicom
        ds=pydicom.dcmread(io.BytesIO(data))
        arr=np.asarray(ds.pixel_array,dtype=np.float32)
        meta.update(source='DICOM',modality=str(ds.get('Modality','Unknown')))
        slope=float(ds.get('RescaleSlope',1)); intercept=float(ds.get('RescaleIntercept',0))
        arr=arr*slope+intercept
        if str(ds.get('PhotometricInterpretation',''))=='MONOCHROME1':meta['invert']=True
        if 'PixelSpacing' in ds:
            try:meta['spacing_mm']=[float(x) for x in ds.PixelSpacing]
            except (TypeError,ValueError):pass
        # Color and multi-frame images are not silently interpreted as a grayscale volume.
        if arr.ndim==3 and arr.shape[-1] in (3,4):
            raise ValueError('Color DICOM is not supported by this grayscale research viewer.')
    elif name.endswith(('.nii','.nii.gz')):
        import nibabel as nib
        suffix='.nii.gz' if name.endswith('.nii.gz') else '.nii'
        with tempfile.NamedTemporaryFile(suffix=suffix,delete=False) as f:
            f.write(data); path=f.name
        try:
            ni=nib.load(path); arr=np.asarray(ni.dataobj,dtype=np.float32)
            meta.update(source='NIfTI',modality='Unverified NIfTI volume',spacing_mm=[float(x) for x in ni.header.get_zooms()[:2]])
        finally:os.unlink(path)
    elif name.endswith(('.png','.jpg','.jpeg','.tif','.tiff')):
        arr=np.asarray(Image.open(io.BytesIO(data)).convert('L'),dtype=np.float32)
        meta.update(source='Raster image',modality='Unverified raster image')
    else:raise ValueError('Unsupported file type')
    if arr.ndim==4:arr=arr[...,0] # first temporal/sequence frame; disclose this choice
    if arr.ndim not in (2,3):raise ValueError('Unsupported image dimensions')
    arr=np.nan_to_num(arr,nan=0,posinf=0,neginf=0)
    if arr.size>160_000_000:raise ValueError('Image exceeds safe memory limit')
    meta['shape']=list(arr.shape)
    meta['modality_note']='Raster images do not establish whether the scan is X-ray, CT or MRI.' if meta['source']=='Raster image' else 'Modality derives from file metadata and must be verified.'
    return arr,meta

def get_slice(arr,index,axis):
    if arr.ndim==2:return arr
    return np.take(arr,int(index),axis=int(axis))

def render_slice(arr, low, high, invert=False, gamma=1.0, sharpen=0.0):
    if high<=low:high=low+1
    scaled=np.clip((arr.astype(np.float32)-low)/(high-low),0,1)
    scaled=np.power(scaled,1/max(float(gamma),0.1))
    if invert:scaled=1-scaled
    img=Image.fromarray((scaled*255).astype('uint8'))
    if sharpen:img=ImageEnhance.Sharpness(img).enhance(1+float(sharpen))
    return img

def roi_statistics(arr,box,spacing=None):
    x0,y0,x1,y1=[int(v) for v in box]
    roi=arr[y0:y1,x0:x1]
    if not roi.size:raise ValueError('ROI is empty')
    out={'width_px':x1-x0,'height_px':y1-y0,'pixel_count':int(roi.size),
         'mean_intensity':round(float(np.mean(roi)),3),'median_intensity':round(float(np.median(roi)),3),
         'std_intensity':round(float(np.std(roi)),3),'min_intensity':round(float(np.min(roi)),3),
         'max_intensity':round(float(np.max(roi)),3)}
    if spacing and len(spacing)>=2:
        out['area_mm2']=round((x1-x0)*(y1-y0)*float(spacing[0])*float(spacing[1]),2)
        out['area_note']='Geometric ROI area, not anatomical organ area'
    return out

def png_bytes(image):
    b=io.BytesIO();image.save(b,format='PNG');return b.getvalue()
