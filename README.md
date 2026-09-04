# AIOrbit — AI Models Dataset

## Dataset Summary

- Records: 613
- Unique model names: 613
- Duplicate model names: 0
- Missing model names: 0
- Missing descriptions: 0
- Verified official websites: 453
- Models without a verified official website: 51
- Provider identities resolved: 585
- Verified/retained official logo URLs: 238

## Pipeline

Document / Source Dataset
→ Extraction
→ Cleaning & Normalization
→ Duplicate Removal
→ Provider Entity Resolution
→ Official Website Verification
→ Logo Validation
→ Final Dataset

## Data Quality

Duplicate model names were removed using normalized model identity.

Third-party and placeholder website references were not treated as official websites.

Generic third-party favicon URLs from OpenRouter and Hugging Face were removed from the official logo field rather than being presented as official logos.

Where an official website could not be confidently verified, the official website field was left blank.

## Final Output

data/final/AIOrbit_AI_Models_Final.csv

The final dataset contains model metadata, provider information, descriptions, technical capabilities, licensing, pricing fields, official website information, source references, and verification metadata.
