# 🧪 SciRAP In Vitro Evaluation Tool

This repository contains an automated Streamlit-based tool for evaluating:
- Reporting Quality (RQ1–RQ24)
- Methodological Quality (MQ1–MQ16)
- Relevance (R1–R4)

### ✨ Features
- Automatic PDF text extraction
- Rule-based evaluation with NLP keyword matching
- Strong/weak/not-reported logic
- Direct/indirect/not-relevant scoring for Relevance
- Numeric scoring (0, 0.5, 1)
- Final study quality rating (High / Moderate / Low)
- CSV downloads for all modules
- Password protection (optional)

---

## 🚀 Deploy Instructions (Streamlit Cloud)

1. Fork / clone this repository into your GitHub.
2. Go to **https://share.streamlit.io**
3. Click **New App**
4. Select your repository
5. Choose `app.py` as the entry file
6. Deploy 🎉

---

## 🔐 Optional: Password Protection

In `app.py`, add:

```python
import streamlit as st
import passwords

pwd = st.text_input("Enter password:", type="password")
if pwd != passwords.PASSWORD:
    st.stop()
