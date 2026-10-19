from literature_intelligence import federated_search, evidence_brief
from clinical_evidence import search_from_image
from medical_ui_v35 import label as medlabel
"""ATLAS EAST Research Intelligence — multilingual research workstation."""
import os, io, hashlib, base64
import numpy as np
from i18n import tr
import streamlit as st
import pandas as pd
from analyzer import extract_document, extract_links, verify_links, analyze_with_ai, basic_analysis
from report import build_pdf
from science import table_insights, simulate_linear, image_measurements, threshold_mask, scenario_summary
from medical_workstation import load_study, get_slice, render_slice, roi_statistics, png_bytes
from book import create_book_content, build_book_pdf
from medical_pdf import build_medical_pdf
from research_engines import ReferenceLibrary, fit_quantitative_model, predict_quantitative, mask_metrics
from arabic_vision import inspect_pdf_page
from evidence_engine import search_pubmed
from longitudinal_engine import ResearchMemory, evidence_assessment
from research_interpretation import explain_medical_image, explain_document_figure, explain_table, polygon_segmentation, mask_overlay, interpret_simulation

st.set_page_config(page_title='ATLAS EAST | Research Intelligence',page_icon='🔬',layout='wide',initial_sidebar_state='expanded')
with st.sidebar:
    lang=st.selectbox('🌐 Language / Sprache / اللغة', ['English','Deutsch','العربية'],index=0,format_func=lambda x: {'العربية':'العربية','Deutsch':'Deutsch','English':'English'}[x],label_visibility='collapsed',key='interface_language')
def T(key): return tr(key,lang)
st.markdown("""<style>
/* ATLAS EAST: readable, calm, high-contrast multicolor identity */
html, body, [class*="css"], .stApp {font-size:17px}
.stApp{background:radial-gradient(ellipse at 90% 4%,#d8eeec 0%,transparent 42%),linear-gradient(135deg,#f1f5f9 0%,#e5edf4 53%,#f1f0f8 100%);color:#193448}
.block-container{max-width:1500px;padding-top:2.3rem;padding-left:2.2rem;padding-right:2.2rem;padding-bottom:4rem}
[data-testid="stSidebar"]{background:linear-gradient(155deg,#102a41 0%,#164b5d 52%,#283c61 100%);border-right:2px solid #3f9c9d}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,[data-testid="stSidebar"] label,[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2{color:#e7f4f8!important}
[data-testid="stSidebar"] .stAlert p{color:#18384a!important}
[data-testid="stSidebar"] [data-baseweb="select"] *,[data-testid="stSidebar"] input{color:#17384f!important}
[data-testid="stHeader"]{background:rgba(241,245,249,.87)}
[data-testid="stMetric"]{background:#fff;padding:18px;border-radius:16px;border:1px solid #c8dce3;box-shadow:0 3px 12px #1b405410}
.stTabs [data-baseweb="tab-list"]{gap:6px;overflow-x:auto}
.stTabs [data-baseweb="tab"]{font-size:1rem;font-weight:650;border-radius:9px 9px 0 0;padding:13px 16px}
h1,h2,h3{color:#14394d!important;letter-spacing:.1px}
h1{font-size:2.15rem!important}h2{font-size:1.55rem!important}h3{font-size:1.25rem!important}
.hero{background:linear-gradient(115deg,#16334f 0%,#205b70 54%,#326b72 100%);border:1px solid #589da0;border-radius:24px;padding:34px 36px;color:#fff;margin:0 0 26px;box-shadow:0 12px 28px #193f5529}
.hero h1,.hero p{color:#fff!important}.hero p{opacity:.94;font-size:1.08rem;margin:12px 0 0}
.stButton>button[kind="primary"],.stDownloadButton>button{background:#167f8b;color:#fff;border-radius:12px;border:0;min-height:44px;font-weight:650}
.stButton>button:hover,.stDownloadButton>button:hover{border-color:#53b5b2;color:#fff}
[data-testid="stFileUploader"]{border-radius:14px}
@media(max-width:800px){.block-container{padding-left:1rem;padding-right:1rem}.hero{padding:22px}.atlas-brand img{max-width:64px}}
</style>""",unsafe_allow_html=True)
if lang=='العربية':
    st.markdown('<style>[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],.stApp h1,.stApp h2,.stApp h3,.stApp p,.stApp label{direction:rtl;text-align:right}</style>',unsafe_allow_html=True)
# ATLAS brand: original microscope motif, enlarged and colored, not a generic atom/diamond.
MICROSCOPE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64" role="img" aria-label="ATLAS EAST microscope"><defs><linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#6CE2D1"/><stop offset="1" stop-color="#37A8CA"/></linearGradient></defs><path d="M36 8l14 14-7 7-14-14z" fill="url(#glass)" stroke="#D6F2F5" stroke-width="1.5"/><path d="M28 19l12 12" stroke="#D5EFF5" stroke-width="5" stroke-linecap="round"/><path d="M28 30l-9 9" stroke="#62C6E7" stroke-width="5" stroke-linecap="round"/><path d="M43 33c6 13-3 19-15 19-10 0-16-6-15-15" fill="none" stroke="#63BDE0" stroke-width="5" stroke-linecap="round"/><path d="M11 56h43" stroke="#6DE3D1" stroke-width="5" stroke-linecap="round"/><circle cx="19" cy="39" r="4" fill="#F2C778"/></svg>"""
LOGO_DATA = base64.b64encode(MICROSCOPE_SVG.encode('utf-8')).decode('ascii')
def brand_html(sidebar=False):
    size=76 if sidebar else 96
    title_size=28 if sidebar else 49
    return (f'<div class="atlas-brand" style="display:flex;align-items:center;gap:19px">'
            f'<img alt="ATLAS EAST microscope" src="data:image/svg+xml;base64,{LOGO_DATA}" width="{size}" height="{size}"/>'
            f'<div><div style="font-size:{title_size}px;font-weight:850;letter-spacing:0.8px;white-space:nowrap;color:#f3fbfd">ATLAS EAST</div>'
            f'<div style="font-size:12px;letter-spacing:1.1px;color:#b4e5e9">RESEARCH INTELLIGENCE</div></div></div>')
with st.sidebar:
    st.markdown(brand_html(sidebar=True),unsafe_allow_html=True)
    st.divider()
    target=st.selectbox(T('output'),['English','German','Arabic'],index={'English':0,'Deutsch':1,'العربية':2}[lang],format_func=lambda v: {'English':{'English':'English','Deutsch':'Englisch','العربية':'الإنجليزية'},'German':{'English':'German','Deutsch':'Deutsch','العربية':'الألمانية'},'Arabic':{'English':'Arabic','Deutsch':'Arabisch','العربية':'العربية'}}[v][lang])
    model=st.selectbox(T('model'),['gpt-4.1-mini','gpt-4o-mini','gpt-4.1'])
    try: api_key=st.secrets.get('OPENAI_API_KEY','')
    except Exception: api_key=''
    api_key=api_key or os.environ.get('OPENAI_API_KEY','')
    st.caption('🔐 '+T('api_caption'))
    check=st.checkbox(T('check_links'),False)
    st.warning(T('privacy'))
# Navigation is intentionally independent of document/session state: opening the app
# never extracts or uploads a document, and switching pages preserves existing work.
WELCOME_TEXT = {
    'العربية': {
        'home': 'الرئيسية', 'workspace': 'مساحة العمل', 'navigation': 'التنقل',
        'intro_title': 'من مشروع بحثي إلى معرفة علمية منظمة',
        'intro': 'ATLAS EAST منصة مساعدة للباحثين لقراءة المشاريع والرسائل العلمية، وفحص الأدلة والجداول والصور، وإعداد تقارير بحثية ومسودات أوراق علمية وكتب قابلة للطباعة.',
        'languages': 'اللغات المدعومة', 'language_detail': 'العربية · الألمانية · الإنجليزية — يمكنك اختيار لغة الواجهة ولغة المخرجات بشكل مستقل.',
        'tools': 'ما الذي يمكنك إنجازه؟',
        'features': [('تدقيق البحث', 'ملخصات ومنهجية وأدلة مرتبطة بالمصدر.'), ('البيانات والمحاكاة', 'جداول وحسابات وصفية وسيناريوهات بحثية مع بيان حدودها.'), ('الصور الطبية', 'عرض وقياسات استكشافية للصور، وليست تشخيصًا طبيًا.'), ('النشر العلمي', 'مسودات أوراق بحثية وكتب علمية مع فهرس وأغلفة للطباعة.')],
        'enter': 'الانتقال إلى مساحة العمل', 'note': 'أداة مساعدة للبحث؛ جميع النتائج العلمية والمخرجات المعدة للنشر تحتاج إلى مراجعة الباحث والتحقق من الحقوق.',
        'workspace_note': 'ارفع مشروعك هنا، ثم اختر أداة التحليل أو التقرير أو الكتاب من الأقسام أدناه.'
    },
    'Deutsch': {
        'home': 'Startseite', 'workspace': 'Arbeitsbereich', 'navigation': 'Navigation',
        'intro_title': 'Vom Forschungsprojekt zu strukturierter wissenschaftlicher Erkenntnis',
        'intro': 'ATLAS EAST unterstützt Forschende beim Auswerten von Abschlussarbeiten und Forschungsdokumenten, beim Prüfen von Belegen, Tabellen und Bildern sowie beim Erstellen von Berichten, Manuskriptentwürfen und druckbaren Büchern.',
        'languages': 'Unterstützte Sprachen', 'language_detail': 'Deutsch · Englisch · Arabisch — Oberfläche und Ausgabesprache können unabhängig gewählt werden.',
        'tools': 'Was bietet ATLAS EAST?',
        'features': [('Forschungsprüfung', 'Zusammenfassungen, Methoden und quellengestützte Belege.'), ('Daten und Simulation', 'Tabellen, deskriptive Berechnungen und gekennzeichnete Forschungsszenarien.'), ('Medizinische Bildgebung', 'Explorative Bildanzeige und Messungen, keine medizinische Diagnose.'), ('Wissenschaftliche Publikationen', 'Entwürfe für Forschungsartikel und druckbare Fachbücher mit Inhaltsverzeichnis und Umschlag.')],
        'enter': 'Zum Arbeitsbereich', 'note': 'Forschungsassistenz: Wissenschaftliche Aussagen und Publikationen erfordern fachliche Prüfung und geklärte Nutzungsrechte.',
        'workspace_note': 'Laden Sie Ihr Projekt hoch und wählen Sie unten Analyse, Bericht oder Bucherstellung.'
    },
    'English': {
        'home': 'Home', 'workspace': 'Workspace', 'navigation': 'Navigation',
        'intro_title': 'From research projects to structured scientific insight',
        'intro': 'ATLAS EAST helps researchers review theses and scientific documents, examine evidence, tables and images, and prepare research reports, manuscript drafts and print-ready book layouts.',
        'languages': 'Supported languages', 'language_detail': 'English · German · Arabic — choose interface and output languages independently.',
        'tools': 'Explore the platform',
        'features': [('Research audit', 'Summaries, methodology and source-linked evidence.'), ('Data and simulation', 'Tables, descriptive calculations and clearly labeled research scenarios.'), ('Medical imaging', 'Exploratory image viewing and measurements, not clinical diagnosis.'), ('Scientific publishing', 'Research manuscript drafts and printable scientific books with contents and covers.')],
        'enter': 'Open research workspace', 'note': 'Research assistance only. Scientific findings and publishable outputs require expert review and appropriate usage rights.',
        'workspace_note': 'Upload your project, then use the analysis, report or book tools below.'
    }
}
ui = WELCOME_TEXT[lang]
with st.sidebar:
    selected_page = st.radio(ui['navigation'], ['home', 'workspace'],
        format_func=lambda page: ui[page], key='atlas_page', horizontal=False)

st.markdown(f'<div class="hero">{brand_html()}<p style="color:#d5f5f3;font-size:1.16rem;margin-top:14px">{T("hero_sub")}</p><p style="color:#a7e6df;font-size:0.96rem;letter-spacing:0.4px">Discover · Analyze · Model · Publish</p></div>',unsafe_allow_html=True)
if selected_page == 'home':
    st.title(ui['intro_title'])
    st.write(ui['intro'])
    st.subheader(ui['tools'])
    feature_columns = st.columns(2)
    for index, (heading, description) in enumerate(ui['features']):
        with feature_columns[index % 2]:
            with st.container(border=True):
                st.markdown('#### ' + heading)
                st.write(description)
    with st.container(border=True):
        st.markdown('#### 🌐 ' + ui['languages'])
        st.write(ui['language_detail'])
    st.caption(ui['note'])
    # Streamlit callbacks run before widget creation on the next rerun.
    # Do not mutate atlas_page after the radio widget is instantiated.
    def open_research_workspace():
        st.session_state['atlas_page'] = 'workspace'

    st.button('→ ' + ui['enter'], type='primary', use_container_width=True,
              key='atlas_enter_workspace', on_click=open_research_workspace)
    st.stop()

st.caption(ui['workspace_note'])

upload=st.file_uploader(T('upload'),type=['pdf','docx'])
if upload:
    signature=hashlib.sha256(upload.getvalue()).hexdigest()
    if st.session_state.get('document_signature')!=signature:
        st.session_state['document_signature']=signature
        for k in list(st.session_state):
            if k in ('analysis','doc','checks','book_content','book_signature','simulation_explanation') or k.startswith(('fig_explanation_','table_explanation_')):
                st.session_state.pop(k,None)
        try: st.session_state['doc']=extract_document(upload)
        except Exception as exc: st.error(str(exc));st.stop()
    doc=st.session_state['doc'];links=extract_links(doc['text'])
    st.session_state['uploaded_pdf_bytes']=upload.getvalue() if upload.name.lower().endswith('.pdf') else None
    metrics=st.columns(4)
    for col,title,value in zip(metrics,[T('pages'),T('tables'),T('figures_count'),T('links_count')],[len(doc['pages']),len(doc['tables']),len(doc['images']),len(links)]): col.metric(title,value)
    st.caption(f"{doc['name']} · {len(doc['text']):,} {T('characters')}")
    if len(doc['text'].strip())<250:
        st.warning('Low extractable text: scanned PDF. Use the Arabic/scanned page OCR tool in Tables. Full-document AI analysis may be incomplete.')
    c1,c2=st.columns(2)
    with c1:
        if st.button(T('run'),type='primary',use_container_width=True,disabled=not bool(api_key)):
            try:
                with st.spinner(T('working')):
                    st.session_state['analysis']=analyze_with_ai(doc,api_key,model,target)
                    st.session_state['analysis_language']=target
            except Exception as exc: st.error(f'{T("analysis_error")}: {type(exc).__name__}: {exc}')
    with c2:
        if st.button(T('inspect'),use_container_width=True): st.session_state['analysis']=basic_analysis(doc);st.session_state['analysis_language']='source'
    if not api_key: st.info(T('api_missing'))
    analysis=st.session_state.get('analysis')
    if analysis and st.session_state.get('analysis_language') not in (target,):
        st.info({'العربية':'تم تغيير لغة التقرير أو استُخدم الفحص دون ذكاء اصطناعي؛ أعد التدقيق بالذكاء الاصطناعي للحصول على نص كامل باللغة المختارة.','Deutsch':'Die Berichtssprache wurde geändert oder eine Prüfung ohne KI verwendet; starten Sie die KI-Analyse erneut, um alle Texte in der gewählten Sprache zu erhalten.','English':'The report language changed or inspection without AI was used; rerun the AI audit to generate all content in the chosen language.'}[lang])
else:
    doc=None;analysis=None;links=[]
    st.info(T('upload_hint'))

tab_names=[T(k) for k in ['summary','methods','results','tables','figures','medical','simulation','refs','export']]
# Workspace tools are visible near the top, not buried at the bottom of the sidebar.
with st.container(border=True):
    left,nav=st.columns([3,1.35],vertical_alignment='top')
    with left:
        st.markdown('#### 🔬 ATLAS EAST · Research workspace')
        st.caption(ui['workspace_note'])
    with nav:
        selected_section=st.radio('Research tools',list(range(len(tab_names))),format_func=lambda i:tab_names[i],horizontal=False,key='atlas_section',label_visibility='collapsed')
if selected_section==0:
    if analysis:
        st.subheader(analysis.get('proposed_title') or T('summary'))
        st.write(analysis.get('executive_summary',''))
        for key in ['research_question','discipline','study_design','translation_notes']:
            with st.expander(T('field_'+key)):st.write(analysis.get(key,''))
    else: st.info(T('missing'))
if selected_section==1:
    if analysis:
        for key in ['methods','sample_and_materials','statistics','limitations','risk_of_bias','reproducibility']:
            st.markdown('#### '+T('field_'+key));st.write(analysis.get(key,''))
    else:st.info(T('missing'))
if selected_section==2:
    if analysis:
        for key in ['scientific_contribution','key_findings','clinical_findings','engineering_findings','pharmaceutical_findings','new_hypotheses','discussion','conclusion']:
            st.markdown('#### '+T('field_'+key));st.write(analysis.get(key,''))
        st.caption(T('quote_note'))
    else:st.info(T('missing'))
if selected_section==3:
    if doc and api_key and st.session_state.get('uploaded_pdf_bytes'):
        with st.expander({'English':'Arabic/scanned page table recognition (AI OCR)','Deutsch':'Arabische Tabellen / Scan-Seiten erkennen (KI-OCR)','العربية':'التعرف على الجداول العربية والصفحات الممسوحة (OCR)'}[lang]):
            st.caption({'English':'Select a page and explicitly authorize sending its rendered image to OpenAI. Verify every transcribed cell against the original.','Deutsch':'Wählen Sie eine Seite und erlauben Sie die Übermittlung des Seitenbilds an OpenAI. Jede Zelle mit dem Original prüfen.','العربية':'اختر صفحة ووافق على إرسال صورتها إلى OpenAI. تحقق من كل خلية مقارنة بالأصل.'}[lang])
            page_no=st.number_input('PDF page / Seite / الصفحة',min_value=1,max_value=len(doc['pages']),value=1,step=1)
            if st.button('Read page tables / Tabellen erkennen / قراءة الجداول',key='arabic_page_ocr'):
                try:
                    with st.spinner('Reading Arabic text and tables…'):
                        result=inspect_pdf_page(st.session_state['uploaded_pdf_bytes'],int(page_no),api_key,model)
                        st.session_state['arabic_ocr_result']=result
                        st.session_state['arabic_ocr_page']=int(page_no)
                except Exception as exc:st.error(f'OCR failed: {type(exc).__name__}: {exc}')
            result=st.session_state.get('arabic_ocr_result')
            if result and st.session_state.get('arabic_ocr_page')==int(page_no):
                st.warning({'English':'Unverified transcription. Compare Arabic letters, numbers and every table cell with the source PDF before use.','Deutsch':'Ungeprüfte Transkription: Arabische Zeichen, Zahlen und alle Tabellenzellen mit dem Original abgleichen.','العربية':'نسخ غير موثق: راجع الحروف العربية والأرقام وكل خلية مع ملف PDF الأصلي قبل استخدامها.'}[lang])
                for warning in result.get('warnings',[]):st.warning(str(warning))
                st.text_area('Transcribed page text',result.get('page_text',''),height=150)
                for ti,table in enumerate(result.get('tables',[])):
                    st.markdown('#### '+str(table.get('title') or f'Table {ti+1}'))
                    rows=table.get('rows',[])
                    if rows:
                        n=max(len(r) for r in rows)
                        frame=pd.DataFrame([list(r)+['']*(n-len(r)) for r in rows])
                        st.dataframe(frame.astype(str),use_container_width=True)
                        st.download_button('Download OCR table CSV',frame.to_csv(index=False,header=False).encode('utf-8-sig'),f'arabic_page_{page_no}_table_{ti+1}.csv',key=f'ocr_table_{page_no}_{ti}')
                if result.get('warnings'):st.warning('; '.join(map(str,result['warnings'])))
    if doc and doc['tables']:
        for i,table in enumerate(doc['tables']):
            with st.expander(table['title'],expanded=i==0):
                try:
                    insights,frame=table_insights(table['rows'])
                    st.dataframe(frame.fillna('').astype(str),use_container_width=True)
                except (ValueError,TypeError,IndexError) as exc:
                    st.warning(T('bad_table'))
                    continue
                if insights:
                    st.write(T('descriptive'))
                    st.dataframe(pd.DataFrame([{**item,'unit':T('unit_source'),'status':T('stat_note')} for item in insights]).rename(columns={'column':T('stat_column'),'mean':T('stat_mean'),'median':T('stat_median'),'std_sample':T('stat_std'),'unit':T('stat_unit'),'status':T('stat_status')}),use_container_width=True)
                    if api_key and st.button({'العربية':'تفسير علمي للجدول','Deutsch':'Wissenschaftliche Tabelleninterpretation','English':'Scientific table interpretation'}[lang],key=f'table_explain_{i}'):
                        with st.spinner('Analyzing table evidence…'):
                            try:
                                st.session_state[f'table_explanation_{i}']=explain_table(api_key,model,table,frame,insights,doc,target)
                            except Exception as exc:st.warning(f'Analysis unavailable: {type(exc).__name__}: {exc}')
                    if st.session_state.get(f'table_explanation_{i}'):st.markdown(st.session_state[f'table_explanation_{i}'])
                    st.download_button(T('csv_table'),frame.to_csv(index=False).encode('utf-8-sig'),file_name=f'atlas_table_{i+1}.csv',key=f'table_{i}')
                else:st.caption(T('no_numbers'))
    else:st.info(T('no_tables'))
if selected_section==4:
    if doc and doc['images']:
        for i,img in enumerate(doc['images']):
            with st.expander(img['label'],expanded=i==0):
                st.image(img['bytes'],caption=img['label'],width=650)
                if api_key and st.button({'العربية':'شرح الصورة في سياق البحث','Deutsch':'Abbildung im Forschungskontext erklären','English':'Explain figure in research context'}[lang],key=f'fig_explain_{i}'):
                    with st.spinner('Reading figure and surrounding research text…'):
                        try:st.session_state[f'fig_explanation_{i}']=explain_document_figure(api_key,model,img,doc,target)
                        except Exception as exc:st.warning(f'Figure explanation unavailable: {type(exc).__name__}: {exc}')
                if st.session_state.get(f'fig_explanation_{i}'):st.markdown(st.session_state[f'fig_explanation_{i}'])
    else:st.info(T('no_images'))
if selected_section==5:
    med_ui={
        'العربية':{'title':'مختبر الصور الطبية البحثي','upload':'تحميل صورة طبية','type':'نوع التصوير (تحقق يدويًا)','slice':'الشريحة','axis':'المحور','window':'نافذة الشدة','gamma':'جاما','sharp':'الحدة','invert':'عكس الألوان','roi':'منطقة الاهتمام (ROI)','zoom':'تكبير المنطقة','original':'الصورة الكاملة','stats':'قياسات منطقة الاهتمام','hist':'توزيع شدة البكسلات','export':'تنزيل صورة المعاينة','report':'تنزيل تقرير القياسات','limits':'هذه أداة بحثية لعرض الصور والقياسات. لا تحدد مرضًا ولا تنتج تشخيصًا أو تقسيمًا تشريحيًا معتمدًا. يلزم نموذج متخصص ومتحقق منه لأي كشف مرضي.','source':'معلومات الملف','interpret':'تفسير القياسات'},
        'Deutsch':{'title':'Medizinischer Forschungsbildbetrachter','upload':'Medizinisches Bild hochladen','type':'Bildgebungsart (manuell prüfen)','slice':'Schicht','axis':'Achse','window':'Intensitätsfenster','gamma':'Gamma','sharp':'Schärfe','invert':'Invertieren','roi':'Untersuchungsbereich (ROI)','zoom':'ROI vergrößern','original':'Gesamtbild','stats':'ROI-Messwerte','hist':'Intensitätshistogramm','export':'Vorschau herunterladen','report':'Messbericht herunterladen','limits':'Nur Forschungsanzeige und Messungen. Keine Krankheitsdetektion, Diagnose oder validierte anatomische Segmentierung. Dafür sind spezifisch validierte Modelle nötig.','source':'Dateimetadaten','interpret':'Interpretation der Messungen'},
        'English':{'title':'Medical research image workstation','upload':'Upload medical image','type':'Imaging modality (verify manually)','slice':'Slice','axis':'Axis','window':'Intensity window','gamma':'Gamma','sharp':'Sharpness','invert':'Invert','roi':'Region of interest (ROI)','zoom':'Zoom into ROI','original':'Full image','stats':'ROI measurements','hist':'Intensity histogram','export':'Download preview','report':'Download measurement report','limits':'Research visualization and measurements only. No disease detection, diagnosis, or validated anatomical segmentation. Those require separately validated modality-specific models.','source':'File metadata','interpret':'Measurement interpretation'}}[lang]
    st.markdown('### '+med_ui['title'])
    st.info(med_ui['limits'])
    medical_file=st.file_uploader(med_ui['upload'],type=['dcm','dicom','nii','gz','png','jpg','jpeg','tif','tiff'],key='medical_upload')
    if medical_file:
        try:
            study_hash=hashlib.sha256(medical_file.getvalue()).hexdigest()
            if st.session_state.get('medical_hash')!=study_hash:
                st.session_state['medical_hash']=study_hash
                st.session_state.pop('med_explanation',None)
                st.session_state.pop('med_explanation_hash',None)
                st.session_state.pop('evidence_status',None)
                st.session_state['medical_study']=load_study(medical_file.name,medical_file.getvalue())
            volume,meta=st.session_state['medical_study']
            st.markdown('#### '+{'العربية':'تفاصيل الدراسة والفحص','Deutsch':'Angaben zur Untersuchung','English':'Research / examination details'}[lang])
            st.caption({'العربية':'لا تُدخل معلومات تعريفية عن المريض في تطبيق عام.','Deutsch':'Keine identifizierenden Patientendaten in einer öffentlichen Anwendung eingeben.','English':'Do not enter identifying patient data into a public app.'}[lang])
            med_project=st.text_input({'العربية':'عنوان البحث أو الدراسة','Deutsch':'Forschungstitel / Studienname','English':'Research title / Study name'}[lang],key='med_project')
            med_patient=st.text_input({'العربية':'رمز الحالة المجهول (اختياري)','Deutsch':'Anonyme Fallkennung (optional)','English':'Patient name or anonymous case ID (optional)'}[lang],key='med_patient')
            med_condition=st.text_input({'العربية':'الحالة المشتبه بها أو سؤال البحث (اختياري)','Deutsch':'Verdachtsdiagnose / Forschungsfrage (optional)','English':'Suspected disease / clinical research question (optional)'}[lang],key='med_condition')
            med_notes=st.text_area({'العربية':'السياق السريري والملاحظات (اختياري)','Deutsch':'Klinischer Kontext / Notizen (optional)','English':'Clinical context / research notes (optional)'}[lang],key='med_notes',height=80)
            choices=['Unverified','X-ray / CR / DX','CT','MRI','Ultrasound','PET / SPECT','Other']
            modality=st.selectbox(med_ui['type'],choices,index=choices.index(meta['modality']) if meta['modality'] in choices else 0)
            if volume.ndim==3:
                axis=st.selectbox(med_ui['axis'],[0,1,2],index=2)
                idx=st.slider(med_ui['slice'],0,volume.shape[axis]-1,volume.shape[axis]//2)
            else:axis=0;idx=0
            arr=get_slice(volume,idx,axis)
            lo,hi=[float(x) for x in np.percentile(arr,[1,99])]
            if hi<=lo:hi=lo+1
            # Percentile window controls avoid float range overflow on unusual scans.
            qlo,qhi=st.slider(med_ui['window'],0,100,(1,99),key='medical_window')
            low,high=[float(x) for x in np.percentile(arr,[qlo,qhi])]
            a,b,c=st.columns(3)
            gamma=a.slider(med_ui['gamma'],0.2,3.0,1.0,0.1)
            sharp=b.slider(med_ui['sharp'],0.0,3.0,0.0,0.1)
            invert=c.checkbox(med_ui['invert'],value=bool(meta.get('invert',False)))
            img=render_slice(arr,low,high,invert,gamma,sharp)
            width,height=img.size
            # ROI controls are explicit coordinates; crop is always bounded.
            st.markdown('#### '+med_ui['roi'])
            x0,x1=st.slider('X (px)',0,width,(width//4,max(width//4+1,3*width//4)))
            y0,y1=st.slider('Y (px)',0,height,(height//4,max(height//4+1,3*height//4)))
            if x1<=x0 or y1<=y0:raise ValueError('ROI must have positive dimensions')
            from PIL import ImageDraw
            annotated=img.convert('RGB');d=ImageDraw.Draw(annotated);d.rectangle((x0,y0,x1-1,y1-1),outline='#00e3cd',width=max(2,width//350))
            col_a,col_b=st.columns(2)
            with col_a:
                st.caption(med_ui['original']);st.image(annotated,use_container_width=True)
            with col_b:
                st.caption(med_ui['zoom']);st.image(img.crop((x0,y0,x1,y1)).resize((min(900,max(200,(x1-x0)*2)),min(900,max(200,(y1-y0)*2)))),use_container_width=True)
            st.caption({'العربية':'يمكنك تكبير الصور أيضًا من أداة عرض Streamlit؛ مستطيل الفيروز يحدد المنطقة المقاسة.','Deutsch':'Das türkisfarbene Rechteck zeigt den Messbereich; die Vorschau kann zusätzlich vergrößert werden.','English':'The teal rectangle marks the measured ROI. You can also enlarge the image preview.'}[lang])
            stats=roi_statistics(arr,(x0,y0,x1,y1),meta.get('spacing_mm') if volume.ndim==2 or axis==2 else None)
            st.markdown('#### '+med_ui['stats'])
            from medical_experience import explain_stats
            st.info(explain_stats(stats,lang))
            st.markdown('#### '+med_ui['hist'])
            roi=arr[y0:y1,x0:x1]
            counts,edges=np.histogram(roi,bins=64)
            hist=pd.DataFrame({'Intensity':(edges[:-1]+edges[1:])/2,'Count':counts})
            st.bar_chart(hist.set_index('Intensity'))
            explanation={'العربية':'المتوسط والانحراف المعياري يصفان توزيع الشدة داخل المستطيل المختار، ولا يحددان مرضًا. لا تقارن الشدة بين صور مختلفة دون توحيد المعايرة.','Deutsch':'Mittelwert und Standardabweichung beschreiben die Intensitätsverteilung in der ROI, nicht eine Erkrankung. Vergleiche erfordern eine geeignete Kalibrierung.','English':'Mean and standard deviation describe pixel intensity inside the selected rectangle, not a disease. Cross-image comparisons require appropriate calibration.'}[lang]
            st.info(explanation)
            st.markdown('#### '+{'العربية':'محرر التقسيم التفاعلي — فرشاة ومستطيل ومضلع','Deutsch':'Interaktiver Segmentierungseditor — Pinsel, Rechteck, Polygon','English':'Interactive segmentation editor — brush, rectangle, polygon'}[lang])
            from segmentation_editor import run_editor
            run_editor(st,img,key=f'editor_{study_hash[:12]}_{axis}_{idx}',spacing=meta.get('spacing_mm'),lang=lang)
            with st.expander({'العربية':'تحديد المضلع بالإحداثيات (أداة متقدمة)','Deutsch':'Polygonkoordinaten (erweitert)','English':'Polygon coordinates (advanced)'}[lang],expanded=False):
                st.markdown('#### '+{'العربية':'تحديد يدوي للمناطق (مضلع)','Deutsch':'Manuelle Segmentierung (Polygon)','English':'Manual polygon segmentation'}[lang])
                st.caption({'العربية':'أدخل رؤوس المضلع كنسب مئوية (0–100) من عرض الصورة وارتفاعها؛ هذا تحديد يدوي وليس اكتشافًا تشريحيًا آليًا.','Deutsch':'Polygonpunkte als Prozentwerte (0–100) von Bildbreite und -höhe. Manuelle Markierung, keine automatische Organerkennung.','English':'Enter polygon vertices as percentages (0–100) of image width and height. This is manual annotation, not automatic organ recognition.'}[lang])
                points_text=st.text_area('Polygon X,Y (%)',value='25,25\n75,25\n75,75\n25,75',height=110,key='med_polygon')
                try:
                    points=[tuple(float(v.strip()) for v in line.split(',')) for line in points_text.strip().splitlines() if line.strip()]
                    mask,mask_stats=polygon_segmentation(arr,points)
                    overlay=mask_overlay(img,mask)
                    st.image(overlay,caption='Manual ROI overlay',width=650)
                    st.markdown('**'+medlabel(target,'area')+'**')
                    st.metric(medlabel(target,'portion'),f"{mask_stats['fraction_of_image']*100:.1f}%")
                    st.caption(medlabel(target,'notdiagnostic'))
                    from PIL import Image
                    st.download_button({'العربية':'تنزيل قناع التحديد PNG','Deutsch':'Segmentierungsmaske als PNG speichern','English':'Download segmentation mask PNG'}[lang],png_bytes(Image.fromarray((mask*255).astype('uint8'))),'atlas_manual_mask.png','image/png')
                except (ValueError,TypeError) as exc:st.warning(str(exc))
            # Single research workflow: references retrieved in the background, never shown as a raw feed.
            from medical_experience import localized, explain_stats, summarize_evidence
            L=lambda key:localized(lang,key)
            st.markdown('#### '+L('automatic_title'))
            st.caption(L('automatic_caption'))
            if st.button(L('analyze_button'),key='unified_medical_review',disabled=not bool(api_key),type='primary'):
                with st.spinner(L('analyzing')):
                    try:
                        description=explain_medical_image(api_key,model,img,modality,target,meta)
                        st.session_state['med_explanation']=description
                        st.session_state['med_explanation_hash']=study_hash
                        evidence=search_from_image(api_key,model,img,modality)
                        st.session_state['auto_image_evidence']=evidence
                        st.session_state['auto_image_evidence_hash']=study_hash
                        st.session_state['evidence_status']=summarize_evidence(evidence,lang)
                    except Exception:
                        st.session_state['evidence_status']=L('unavailable')
            if st.session_state.get('med_explanation_hash')==study_hash:
                st.markdown(st.session_state['med_explanation'])
                st.caption(st.session_state.get('evidence_status',L('unavailable')))
            with st.expander({"العربية":"إعدادات البحث المتقدمة (اختيارية)","Deutsch":"Erweiterte Forschungswerkzeuge (optional)","English":"Advanced research tools (optional)"}[lang],expanded=False):
                st.markdown('#### '+{'العربية':'مقارنة الحالات المرجعية (تجريبية)','Deutsch':'Vergleich mit Referenzfällen (experimentell)','English':'Reference case comparison (experimental)'}[lang])
                st.caption('Compares visual appearance with independently verified, licensed, anonymized reference cases. Similarity is NOT a disease prediction. Cloud-local records may disappear on restart; configure persistent private storage for long-term use.')
                anatomy=st.selectbox('Reference anatomy',['Brain','Chest / Lung','Heart','Knee','Other bone','Other'],key='ref_anatomy')
                reference_path=os.environ.get('ATLAS_REFERENCE_DB','/tmp/atlas_east_references.sqlite3')
                try:
                    reference_library=ReferenceLibrary(reference_path)
                    with st.expander('Register a verified reference image (optional)'):
                        st.warning('Do not upload identifiable patient data. Only use independently confirmed labels and images you are authorized to process.')
                        ref_file=st.file_uploader('Verified reference PNG/JPG',type=['png','jpg','jpeg'],key='ref_image')
                        ref_label=st.text_input('Expert-confirmed reference label',key='ref_label')
                        ref_source=st.text_input('Published source / DOI / provenance',key='ref_source')
                        ref_license=st.text_input('Image license or documented permission',key='ref_license')
                        ref_confirm=st.checkbox('I confirm expert label verification and permission to use this de-identified reference',key='ref_confirm')
                        if st.button('Register verified reference',key='ref_register'):
                            if not ref_file:st.warning('Select a reference image first.')
                            else:
                                from PIL import Image as PILImage
                                reference_library.add(PILImage.open(io.BytesIO(ref_file.getvalue())),modality=modality,anatomy=anatomy,label=ref_label,source=ref_source,license=ref_license,verified=ref_confirm,consent=ref_confirm)
                                st.success('Reference descriptor stored. No source image stored.')
                    if st.button('Compare against verified references',key='ref_compare'):
                        st.session_state['reference_matches']=reference_library.search(img,modality=modality,anatomy=anatomy)
                        st.session_state['reference_matches_hash']=study_hash
                    if st.session_state.get('reference_matches_hash')==study_hash:
                        matches=st.session_state.get('reference_matches',[])
                        if matches:st.dataframe(pd.DataFrame(matches),hide_index=True)
                        else:st.info(medlabel(target,'missing'))
                except Exception as ref_exc:st.warning(f'Reference engine: {type(ref_exc).__name__}: {ref_exc}')
                st.markdown('#### '+{'العربية':'الذاكرة البحثية ومراجعة الأدلة','Deutsch':'Forschungsarchiv und Evidenzbewertung','English':'Research memory and evidence synthesis'}[lang])
                st.caption('Private opt-in research memory: independently reviewed, de-identified summaries only. No automatic learning from AI guesses or patient images. Persistent storage must be configured by the deployment owner.')
                memory_path=os.environ.get('ATLAS_RESEARCH_DB','/tmp/atlas_east_research.sqlite3')
                try:
                    memory=ResearchMemory(memory_path)
                    with st.expander('Register a reviewed research finding'):
                        memory_title=st.text_input('Study title',key='memory_title')
                        memory_domain=st.selectbox('Study domain',['Medical imaging','Clinical research','Pharmacy','Engineering','Other'],key='memory_domain')
                        memory_summary=st.text_area('De-identified scientific summary and verified findings',key='memory_summary')
                        memory_source=st.text_input('DOI / PubMed URL / verifiable source',key='memory_source')
                        memory_license=st.text_input('License / documented permission',key='memory_license')
                        memory_ok=st.checkbox('I confirm expert review, permission and removal of all identifying patient data',key='memory_consent')
                        if st.button('Save reviewed research evidence',key='memory_save'):
                            try:
                                memory.add_study(memory_title,memory_domain,memory_summary,memory_source,memory_license,expert_reviewed=memory_ok,permission=memory_ok)
                                st.success('Reviewed evidence saved in the configured database.')
                            except ValueError as exc:st.warning(str(exc))
                    search_terms=st.text_input('Search prior verified research findings',value=med_condition,key='memory_query')
                    if st.button('Retrieve previous research',key='memory_retrieve'):
                        st.session_state['memory_results']=memory.retrieve(search_terms)
                        st.session_state['memory_results_hash']=study_hash
                    if st.session_state.get('memory_results_hash')==study_hash:
                        for finding in st.session_state.get('memory_results',[]):
                            st.markdown('**'+finding['title']+'** · '+finding['provenance'])
                            st.write(finding['summary'])
                except Exception as mem_exc:st.warning('Research memory unavailable: '+str(mem_exc))
                st.markdown('#### Scientific literature evidence (PubMed)')
                st.caption('On demand: searches public biomedical publications using anatomy and disease/finding terms only. Does not upload the image, patient name or clinical notes. Published papers are not automatically matched to this patient or proof of disease.')
                literature_query=st.text_input('Disease / radiological finding for literature search (no patient data)',value='',key='literature_query')
                if st.button('Search peer-reviewed medical literature',key='pubmed_search'):
                    try:
                        with st.spinner('Retrieving PubMed publications…'):
                            st.session_state['med_literature']=search_pubmed(anatomy,literature_query)
                            st.session_state['med_literature_hash']=study_hash
                    except Exception as literature_exc:st.warning(f'Literature search unavailable: {type(literature_exc).__name__}: {literature_exc}')
                if st.session_state.get('med_literature_hash')==study_hash:
                    papers=st.session_state.get('med_literature',[])
                    if not papers:st.info('No matching PubMed records found for this search.')
                    for paper in papers:
                        st.markdown(f"**[{paper['title']}]({paper['url']})** · PMID {paper['pmid']}")
                        with st.expander('Read abstract'):st.write(paper['abstract'] or 'No abstract available.')
                st.markdown('#### Federated research evidence · Europe PMC + Crossref')
                st.caption('Background retrieval of published research metadata. Searches contain only the terms you enter, never patient names or uploaded images. Ranking indicates topical relevance, not diagnostic probability.')
                federated_terms=st.text_input('Research finding / suspected condition / engineering topic (no identifying details)',key='federated_terms')
                federated_domain=st.selectbox('Research field',['medical','engineering','pharmacy'],key='federated_domain')
                if st.button('Search research evidence across sources',key='federated_search'):
                    try:
                        with st.spinner('Searching public scholarly indexes…'):
                            st.session_state['federated_evidence']=federated_search(federated_terms,domain=federated_domain)
                            st.session_state['federated_hash']=study_hash
                            st.session_state.pop('federated_brief_result',None)
                    except Exception as fed_exc:st.warning(f'Federated search unavailable: {type(fed_exc).__name__}: {fed_exc}')
                if st.session_state.get('federated_hash')==study_hash:
                    fed=st.session_state.get('federated_evidence',{})
                    for record in fed.get('records',[]):
                        st.markdown(f"**[{record['title']}]({record['url']})** · {record['source']} · {record.get('year','')} · topical relevance {record['relevance_score']:.2f}")
                        with st.expander('Research abstract / indexed summary'):
                            st.write(record.get('abstract') or 'No abstract indexed.')
                    if fed.get('provider_errors'):st.warning('Some sources unavailable: '+', '.join(fed['provider_errors']))
                    if fed.get('records') and st.button('Build cited research leads',key='federated_brief'):
                        try:st.session_state['federated_brief_result']=evidence_brief(fed['records'],federated_terms,federated_domain)
                        except ValueError as exc:st.warning(str(exc))
                    if st.session_state.get('federated_brief_result'):
                        st.json(st.session_state['federated_brief_result'])
                assessment=evidence_assessment(
                    st.session_state.get('reference_matches',[]) if st.session_state.get('reference_matches_hash')==study_hash else [],
                    st.session_state.get('med_literature',[]) if st.session_state.get('med_literature_hash')==study_hash else [])
                st.markdown('#### '+medlabel(target,'audit'))
                st.info({'German':'Die Literaturrecherche liefert Forschungsquellen, keine gesicherte Diagnose.','Arabic':'المراجع العلمية تساعد في تفسير الصورة ولا تثبت تشخيصًا.','English':'Published research provides context, not a confirmed diagnosis.'}[target])
                st.markdown('#### '+medlabel(target,'search'))
                st.caption({'German':'Die Bildanalyse erzeugt anonymisierte Suchbegriffe. Europe PMC und Crossref werden automatisch durchsucht. Dies ist keine Diagnose und kein Abgleich mit Original-Röntgenbildern.','Arabic':'يستخرج النظام كلمات بحث غير تعريفية من الصورة ثم يبحث تلقائيًا في Europe PMC وCrossref. هذا ليس تشخيصًا ولا مطابقة لصور أشعة أصلية.','English':'The image produces non-identifying search terms for automatic Europe PMC/Crossref retrieval. This is neither diagnosis nor direct published-image matching.'}[target])
                if st.button({'German':'Bild analysieren und Fachliteratur automatisch suchen','Arabic':'تحليل الصورة والبحث تلقائيًا عن المراجع','English':'Analyze image and automatically search literature'}[target],key='automatic_image_evidence',disabled=not bool(api_key)):
                    try:
                        with st.spinner({'German':'Bild und Quellen werden ausgewertet…','Arabic':'يجري تحليل الصورة واسترجاع المصادر…','English':'Analyzing image and retrieving references…'}[target]):
                            st.session_state['auto_image_evidence']=search_from_image(api_key,model,img,modality)
                            st.session_state['auto_image_evidence_hash']=study_hash
                    except Exception as exc:
                        st.warning(f'Automatic literature retrieval unavailable: {type(exc).__name__}: {exc}')
                if st.session_state.get('auto_image_evidence_hash')==study_hash:
                    result=st.session_state['auto_image_evidence']
                    st.write(' · '.join(result['visual_terms']['observations']))
                    st.markdown('**'+medlabel(target,'sources')+'**')
                    for record in result['literature'].get('records',[]):
                        st.markdown(f"[{record['title']}]({record['url']}) — {record['source']}")
                    if not result['literature'].get('records'):st.info(medlabel(target,'none'))
                # Optional hybrid GPU service: explicit permission and verified model provenance.
                with st.expander({'German':'Spezialisiertes Forschungsmodell (optionaler GPU-Dienst)','Arabic':'نموذج بحثي متخصص (خدمة GPU اختيارية)','English':'Specialist research model (optional GPU service)'}[target]):
                    from hybrid_inference import infer_remote, format_findings
                    from dataset_catalog import catalog
                    endpoint=st.secrets.get('ATLAS_GPU_ENDPOINT','')
                    service_token=st.secrets.get('ATLAS_GPU_TOKEN','')
                    labels={'German':{'choice':'Bildtyp','consent':'Ich bin berechtigt, dieses anonymisierte Bild an den externen Dienst zu senden','run':'Forschungsmodell ausführen','unavailable':'Kein GPU-Dienst konfiguriert. Keine Krankheitsvorhersage verfügbar.'},'Arabic':{'choice':'نوع الصورة','consent':'أوافق على إرسال هذه الصورة المنزوعة البيانات التعريفية إلى الخدمة الخارجية ولدي الإذن بذلك','run':'تشغيل النموذج البحثي','unavailable':'لم تُضبط خدمة GPU؛ لا يوجد تنبؤ مرضي متخصص.'},'English':{'choice':'Image task','consent':'I am authorized to send this de-identified image to the external service','run':'Run research model','unavailable':'GPU service not configured. No specialist disease prediction available.'}}[target]
                    task=st.selectbox(labels['choice'],['chest_xray','brain_mri','knee_xray','cardiac','bone_xray'],key='hybrid_task')
                    permission=st.checkbox(labels['consent'],key='hybrid_consent')
                    if not endpoint or not service_token:st.info(labels['unavailable'])
                    if st.button(labels['run'],disabled=not (endpoint and service_token and permission),key='hybrid_run'):
                        try:
                            prediction=infer_remote(img,task,endpoint,service_token,permission)
                            st.session_state['hybrid_result']=prediction
                            st.session_state['hybrid_hash']=study_hash
                        except Exception as e:st.warning(f'{type(e).__name__}: {e}')
                    if st.session_state.get('hybrid_hash')==study_hash:
                        st.markdown(format_findings(st.session_state['hybrid_result'],target))
            st.markdown('#### '+{'العربية':'شرح طبي بحثي للصورة','Deutsch':'Medizinisch-wissenschaftliche Bildbeschreibung','English':'Medical research image explanation'}[lang])
            st.caption({'العربية':'المراجعة الاختيارية تستخدم خدمة معالجة خارجية. لا ترفع بيانات مرضى تعريفية دون إذن مناسب.','Deutsch':'Optionale Bildprüfung nutzt einen externen Verarbeitungsdienst. Keine identifizierbaren Patientendaten ohne Berechtigung hochladen.','English':'Optional image review uses an external processing service. Do not upload identifiable patient data without authorization.'}[lang])
            if st.button({'العربية':'شرح الصورة طبيًا (بحثي فقط)','Deutsch':'Bild medizinisch erklären (Forschung)','English':'Explain image medically (research only)'}[lang],disabled=not bool(api_key),key='medical_explain'):
                with st.spinner('Reviewing visible anatomy and uncertainty…'):
                    try:
                        st.session_state['med_explanation']=explain_medical_image(api_key,model,img,modality,target,meta)
                        st.session_state['med_explanation_hash']=study_hash
                    except Exception as exc:st.warning(f'Medical description unavailable: {type(exc).__name__}: {exc}')
            # The unified review already presents the interpretation once.
            safe_meta={k:v for k,v in meta.items() if k not in ('patient_name','patient_id','patient_age','study_date')}
            # Technical metadata stays internal; never expose raw JSON in the clinical view.
            st.download_button(med_ui['export'],png_bytes(annotated),'atlas_east_research_preview.png','image/png')
            import json
            report_data={'notice':med_ui['limits'],'file_type':meta['source'],'user_selected_modality':modality,'slice_axis':axis,'slice_index':idx,'roi_px':[x0,y0,x1,y1],'statistics':stats,'interpretation':explanation,'research_title':med_project,'patient_or_case_id':med_patient,'research_question':med_condition,'clinical_notes':med_notes,'literature':st.session_state.get('med_literature',[]) if st.session_state.get('med_literature_hash')==study_hash else [],'evidence_assessment':assessment,'federated_literature':(st.session_state.get('auto_image_evidence',{}).get('literature',{}).get('records',[]) if st.session_state.get('auto_image_evidence_hash')==study_hash else st.session_state.get('federated_evidence',{}).get('records',[]) if st.session_state.get('federated_hash')==study_hash else [])}
            try:
                medical_pdf=build_medical_pdf(annotated,report_data,st.session_state.get('med_explanation','') if st.session_state.get('med_explanation_hash')==study_hash else '',language=target)
                st.download_button(med_ui['report']+' (PDF)',medical_pdf,'ATLAS_EAST_Medical_Research_Report.pdf','application/pdf',key='medical_pdf_download')
            except Exception as pdf_exc:
                st.error(f'PDF export failed: {type(pdf_exc).__name__}: {pdf_exc}')
        except Exception as exc:
            st.error(f'{T("med_error")}: {type(exc).__name__}: {exc}')
if selected_section==6:
    st.markdown('### '+T('sim_title'))
    st.caption(T('sim_caption'))
    p1,p2,p3,p4=st.columns(4)
    base=p1.number_input(T('sim_initial'),value=1.0)
    slope=p2.number_input(T('sim_slope'),value=0.15)
    n=p3.number_input(T('sim_steps'),min_value=2,max_value=1000,value=20)
    step=p4.number_input(T('sim_step'),min_value=0.00001,value=1.0)
    curve=simulate_linear(base,slope,n,step)
    st.line_chart(curve.set_index('input_delta'))
    st.info(scenario_summary(curve,lang))
    with st.expander('Evidence-based quantitative model from measured research data (experimental)'):
        st.caption('Paste paired numerical observations from a verified table. Fits a polynomial, evaluates cross-validation and bootstrap intervals. No automatic extraction or causal claims.')
        observations=st.text_area('X,Y — one pair per line (decimal dot)',placeholder='1,2.1\n2,3.7\n3,5.2',key='fit_pairs')
        degree=st.selectbox('Model degree',[1,2],key='fit_degree')
        if st.button('Fit and validate scientific model',key='fit_run'):
            try:
                pairs=[]
                for line in observations.strip().splitlines():
                    if not line.strip():continue
                    a,b=line.split(',');pairs.append((float(a),float(b)))
                fitted=fit_quantitative_model([p[0] for p in pairs],[p[1] for p in pairs],degree=degree)
                st.session_state['fitted_research_model']=fitted
                st.session_state['fitted_research_pairs']=pairs
            except (ValueError,TypeError) as fit_exc:st.error(str(fit_exc))
        if st.session_state.get('fitted_research_model'):
            fitted=st.session_state['fitted_research_model'];st.json(fitted)
            xs=np.linspace(*fitted['x_observed_range'],100)
            ys=predict_quantitative(fitted,xs)
            st.line_chart(pd.DataFrame({'X':xs,'Model Y':ys}).set_index('X'))
            st.download_button('Download validated model JSON',__import__('json').dumps(fitted,indent=2).encode(),'atlas_east_fitted_model.json','application/json',key='fit_download')
    st.markdown(interpret_simulation(curve,lang))
    if api_key and doc and st.button({'العربية':'مناقشة السيناريو علميًا في سياق المشروع','Deutsch':'Szenario im Projektkontext diskutieren','English':'Discuss scenario in project context'}[lang],key='simulation_explain'):
        from research_interpretation import discuss_simulation
        try:st.session_state['simulation_explanation']=discuss_simulation(api_key,model,doc,curve,target)
        except Exception as exc:st.warning(f'Simulation discussion unavailable: {type(exc).__name__}: {exc}')
    if st.session_state.get('simulation_explanation'):st.markdown(st.session_state['simulation_explanation'])
    st.download_button(T('sim_download'),curve.to_csv(index=False).encode('utf-8-sig'),'atlas_hypothetical_simulation.csv')
if selected_section==7:
    if links:
        st.dataframe(pd.DataFrame({T('ref_heading'):links}),use_container_width=True)
        if check and st.button(T('ref_check'),key='check_urls'):
            with st.spinner(T('ref_working')):st.session_state['checks']=verify_links(links)
        if st.session_state.get('checks'):st.dataframe(pd.DataFrame(st.session_state['checks']))
    else:st.info(T('ref_empty'))
    st.caption(T('ref_caution'))
if selected_section==8:
    if analysis and doc:
        proposed=analysis.get('proposed_title') or os.path.splitext(doc['name'])[0]
        project_title=st.text_input(T('project'),value=proposed)
        report_type=st.radio(T('format'),[T('audit'),T('manuscript')],horizontal=True)
        manuscript=report_type==T('manuscript')
        st.info(T('manuscript_warning'))
        st.markdown('#### '+T('evidence'))
        for i,item in enumerate(analysis.get('evidence',[])):
            if not isinstance(item,dict):continue
            mark='✓' if item.get('verified_quote') else '⚠'
            with st.expander(f'{mark} {T("page")} {item.get("page","?")} — {str(item.get("claim",""))[:90]}'):
                st.write(item.get('claim',''))
                st.code(item.get('excerpt',''))
                st.caption(T('verified') if item.get('verified_quote') else T('unverified'))
        for warning in analysis.get('warnings',[]):st.warning(str(warning))
        st.caption(analysis.get('_coverage',''))
        try:
            pdf=build_pdf(doc,analysis,links,title=project_title,manuscript=manuscript,language=target)
            st.download_button(T('download'),pdf,file_name='ATLAS_EAST_Research_Manuscript_DRAFT.pdf' if manuscript else 'ATLAS_EAST_Scientific_Audit.pdf',mime='application/pdf',type='primary',use_container_width=True)
        except Exception as exc:st.error(f'{T("pdf_error")}: {exc}')
    else:st.info(T('missing'))

# Independent book-production workflow: no dependency on the audit/manuscript export.
st.divider()
st.header('📚 '+T('book_studio'))
st.caption(T('book_intro'))
if doc:
    bc1,bc2=st.columns(2)
    with bc1:
        book_lang=st.selectbox(T('book_language'),['Arabic','German','English'],index={'العربية':0,'Deutsch':1,'English':2}[lang],key='book_language',format_func=lambda v: {'Arabic':{'English':'Arabic','Deutsch':'Arabisch','العربية':'العربية'},'German':{'English':'German','Deutsch':'Deutsch','العربية':'الألمانية'},'English':{'English':'English','Deutsch':'Englisch','العربية':'الإنجليزية'}}[v][lang])
        trim=st.selectbox(T('book_size'),['A5','A4'],key='book_trim')
    with bc2:
        book_author=st.text_input(T('book_author'),value=T('book_author_default'),key='book_author')
        st.caption(T('book_rights'))
    st.caption({'العربية':'المشاريع الطويلة قد تتطلب عشرات طلبات API وتكلفة ملحوظة. يمكن استئناف الأجزاء المكتملة بعد انقطاع العملية.','Deutsch':'Lange Dokumente können viele API-Aufrufe und Kosten verursachen. Abgeschlossene Abschnitte können nach Unterbrechungen fortgesetzt werden.','English':'Long documents may require many API calls and incur significant cost. Completed sections can be resumed after interruptions.'}[lang])
    if st.button(T('book_generate'),type='primary',disabled=not bool(api_key),key='book_generate'):
        try:
            with st.spinner(T('book_working')):
                resume_key=f'book_progress_{signature}_{book_lang}_{model}'
                prior=st.session_state.get(resume_key,[])
                progress_bar=st.progress(0,text=T('book_working'))
                def save_progress(done,total,chapters):
                    st.session_state[resume_key]=list(chapters)
                    progress_bar.progress(done/total,text=f'{done}/{total}')
                st.session_state['book_content']=create_book_content(doc,api_key,model,book_lang,analysis,progress=save_progress,resume=prior)
                st.session_state.pop(resume_key,None)
                st.session_state['book_signature']=(signature,book_lang)
        except Exception as exc:
            st.error(f'{T("book_error")}: {type(exc).__name__}: {exc}')
    book=st.session_state.get('book_content')
    if book and st.session_state.get('book_signature')==(signature,book_lang):
        st.success(T('book_prepared')+' · '+book['coverage'])
        title=st.text_input(T('book_title'),value=book['title'],key='book_title')
        book['title']=title
        st.write(T('chapters')+':',len(book['chapters']))
        for i,ch in enumerate(book['chapters']):
            with st.expander(f"{i+1}. {ch['heading']} · {T('page')} {ch['page']}"):
                for paragraph in ch['paragraphs']:st.write(paragraph)
        show_tables=st.checkbox(T('include_tables'),value=True,key='book_tables')
        show_figures=st.checkbox(T('include_figures'),value=True,key='book_figures')
        try:
            book_pdf=build_book_pdf(doc,book,links,book_author,show_figures,show_tables,trim)
            st.download_button(T('book_download'),book_pdf,'ATLAS_EAST_Scientific_Book_'+book_lang+'.pdf','application/pdf',type='primary',key='download_book')
            st.caption(T('book_print_note'))
        except Exception as exc:st.error(f'{T("book_pdf_error")}: {exc}')
    elif book:
        st.info(T('book_regenerate'))
else:
    st.info(T('book_need_upload'))
