# ATLAS EAST V3.8 — Research Intelligence Foundation

This is an incremental addition to V3.7, not a trained diagnostic system.

- atlas_intelligence.py: automated de-identified literature retrieval from image-derived descriptions; no image or patient name is sent to the literature API.
- Source-anchored extraction of quantities, units and candidate equations for pharmacy/engineering research.
- Tests verify extraction and retrieval routing.

IMPORTANT: No new image classifier weights were trained or downloaded. No sensitivity, specificity or clinical accuracy is claimed. Actual disease prediction requires licensed labelled datasets, validated organ/modality-specific models, held-out external evaluation, calibration, and clinician oversight. No automatic learning from unverified prior predictions.

For future deployment, use a GPU inference service with authenticated endpoints and consent/privacy controls. Check each model and dataset license before use. MONAI model zoo: https://project-monai.github.io/model-zoo.html
