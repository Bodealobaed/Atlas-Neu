"""Reproducible medical RESEARCH report; not a clinical diagnosis."""
import io
from xml.sax.saxutils import escape
from PIL import Image as PILImage
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import mm
from report import shape, font


def build_medical_pdf(image, data, interpretation='', language='English'):
    """Generate a real PDF containing the annotated image, measurements and analysis."""
    if not isinstance(data, dict):
        raise TypeError('Report data must be a dictionary.')
    labels={
      'Arabic':('تقرير تحليل صور طبية بحثي','صورة التحليل','القياسات','التفسير البحثي','هذا التقرير لأغراض البحث ولا يمثل تشخيصاً طبياً.'),
      'German':('Medizinischer Bildforschungsbericht','Analysiertes Bild','Messwerte','Wissenschaftliche Interpretation','Forschungsbericht, keine klinische Diagnose.'),
      'English':('Medical Image Research Report','Analyzed image','Measurements','Research interpretation','Research use only; not a clinical diagnosis.')
    }
    title, image_label, measures, analysis, disclaimer=labels.get(language,labels['English'])
    buffer=io.BytesIO()
    pdf=SimpleDocTemplate(buffer,pagesize=(210*mm,297*mm),leftMargin=19*mm,rightMargin=19*mm,topMargin=19*mm,bottomMargin=20*mm)
    header=ParagraphStyle('MedicalTitle',fontName=font,fontSize=17,leading=26,textColor=colors.HexColor('#153e50'),spaceAfter=12)
    section=ParagraphStyle('MedicalSection',fontName=font,fontSize=11,leading=18,textColor=colors.HexColor('#147e8c'),spaceBefore=12,spaceAfter=8)
    body=ParagraphStyle('MedicalBody',fontName=font,fontSize=9,leading=15,textColor=colors.HexColor('#263d49'),spaceAfter=8,wordWrap='CJK',alignment=TA_LEFT)
    def para(value,style=body):return Paragraph(escape(shape(str(value or ''))).replace('\n','<br/>'),style)
    story=[para('ATLAS EAST  |  RESEARCH INTELLIGENCE',section),para(title,header),para(disclaimer),para(image_label,section)]
    if not isinstance(image,PILImage.Image):image=PILImage.open(io.BytesIO(image))
    img=image.convert('RGB');img.thumbnail((1600,1600))
    stream=io.BytesIO();img.save(stream,format='PNG');stream.seek(0)
    scale=min(169*mm/img.width,115*mm/img.height)
    story.append(Image(stream,width=img.width*scale,height=img.height*scale))
    story.append(para(measures,section))
    for key in ('user_selected_modality','file_type','slice_axis','slice_index','roi_px'):
        if key in data:story.append(para(f'{key.replace("_"," ")}: {data[key]}'))
    for field, label in [('research_title','Research title'),('patient_or_case_id','Patient / anonymous case ID'),('research_question','Research question'),('clinical_notes','Clinical context')]:
        if data.get(field):story.append(para(label+': '+str(data[field])))
    stats=data.get('statistics') or {}
    if isinstance(stats,dict) and stats:
        rows=[[para('Measurement'),para('Value')]]+[[para(k),para(v)] for k,v in stats.items()]
        table=Table(rows,colWidths=[78*mm,85*mm],repeatRows=1,hAlign='LEFT')
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e0eeee')),('GRID',(0,0),(-1,-1),.25,colors.HexColor('#b4cdd2')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
        story.append(table)
    story.append(para(analysis,section))
    text=interpretation or data.get('interpretation') or 'No AI interpretation was performed.'
    for paragraph in str(text).split('\n'):
        if paragraph.strip():story.append(para(paragraph))
    if data.get('literature'):
        story.append(para('Related published research (not case-specific diagnostic evidence)',section))
        for item in data['literature'][:10]:
            story.append(para(str(item.get('title',''))+' | PMID: '+str(item.get('pmid',''))+' | '+str(item.get('url',''))))
    story.extend([Spacer(1,7*mm),para(disclaimer)])
    pdf.build(story)
    output=buffer.getvalue()
    if not output.startswith(b'%PDF-'):raise RuntimeError('Invalid generated PDF')
    return output
