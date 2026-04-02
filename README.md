# E Hospital Explainer

AI-Powered Medical Report Translation System - Translates complex medical reports into patient-friendly language.

## 🎯 Project Overview

This is a full-stack web application that uses GPT-4 to explain medical test results in simple, patient-friendly language.

**University of Ottawa - Masters Project**

### Features

- ✅ Modern professional web interface
- ✅ GPT-4 AI integration for medical explanations
- ✅ Support for text input and file upload (PDF, TXT, DOCX)
- ✅ Medical report parser (73 tests, 14 categories)
- ✅ Reference ranges database
- ✅ Medical terminology glossary
- ✅ Download results functionality
- ✅ 90%+ coverage of common medical tests

## 🛠️ Technology Stack

**Backend:**
- Python 3.10+
- Flask 2.3
- OpenAI GPT-4 API
- pandas, PyPDF2, python-docx

**Frontend:**
- HTML5, CSS3, JavaScript
- Font Awesome icons
- Google Fonts (Inter)

**Database:**
- CSV-based reference ranges (85 entries)
- JSON medical terminology (100+ terms)

## 📁 Project Structure
```
complete-project/
├── app.py                 # Flask application entry point
├── modules/
│   ├── parser.py         # Medical report parser
│   ├── validator.py      # Input validation
│   ├── ai_service.py     # GPT-4 integration
│   ├── formatter.py      # Response formatting
│   └── utils.py          # Utilities
├── data/
│   ├── reference_ranges.csv
│   └── medical_terms.json
├── e_hospital_explainer_professional.html
└── requirements.txt
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.10 or higher
- OpenAI API key

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/e-hospital-explainer.git
cd e-hospital-explainer
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

5. **Run the backend**
```bash
PORT=5001 python app.py
```

6. **Run the frontend**

Open a new terminal:
```bash
python3 -m http.server 8000
```

Then open: http://localhost:8000/e_hospital_explainer_professional.html

## 📊 Coverage

- **73 Medical Tests** across 14 categories
- **Categories:** CBC, Lipid Panel, BMP, Liver Function, Kidney Function, Thyroid, Diabetes, Cardiac, Coagulation, Iron Studies, Vitamins, Hormones, Tumor Markers, Urinalysis

## 🔒 Security

- Input validation and sanitization
- XSS protection
- File type and size validation
- API key stored in environment variables (not in code)

## ⚠️ Disclaimer

This tool is for educational purposes only and is NOT medical advice. Always consult your healthcare provider for medical decisions.

## 👨‍💻 Author

**Umar Afraz**  
University of Ottawa - Masters Student  
ELG 6131 Medical Diagnostic Project

## 📄 License

This project is for academic purposes.

