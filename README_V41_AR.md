# ATLAS EAST V4.1 — Medical UI cleanup

- German/Arabic/English translations for examination fields, brush controls, research review and measurements.
- Technical metadata JSON and raw measurement dataframe removed from the standard medical view.
- Literature/reference tools grouped in a collapsed optional expert section.
- One visible button calls existing image description and evidence search, presenting only a short evidence status, not the publication list. Research papers are not disease predictions.
- No GPU service, new diagnostic classifier or clinical validation is included.
- Brush uses streamlit-drawable-canvas; if unsupported by deployment environment, this requires browser compatibility work.
- IMPORTANT: Uploaded medical image is transmitted to OpenAI when the unified analysis button is pressed. Ensure authorization, consent and removal of identifying pixels. Literature searches use generated terms, not raw patient data.
- Tests check modules and syntax, not real-browser deployment or clinical performance.
