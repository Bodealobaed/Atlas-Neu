"""Manual research annotations, not automated clinical segmentation."""
import io
import numpy as np
from PIL import Image, ImageDraw

def mask_from_canvas(image_data, shape, threshold=20):
    """Extract the alpha-painted overlay from drawable-canvas, ignoring background image."""
    h,w=shape
    if image_data is None:
        return np.zeros((h,w),dtype=bool)
    arr=np.asarray(image_data)
    if arr.ndim!=3 or arr.shape[2]!=4 or arr.shape[:2]!=(h,w):
        raise ValueError('Canvas image dimensions do not match scan')
    return arr[:,:,3]>threshold

def overlay_mask(image,mask,color=(0,230,200),alpha=0.48):
    base=image.convert('RGB'); m=np.asarray(mask,dtype=bool)
    if m.shape!=(base.height,base.width):raise ValueError('Mask/image mismatch')
    tint=Image.new('RGB',base.size,color)
    blend=Image.blend(base,tint,alpha)
    base.paste(blend,mask=Image.fromarray((m*255).astype('uint8')))
    return base

def mask_measurements(mask,spacing=None):
    mask=np.asarray(mask,dtype=bool)
    count=int(mask.sum())
    out={'pixels':count,'percent':round(100*count/mask.size,2) if mask.size else 0}
    if spacing and len(spacing)>=2 and all(float(x)>0 for x in spacing[:2]):
        out['area_mm2']=round(count*float(spacing[0])*float(spacing[1]),2)
    return out

def mask_png(mask):
    b=io.BytesIO();Image.fromarray((np.asarray(mask,dtype=bool)*255).astype('uint8')).save(b,format='PNG');return b.getvalue()

def run_editor(st,image,key,spacing=None,lang="English"):
    """Canvas-based paint, erase, rectangle and polygon tools; local manual annotations."""
    try:
        from streamlit_drawable_canvas import st_canvas
    except ImportError:
        st.warning({'Deutsch':'Zeichenwerkzeug ist nicht installiert.','العربية':'أداة الرسم غير مثبتة.','English':'Drawing component is not installed.'}.get(lang,'Drawing component is not installed.'))
        return None
    st.caption({'Deutsch':'Manuelle Forschungsmarkierung; keine automatische Krankheitserkennung.','العربية':'تحديد بحثي يدوي؛ ليس كشفًا آليًا للأمراض.','English':'Manual research annotation; not automatic disease detection.'}.get(lang,'Manual annotation.'))
    mode=st.selectbox({'Deutsch':'Zeichenwerkzeug','العربية':'أداة الرسم','English':'Drawing tool'}.get(lang,'Drawing tool'),['freedraw','rect','polygon','transform'],format_func=lambda m: {'Deutsch':{'freedraw':'Pinsel','rect':'Rechteck','polygon':'Polygon','transform':'Verschieben'},'العربية':{'freedraw':'فرشاة','rect':'مستطيل','polygon':'مضلع','transform':'تحريك'},'English':{'freedraw':'Brush','rect':'Rectangle','polygon':'Polygon','transform':'Move'}}.get(lang,{}).get(m,m),key=key+'_mode')
    stroke=st.slider({'Deutsch':'Pinselgröße','العربية':'حجم الفرشاة','English':'Brush size'}.get(lang,'Brush size'),1,60,12,key=key+'_stroke')
    # Canvas max dimensions to keep responsive; explicit scale back to original image.
    w,h=image.size; scale=min(1.,850/max(w,1),650/max(h,1))
    sw,sh=max(1,round(w*scale)),max(1,round(h*scale))
    background=image.convert('RGB').resize((sw,sh))
    # Keep a separate per-slice canvas key to avoid leaking masks between slices.
    canvas=st_canvas(fill_color='rgba(0,230,200,0.35)',stroke_width=stroke,
                     stroke_color='rgba(0,230,200,1)',background_image=background,
                     update_streamlit=True,height=sh,width=sw,drawing_mode=mode,
                     display_toolbar=True,key=key+'_canvas')
    if canvas.image_data is None:return None
    data=np.asarray(canvas.image_data)
    # st_canvas composits background into RGBA; use Fabric object geometry to reconstruct a mask.
    # Fabric supports paths, polygons, rectangles; raster extraction must not mistake the background for a mask.
    mask_small=Image.new('L',(sw,sh),0)
    draw=ImageDraw.Draw(mask_small)
    objects=(canvas.json_data or {}).get('objects',[])
    for obj in objects:
        kind=obj.get('type','')
        left=float(obj.get('left',0));top=float(obj.get('top',0))
        sx=float(obj.get('scaleX',1));sy=float(obj.get('scaleY',1))
        thick=max(1,round(float(obj.get('strokeWidth',stroke))*max(sx,sy)))
        if kind=='rect':
            right=left+float(obj.get('width',0))*sx;bottom=top+float(obj.get('height',0))*sy
            draw.rectangle((left,top,right,bottom),fill=255)
        elif kind=='polygon':
            pts=obj.get('points',[])
            if len(pts)>=3:
                # Fabric polygon point coordinates are relative to pathOffset.
                off=obj.get('pathOffset',{})
                ox=float(off.get('x',0));oy=float(off.get('y',0))
                coords=[(left+(float(p['x'])-ox+float(obj.get('width',0))/2)*sx,
                         top+(float(p['y'])-oy+float(obj.get('height',0))/2)*sy) for p in pts]
                draw.polygon(coords,fill=255)
        elif kind=='path':
            # Use path point endpoints as a brush approximation; Bezier curves are sampled via their control/end points.
            path=obj.get('path',[]);points=[]
            for segment in path:
                if not isinstance(segment,list) or len(segment)<3:continue
                values=segment[1:]
                if len(values)>=2 and all(isinstance(v,(int,float)) for v in values[-2:]):
                    points.append((left+float(values[-2])*sx,top+float(values[-1])*sy))
            if len(points)>1:draw.line(points,fill=255,width=thick,joint='curve')
            for x,y in points:draw.ellipse((x-thick/2,y-thick/2,x+thick/2,y+thick/2),fill=255)
    mask=np.asarray(mask_small.resize((w,h),resample=Image.Resampling.NEAREST))>0
    if mask.any():
        st.markdown({'Deutsch':'**Bildgeführte Bereichserweiterung**','العربية':'**توسيع المنطقة اعتمادًا على الصورة**','English':'**Image-guided region refinement**'}.get(lang,'Image-guided refinement'))
        tolerance=st.slider({'Deutsch':'Ähnlichkeit der Grauwerte','العربية':'تشابه درجات الشدة','English':'Intensity similarity'}.get(lang,'Intensity similarity'),5,40,20,5,key=key+'_tolerance')
        if st.button({'Deutsch':'Markierung automatisch erweitern','العربية':'توسيع التحديد تلقائيًا','English':'Refine selected region'}.get(lang,'Refine region'),key=key+'_refine'):
            from assisted_segmentation import refine_region
            try:
                refined,info=refine_region(image,mask,tolerance=tolerance/100)
                st.session_state[key+'_refined']=refined
                st.session_state[key+'_refine_limited']=info['limited']
            except ValueError:
                st.warning({'Deutsch':'Bereich konnte nicht erweitert werden.','العربية':'تعذر توسيع المنطقة.','English':'Region could not be refined.'}.get(lang))
        refined=st.session_state.get(key+'_refined')
        if refined is not None and np.shape(refined)==np.shape(mask):
            mask=refined
            if st.session_state.get(key+'_refine_limited'):
                st.warning({'Deutsch':'Erweiterung begrenzt: zu großer Bereich.','العربية':'تم تقييد التوسيع لأن المنطقة كبيرة جدًا.','English':'Refinement limited because the area is too large.'}.get(lang))
        st.caption({'Deutsch':'Die Erweiterung folgt ähnlichen Pixelwerten, erkennt aber keine Krankheit.','العربية':'يتبع التوسيع قيم البكسلات المتشابهة ولا يكتشف المرض.','English':'Refinement follows similar pixel intensities; it does not detect disease.'}.get(lang))
        st.image(overlay_mask(image,mask),caption='Manual segmentation overlay / التحديد اليدوي',use_container_width=True)
        measures=mask_measurements(mask,spacing)
        st.caption(({'Deutsch':'Markierte Fläche','العربية':'المساحة المحددة','English':'Selected area'}.get(lang,'Selected area'))+f": {measures['percent']}%")
        st.download_button({'Deutsch':'Maske als PNG herunterladen','العربية':'تنزيل القناع PNG','English':'Download mask PNG'}.get(lang,'Download mask PNG'),mask_png(mask),'atlas_segmentation_mask.png','image/png',key=key+'_download')
    return mask
