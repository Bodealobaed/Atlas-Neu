"""Patient-safe UI language and restrained evidence presentation.
Research retrieval is not disease probability or clinical validation.
"""
WORDS={
 'العربية':{'automatic_title':'التحليل الطبي البحثي ومراجعة الأدلة','automatic_caption':'يفحص البرنامج الصورة ويبحث في المراجع العلمية في الخلفية. نتائج البحث ليست إثباتًا للتشخيص. لا تظهر قوائم المقالات أو بيانات تقنية خام.','analyze_button':'تحليل الصورة ومراجعة الأدلة تلقائيًا','analyzing':'جارٍ تحليل الصورة والتحقق من الأدلة العلمية…','unavailable':'تعذّر استكمال المراجعة الآلية؛ لا يمكن تأكيد النتيجة.'},
 'Deutsch':{'automatic_title':'Medizinische Bildanalyse und Evidenzprüfung','automatic_caption':'Die Bildanalyse und Literaturrecherche erfolgen im Hintergrund. Publikationen beweisen keine Diagnose. Rohdaten und Artikellisten werden nicht angezeigt.','analyze_button':'Bild analysieren und Evidenz automatisch prüfen','analyzing':'Bild und wissenschaftliche Evidenz werden geprüft…','unavailable':'Die automatische Prüfung konnte nicht abgeschlossen werden; keine Bestätigung möglich.'},
 'English':{'automatic_title':'Medical image review and evidence check','automatic_caption':'Image analysis and scholarly retrieval run in the background. Papers do not establish a diagnosis. Raw technical data and publication lists are hidden.','analyze_button':'Analyze image and check evidence automatically','analyzing':'Analyzing image and checking evidence…','unavailable':'Automatic evidence review was incomplete; findings are unconfirmed.'}}
def localized(lang,key):return WORDS.get(lang,WORDS['English'])[key]
def explain_stats(stats,lang):
    def fmt(key):
        v=stats.get(key)
        return f'{v:,.1f}' if isinstance(v,(int,float)) else str(v) if v is not None else None
    # Never interpret intensity as disease likelihood.
    count=fmt('pixel_count');mean=fmt('mean_intensity')
    if lang=='Deutsch':return f'Der ausgewählte Bereich umfasst {count or "–"} Pixel. Die mittlere Bildintensität beträgt {mean or "–"}. Dies sind technische Messwerte, keine Krankheitswahrscheinlichkeiten.'
    if lang=='العربية':return f'تضم المنطقة المختارة {count or "—"} بكسل، ومتوسط شدة الصورة {mean or "—"}. هذه قياسات تقنية وليست احتمالات مرضية.'
    return f'The selected area contains {count or "—"} pixels, with mean image intensity {mean or "—"}. These are technical measurements, not disease probabilities.'
def summarize_evidence(result,lang):
    n=len((result or {}).get('literature',{}).get('records',[]))
    if lang=='Deutsch':return f'Automatische Hintergrundrecherche abgeschlossen ({n} thematisch passende Publikationen). Keine klinische Bestätigung oder validierte Bildähnlichkeit.'
    if lang=='العربية':return f'اكتمل البحث العلمي في الخلفية ({n} منشورات مرتبطة بالموضوع). لا تمثل تأكيدًا سريريًا أو مطابقة صور موثقة.'
    return f'Background literature retrieval completed ({n} topically relevant publications). Not clinical confirmation or validated image matching.'
