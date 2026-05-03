# 🎯 ATS Scanner Pro

AI-powered resume analyzer that evaluates how well your resume matches a job description using **Google Gemini + LangChain**.

---

## 🚀 Features

- 📄 Upload Resume (PDF)
- 🧠 AI-based ATS Score (0–100)
- ✅ Matched Skills Detection
- ❌ Missing Skills Identification
- 💡 Smart Suggestions to Improve Resume
- 🎨 Modern UI built with Streamlit + Custom CSS

---

## 🛠️ Tech Stack

- **Frontend/UI:** Streamlit  
- **AI Model:** Google Gemini (`gemini-3-flash-preview`)  
- **Framework:** LangChain  
- **PDF Parsing:** PyMuPDF (`fitz`)  
- **Data Validation:** Pydantic  

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ats-scanner-pro.git
cd ats-scanner-pro
```
### Create Virtual environment
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
```
### Install DEpendencies
```bash
pip install -r requirements.txt
```
###🔑 Setup API Key
-Go to Google AI Studio
-Generate your Gemini API Key
-Paste it inside the app when running

### ▶️ Run the App
```bash
streamlit run app.py
```
venv\Scripts\activate      # Windows
