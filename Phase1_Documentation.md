# Phase 1: Project Setup & System Design
# Medical Diagnostic Engineering - Winter 2026
# AI-Powered Medical Report Explanation System

## Project Overview

**Project Title:** Generative AI-Powered Medical Imaging and Blood Work Explanation Agents

**Objective:** Design and implement an AI-powered system that converts complex medical reports into patient-friendly explanations without providing diagnosis or treatment recommendations.

---

## 1. SYSTEM ARCHITECTURE

### 1.1 Architecture Type: Web-Based Client-Server Architecture

The system follows a **3-tier architecture**:

#### **Tier 1: Presentation Layer (Frontend)**
- **Technology:** HTML5, CSS3, JavaScript
- **Framework:** Bootstrap for responsive design
- **Components:**
  - File upload interface
  - Text input form
  - Results display panel
  - Safety disclaimer banner
  
#### **Tier 2: Application Layer (Backend)**
- **Technology:** Python 3.10+
- **Framework:** Flask (lightweight web framework)
- **Components:**
  - **API Controller:** Handles HTTP requests/responses
  - **Report Parser:** Extracts information from medical reports
  - **Validation Module:** Checks input format and safety
  - **Response Formatter:** Structures output for display

#### **Tier 3: Data & AI Layer**
- **AI Integration:** OpenAI GPT-4 API / Anthropic Claude API
- **Data Storage:** 
  - JSON files for medical terminology
  - CSV files for reference ranges
  - SQLite for optional logging (no patient data)
- **External Services:**
  - AI API endpoints
  - Medical terminology databases (public)

---

## 2. DATA FLOW

### 2.1 High-Level Data Flow (Context Diagram)

```
[Patient/User] 
    ↓ (Medical Report)
[AI Explanation System]
    ↓ (Patient-Friendly Explanation)
[Patient/User]
    
Data Stores:
- Medical Knowledge Base
- Reference Ranges Database
- Sample Reports

External APIs:
- OpenAI/Claude API
```

### 2.2 Detailed Process Flow (Level 2 DFD)

**Process Breakdown:**

1. **P1.1: Receive & Validate Input**
   - Accept file upload (PDF/TXT) or text paste
   - Validate format and file size
   - Check for prohibited content

2. **P1.2: Parse Medical Report**
   - Extract text from files
   - Identify report type (blood work, imaging, etc.)
   - Structure data for processing

3. **P1.3: Extract Key Information**
   - Identify test names and values
   - Extract medical terminology
   - Detect abnormal flags

4. **P1.4: Compare with Reference Ranges**
   - Query reference database
   - Flag out-of-range values
   - Determine severity indicators

5. **P1.5: Build AI Prompt**
   - Load appropriate template
   - Insert extracted information
   - Add context and constraints

6. **P1.6: Call AI Service**
   - Send request to AI API
   - Handle rate limiting
   - Manage errors and retries

7. **P1.7: Format Response**
   - Structure AI output
   - Add safety disclaimers
   - Apply styling

8. **P1.8: Display Result**
   - Render on web page
   - Provide download option
   - Log interaction (no PII)

---

## 3. IMPLEMENTATION APPROACH

### 3.1 Technology Stack

**Frontend:**
```
- HTML5
- CSS3 (Bootstrap 5)
- JavaScript (Vanilla JS or React for advanced version)
```

**Backend:**
```
- Python 3.10+
- Flask 2.3+
- Flask-CORS (for API access)
```

**AI Integration:**
```
- OpenAI Python SDK (openai>=1.0.0)
- Alternative: Anthropic SDK
```

**Data Management:**
```
- pandas (CSV handling)
- json (structured data)
- sqlite3 (optional logging)
```

**File Processing:**
```
- PyPDF2 or pdfplumber (PDF parsing)
- python-docx (Word documents)
```

### 3.2 Database Schema

**Since we're not storing patient data, we use file-based storage:**

**medical_terms.json:**
```json
{
  "CBC": {
    "full_name": "Complete Blood Count",
    "tests": {
      "WBC": "White Blood Cells",
      "RBC": "Red Blood Cells",
      "HGB": "Hemoglobin"
    }
  }
}
```

**reference_ranges.csv:**
```csv
test_name,unit,min_normal,max_normal,age_group,gender
WBC,10^9/L,4.0,11.0,adult,both
RBC,10^12/L,4.5,5.5,adult,male
```

### 3.3 AI Prompt Engineering Strategy

**Prompt Template Structure:**
```
SYSTEM: You are a medical communication assistant helping patients understand their medical reports. 

CONSTRAINTS:
- Do NOT provide diagnosis
- Do NOT recommend treatment
- Use simple language (8th-grade reading level)
- Always include "Consult your doctor" disclaimer

TASK: Explain the following medical report to a patient...

[REPORT DATA]

FORMAT:
1. Overview of the test
2. Explanation of each value
3. What normal/abnormal might indicate (general terms)
4. When to contact a doctor
```

---

## 4. SYSTEM COMPONENTS BREAKDOWN

### 4.1 Frontend Components

**index.html:**
- Header with logo and title
- Upload form
- Text input area
- Submit button
- Results display section
- Disclaimer footer

**style.css:**
- Responsive design
- Medical-themed color scheme (blues/greens)
- Clear typography
- Accessibility features

**script.js:**
- Form validation
- AJAX requests to backend
- Loading indicators
- Result rendering

### 4.2 Backend Components

**app.py (Main Flask Application):**
```python
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/explain', methods=['POST'])
def explain_report():
    # Process request
    pass

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})
```

**parser.py (Report Parser Module):**
```python
class ReportParser:
    def parse_blood_test(self, text):
        # Extract test names and values
        pass
    
    def parse_imaging_report(self, text):
        # Extract findings
        pass
```

**ai_service.py (AI Integration):**
```python
import openai

class AIExplainer:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)
    
    def generate_explanation(self, report_data):
        # Build prompt and call API
        pass
```

**validator.py (Input Validation):**
```python
class InputValidator:
    def validate_file(self, file):
        # Check file type, size, content
        pass
    
    def sanitize_input(self, text):
        # Remove potentially harmful content
        pass
```

---

## 5. SECURITY & PRIVACY CONSIDERATIONS

### 5.1 Data Protection
- **No storage of patient data:** All processing is done in memory
- **No PHI collection:** System doesn't ask for names, DOB, etc.
- **Secure communication:** HTTPS only (in production)
- **API key security:** Environment variables, never hardcoded

### 5.2 Safety Measures
- **Clear disclaimers:** "Not for diagnosis or treatment"
- **Encourage medical consultation:** Always direct to healthcare provider
- **Input validation:** Prevent malicious uploads
- **Rate limiting:** Prevent abuse

### 5.3 Ethical Guidelines
- **Transparency:** Clear about AI use
- **Accuracy:** Use reliable reference data
- **Accessibility:** Simple language
- **Inclusivity:** Consider diverse backgrounds

---

## 6. DEVELOPMENT ENVIRONMENT SETUP

### 6.1 Required Software

**Python Environment:**
```bash
Python 3.10+
pip (package manager)
virtualenv (optional but recommended)
```

**Code Editor:**
```
VS Code (recommended)
PyCharm
Sublime Text
```

**Version Control:**
```
Git
GitHub account
```

### 6.2 Installation Steps

**Step 1: Create Project Directory**
```bash
mkdir medical-report-explainer
cd medical-report-explainer
```

**Step 2: Set Up Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Step 3: Install Dependencies**
```bash
pip install flask flask-cors openai pandas PyPDF2
```

**Step 4: Create Project Structure**
```
medical-report-explainer/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── config.py             # Configuration settings
├── .env                  # Environment variables (API keys)
├── modules/
│   ├── parser.py         # Report parsing logic
│   ├── ai_service.py     # AI API integration
│   ├── validator.py      # Input validation
│   └── formatter.py      # Response formatting
├── data/
│   ├── medical_terms.json    # Medical terminology
│   ├── reference_ranges.csv  # Normal ranges
│   └── sample_reports/       # Test data
├── static/
│   ├── css/
│   │   └── style.css     # Stylesheets
│   ├── js/
│   │   └── script.js     # Frontend JavaScript
│   └── images/           # Logo, icons
└── templates/
    └── index.html        # Main web page
```

### 6.3 Environment Configuration

**Create .env file:**
```
OPENAI_API_KEY=your_api_key_here
FLASK_ENV=development
FLASK_APP=app.py
MAX_FILE_SIZE=5242880  # 5MB
ALLOWED_EXTENSIONS=pdf,txt,docx
```

---

## 7. SAMPLE DATA PREPARATION

### 7.1 Blood Test Report Samples

**Sample 1: Complete Blood Count (CBC)**
```
Patient: Sample
Date: 2026-02-01

Complete Blood Count (CBC)
---------------------------
White Blood Cells (WBC): 7.5 × 10^9/L [4.0-11.0]
Red Blood Cells (RBC): 4.8 × 10^12/L [4.5-5.5]
Hemoglobin (HGB): 14.5 g/dL [13.5-17.5]
Hematocrit (HCT): 42% [38-50]
Platelets (PLT): 250 × 10^9/L [150-400]
```

**Sample 2: Lipid Panel**
```
Lipid Panel
-----------
Total Cholesterol: 220 mg/dL [<200]
LDL Cholesterol: 145 mg/dL [<100]
HDL Cholesterol: 45 mg/dL [>40]
Triglycerides: 180 mg/dL [<150]
```

### 7.2 Imaging Report Samples

**Sample: Chest X-Ray**
```
CLINICAL INDICATION: Routine screening

FINDINGS:
The lungs are clear with no focal consolidation, pleural effusion, or pneumothorax. 
Heart size is normal. No acute osseous abnormality is detected.

IMPRESSION:
No acute cardiopulmonary process.
```

---

## 8. TESTING STRATEGY

### 8.1 Unit Testing
- Test each module independently
- Validate parser accuracy
- Check API integration

### 8.2 Integration Testing
- End-to-end flow testing
- Error handling verification
- Performance testing

### 8.3 User Acceptance Testing
- Test with sample reports
- Verify explanation clarity
- Check disclaimer visibility

---

## 9. SUCCESS METRICS

### 9.1 Technical Metrics
- Response time < 5 seconds
- Parser accuracy > 95%
- API success rate > 99%

### 9.2 User Experience Metrics
- Explanation readability (Flesch-Kincaid Grade 8)
- User satisfaction (survey)
- Clarity of disclaimers

### 9.3 Educational Metrics
- Terms explained
- Context provided
- Follow-up guidance

---

## 10. PROJECT TIMELINE

**Week 1:** Setup & Architecture (Current)
- Environment setup ✓
- Architecture design ✓
- Data collection

**Week 2:** Core Development
- Backend implementation
- Parser development
- AI integration

**Week 3:** Frontend Development
- UI design
- Form implementation
- Results display

**Week 4:** Testing & Refinement
- Unit tests
- Integration tests
- Bug fixes

**Week 5:** Documentation
- Code documentation
- User guide
- Technical report

**Week 6:** Final Presentation
- Demo preparation
- Presentation slides
- Video recording

---

## 11. RISK MANAGEMENT

### 11.1 Technical Risks
- **API Rate Limits:** Use caching, implement retry logic
- **Parsing Errors:** Fallback to manual input
- **AI Inaccuracy:** Implement validation checks

### 11.2 Academic Risks
- **Scope Creep:** Stick to explanation, not diagnosis
- **Time Constraints:** Prioritize core features
- **Resource Limitations:** Use free tier APIs

---

## 12. DELIVERABLES

### 12.1 Phase 1 Deliverables (Current)
✓ System Architecture Diagram
✓ Data Flow Diagrams (Level 1 & 2)
✓ Implementation Plan
✓ Development Environment Setup

### 12.2 Final Project Deliverables
□ Working prototype/demo
□ Source code with documentation
□ Technical report
□ Presentation slides
□ User guide
□ Test results and validation

---

## 13. REFERENCES

- Course lecture materials (Medical Diagnostic Engineering)
- OpenAI API Documentation
- Flask Web Framework Documentation
- Medical terminology standards (ICD-10, LOINC)
- Health literacy guidelines

---

## NEXT STEPS

1. **Set up development environment** (Instructions provided above)
2. **Gather and prepare sample medical reports**
3. **Create medical terms database**
4. **Begin backend development** (Phase 2)

---

**Document Version:** 1.0  
**Last Updated:** February 9, 2026  
**Authors:** Medical Diagnostic Engineering Team  
**Course:** Medical Diagnostic Engineering, University of Ottawa
