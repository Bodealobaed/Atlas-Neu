# ATLAS EAST V3.6 — Conservative Book Layout & Arabic Table Audit

- Book PDF: media are associated with the nearest source-page chapter and interleaved among paragraphs; figures and tables are no longer collected as a final appendix. This is **page-based approximation**, not yet caption-to-paragraph semantic matching.
- Cover: text is rendered on an opaque area so that subject-themed vector graphics cannot cross the title.
- `table_quality.py`: reusable Arabic/bilingual table normalization, structural validation and independent-pass numeric comparison. It **does not** magically reconstruct corrupted Arabic OCR or certify transcription accuracy. It is not yet wired to all table extraction paths.
- No new clinical diagnostic model is claimed. Existing research-only evidence search remains as in V3.5. The existing manuscript/report generator is not an accepted journal article, nor a trademark registration.
- Run `python -m pytest -q tests` before deployment. Do not upload actual patient names to a public Streamlit deployment.
