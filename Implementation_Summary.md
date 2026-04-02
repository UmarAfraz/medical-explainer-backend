# AI Medical Report Explanation System
## Implementation Summary for Professor Review

**Project:** Generative AI-Powered Medical Imaging and Blood Work Explanation Agents  
**Course:** Medical Diagnostic Engineering - Winter 2026  
**University:** University of Ottawa

---

## SYSTEM ARCHITECTURE OVERVIEW

### **Implementation Type: Web-Based Application**

**Architecture: 3-Tier Client-Server Model**

```
┌─────────────────────────────────────────────┐
│   TIER 1: PRESENTATION LAYER (Frontend)     │
│   - HTML/CSS/JavaScript                     │
│   - User uploads reports                    │
│   - Displays patient-friendly explanations  │
└─────────────────────────────────────────────┘
                    ↓ HTTP Request
┌─────────────────────────────────────────────┐
│   TIER 2: APPLICATION LAYER (Backend)       │
│   - Python Flask Web Server                 │
│   - Report Parser (extracts data)           │
│   - Input Validator (security)              │
│   - Response Formatter                      │
└─────────────────────────────────────────────┘
                    ↓ API Call
┌─────────────────────────────────────────────┐
│   TIER 3: AI & DATA LAYER                   │
│   - OpenAI GPT-4 API / Anthropic Claude     │
│   - Medical Terms Database (JSON)           │
│   - Reference Ranges (CSV)                  │
│   - No patient data storage                 │
└─────────────────────────────────────────────┘
```

---

## KEY COMPONENTS

### **1. Frontend (User Interface)**
- **Technology:** HTML5, CSS3, Bootstrap, JavaScript
- **Features:**
  - File upload (PDF, TXT, DOCX)
  - Text paste option
  - Loading indicators
  - Results display with formatting
  - Prominent safety disclaimers

### **2. Backend (Processing Engine)**
- **Technology:** Python 3.10+, Flask Framework
- **Modules:**
  - **app.py:** Main application and API routes
  - **parser.py:** Extracts test names, values, flags from reports
  - **ai_service.py:** Manages AI API calls
  - **validator.py:** Input validation and security
  - **formatter.py:** Structures output

### **3. AI Integration**
- **Primary:** OpenAI GPT-4 API
- **Alternative:** Anthropic Claude API
- **Method:** Prompt engineering with medical context
- **Safety:** System prompts prevent diagnosis/treatment advice

### **4. Data Storage**
- **Medical Terms:** JSON file with terminology explanations
- **Reference Ranges:** CSV with normal values by age/gender
- **NO PATIENT DATA:** Everything processes in memory only

---

## DATA FLOW (HOW IT WORKS)

**Step-by-Step Process:**

1. **User Action:** Patient uploads medical report or pastes text
   
2. **Validation:** System checks file type, size, and content safety
   
3. **Parsing:** Extract test names, values, and abnormal flags
   ```
   Example: "WBC: 7.8 × 10^9/L [4.0-11.0]" 
   → Extracts: Test=WBC, Value=7.8, Unit=10^9/L, Range=4.0-11.0
   ```

4. **Reference Lookup:** Compare values against normal ranges database
   
5. **AI Prompt Construction:**
   ```
   System: You are a medical communication assistant...
   Constraints: No diagnosis, no treatment, 8th-grade language
   Task: Explain this report to a patient
   Data: [Parsed report with context]
   ```

6. **AI Processing:** Send to GPT-4, receive explanation
   
7. **Formatting:** Add disclaimers, structure output
   
8. **Display:** Show patient-friendly explanation to user

---

## SECURITY & ETHICS

### **Privacy Protection:**
✓ No patient data stored anywhere  
✓ All processing in RAM only  
✓ No names, dates of birth, or identifiers collected  
✓ HIPAA-aligned design (though not HIPAA-compliant without full infrastructure)

### **Safety Measures:**
✓ Clear disclaimers: "Not for diagnosis or treatment"  
✓ Always directs to healthcare provider  
✓ Input validation prevents malicious files  
✓ Rate limiting prevents abuse

### **Ethical Design:**
✓ Transparent about AI use  
✓ Simple language (8th-grade reading level)  
✓ Accessible design  
✓ Educational purpose only

---

## TECHNICAL SPECIFICATIONS

### **System Requirements:**
- Python 3.10 or higher
- Flask web framework
- OpenAI API key (or Anthropic)
- 2GB RAM minimum
- Modern web browser

### **Dependencies:**
```
flask==2.3.0
flask-cors==4.0.0
openai>=1.0.0
pandas==2.0.0
PyPDF2==3.0.0
python-docx==0.8.11
```

### **File Structure:**
```
medical-report-explainer/
├── app.py                    # Main Flask application
├── modules/
│   ├── parser.py            # Report parsing
│   ├── ai_service.py        # AI integration
│   ├── validator.py         # Security
│   └── formatter.py         # Output formatting
├── data/
│   ├── medical_terms.json   # Terminology database
│   └── reference_ranges.csv # Normal values
├── static/
│   ├── css/style.css        # Styling
│   └── js/script.js         # Frontend logic
└── templates/
    └── index.html           # Web interface
```

---

## SAMPLE INPUT/OUTPUT

### **Input Example:**
```
Complete Blood Count (CBC)
White Blood Cells (WBC): 7.5 × 10^9/L [4.0-11.0]
Hemoglobin (HGB): 14.5 g/dL [13.5-17.5]
```

### **AI-Generated Output Example:**
```
Your Complete Blood Count (CBC) Test Results:

1. White Blood Cells (WBC): 7.5
   • What it is: These are cells that help fight infections
   • Your result: Normal (within healthy range of 4.0-11.0)
   • What this means: Your body's infection-fighting system is working well

2. Hemoglobin (HGB): 14.5
   • What it is: Protein that carries oxygen in your blood
   • Your result: Normal (within healthy range of 13.5-17.5)
   • What this means: Your blood is carrying oxygen properly

Overall: All your blood count values are within normal ranges.

⚠️ IMPORTANT: This explanation is for educational purposes only. 
Always discuss your results with your healthcare provider.
```

---

## ADVANTAGES OF THIS APPROACH

### **1. Web-Based (No Installation Required)**
- Access from any device with browser
- Easy to share and demonstrate
- Platform independent

### **2. AI-Powered (Flexible & Intelligent)**
- Handles various report formats
- Adapts language to context
- Can explain complex terminology

### **3. Modular Design (Easy to Maintain)**
- Components can be updated independently
- Easy to add new test types
- Scalable architecture

### **4. Privacy-Focused (No Data Storage)**
- Processes and discards immediately
- No database to secure
- Minimal privacy risk

### **5. Educational Value (Aligns with Course)**
- Demonstrates AI in healthcare
- Shows system design principles
- Applies engineering to real problem

---

## LIMITATIONS & SCOPE

**What the System DOES:**
✓ Explains medical terminology  
✓ Compares values to normal ranges  
✓ Provides educational context  
✓ Uses simple language

**What the System DOES NOT DO:**
✗ Diagnose conditions  
✗ Recommend treatments  
✗ Replace doctor consultations  
✗ Store patient information  
✗ Handle real PHI (Protected Health Information)

---

## VALIDATION & TESTING

### **Testing Approach:**
1. **Unit Tests:** Individual component testing
2. **Integration Tests:** Full workflow testing
3. **User Testing:** Sample report trials
4. **Security Testing:** Input validation checks

### **Success Metrics:**
- Response time < 5 seconds
- Explanation readability (Flesch-Kincaid Grade 8)
- Parser accuracy > 95%
- Disclaimer visibility: 100%

---

## COMPARISON TO ALTERNATIVES

### **Why NOT just use ChatGPT directly?**
- Need structured parsing
- Must enforce safety constraints
- Want consistent format
- Require medical knowledge base integration

### **Why NOT a mobile app?**
- Web version works on all devices
- Easier to develop in timeframe
- No app store approval needed
- Simpler for academic project

### **Why NOT store data?**
- Privacy concerns
- Not needed for functionality
- Simpler architecture
- Reduces legal/ethical issues

---

## PROJECT TIMELINE (6 Weeks)

**Week 1:** Architecture & Setup (CURRENT - COMPLETE ✓)  
**Week 2:** Backend Development  
**Week 3:** Frontend Development  
**Week 4:** AI Integration & Testing  
**Week 5:** Refinement & Documentation  
**Week 6:** Final Demo & Presentation

---

## DELIVERABLES

### **Phase 1 (Current):**
✓ System Architecture Diagram  
✓ Data Flow Diagrams (Level 1 & 2)  
✓ Implementation Plan  
✓ Sample Data Files  
✓ Technical Documentation

### **Final Project:**
□ Working prototype/demo  
□ Complete source code  
□ User guide  
□ Technical report  
□ Presentation slides  
□ Video demonstration

---

## REFERENCES

1. OpenAI API Documentation - https://platform.openai.com/docs
2. Flask Framework - https://flask.palletsprojects.com/
3. Health Literacy Guidelines - CDC, NIH
4. Medical Terminology Standards - ICD-10, LOINC
5. Course Materials - Medical Diagnostic Engineering

---

## CONTACT & SUPPORT

**For questions or clarification:**
- Review the detailed Phase1_Documentation.md
- Check sample files for examples
- Refer to architecture diagrams for structure

**Next Steps:**
1. Review architecture and data flow diagrams
2. Examine sample medical reports
3. Study medical terms database structure
4. Prepare for Phase 2: Backend implementation

---

**Document Version:** 1.0  
**Date:** February 9, 2026  
**Status:** Phase 1 Complete - Ready for Professor Review
