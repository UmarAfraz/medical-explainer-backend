# QUICK START GUIDE
## Medical Report Explanation System - Backend Setup

**Time Required:** 15-20 minutes  
**For:** Mac M4 MacBook Pro

---

## ⚡ Super Quick Setup (For the Impatient!)

```bash
# 1. Get OpenAI API key from https://platform.openai.com/api-keys

# 2. Navigate to project folder
cd /path/to/medical-report-explainer

# 3. Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Configure API key
cp .env.example .env
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# 5. Run server
python app.py

# 6. Test in another terminal
curl http://localhost:5000/api/health
```

---

## 📋 Step-by-Step (Recommended)

### Step 1: Get OpenAI API Key (5 min)

1. Visit: https://platform.openai.com/api-keys
2. Sign up or login
3. Click **"Create new secret key"**
4. **Copy the key** (starts with `sk-...`)
5. Add **$5-10** to your account for testing

💡 **Save the key** - you can't see it again!

---

### Step 2: Prepare Project Files (2 min)

```bash
# Create project directory
mkdir ~/medical-report-explainer
cd ~/medical-report-explainer

# Copy all provided files here:
# - app.py
# - config.py
# - requirements.txt
# - .env.example
# - modules/ folder
# - data/ folder
```

---

### Step 3: Setup Virtual Environment (3 min)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it (you'll see (venv) in terminal)
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

**Expected output:** Packages installing successfully

---

### Step 4: Configure Environment (2 min)

```bash
# Copy environment template
cp .env.example .env

# Edit .env file (use nano, vim, or VS Code)
nano .env
```

**In .env, set:**
```
OPENAI_API_KEY=sk-your-actual-api-key-here
FLASK_ENV=development
```

**Save and exit** (Ctrl+X, then Y, then Enter in nano)

---

### Step 5: Verify Setup (1 min)

```bash
# Check if data files exist
ls data/

# You should see:
# medical_terms.json
# reference_ranges.csv

# Create temp upload folder
mkdir -p temp_uploads
```

---

### Step 6: Start the Server (1 min)

```bash
# Make sure venv is activated
source venv/bin/activate

# Run the server
python app.py
```

**Success looks like:**
```
INFO - Application initialized successfully
INFO - Starting server on 0.0.0.0:5000
* Running on http://0.0.0.0:5000
```

---

### Step 7: Test the API (3 min)

**Open a NEW terminal** (keep server running in first terminal)

**Test 1: Health Check**
```bash
curl http://localhost:5000/api/health
```

**Expected:** `{"status": "healthy", ...}`

**Test 2: Simple Blood Test**
```bash
curl -X POST http://localhost:5000/api/explain \
  -H "Content-Type: application/json" \
  -d '{
    "report_text": "WBC: 7.5 × 10^9/L [4.0-11.0]",
    "report_type": "blood_test"
  }'
```

**Expected:** JSON with AI-generated explanation

**Test 3: Using Sample File**
```bash
# If you have a sample report file
curl -X POST http://localhost:5000/api/upload \
  -F "file=@path/to/sample_report.txt"
```

---

## ✅ Verification Checklist

- [ ] Python 3.10+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (no errors)
- [ ] `.env` file created with API key
- [ ] Data files present in `data/` folder
- [ ] Server starts without errors
- [ ] Health check returns "healthy"
- [ ] Test explanation request works

---

## 🎯 Using VS Code

If you're using VS Code:

1. **Open project:**
   ```bash
   code ~/medical-report-explainer
   ```

2. **Select Python interpreter:**
   - Press `Cmd+Shift+P`
   - Type "Python: Select Interpreter"
   - Choose the one in `venv/bin/python`

3. **Run server:**
   - Open `app.py`
   - Press `F5` or click "Run" button
   - Or use integrated terminal: `python app.py`

---

## 🔥 Common Issues & Quick Fixes

### "Command not found: python3"
**Fix:** Use `python` instead of `python3`

### "No module named 'flask'"
**Fix:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "OPENAI_API_KEY is required"
**Fix:** Check `.env` file has `OPENAI_API_KEY=sk-...` (no spaces!)

### "Address already in use"
**Fix:**
```bash
# Kill process on port 5000
lsof -i :5000
kill -9 <PID>
```

### "Insufficient credits"
**Fix:** Add funds to OpenAI account at https://platform.openai.com/account/billing

---

## 📊 Testing with Real Data

Use the sample reports in `data/` folder:

**Sample Blood Test:**
```bash
curl -X POST http://localhost:5000/api/explain \
  -H "Content-Type: application/json" \
  -d @sample_blood_request.json
```

**Sample Imaging Report:**
```bash
curl -X POST http://localhost:5000/api/explain \
  -H "Content-Type: application/json" \
  -d @sample_imaging_request.json
```

---

## 🎓 Next Steps

After backend is running:

1. **Phase 3:** Build frontend web interface
2. **Integration:** Connect frontend to this backend
3. **Testing:** Test with various report types
4. **Documentation:** Document your findings
5. **Presentation:** Prepare demo for professor

---

## 💡 Pro Tips

1. **Keep terminal open:** Don't close the server terminal
2. **Check logs:** Look at `app.log` for debugging
3. **Use Postman:** Better for testing than curl
4. **Save API calls:** Each call costs ~$0.01-0.03
5. **Test locally first:** Before deploying

---

## 🆘 Still Stuck?

1. Check `README.md` for detailed documentation
2. Review error messages in terminal
3. Check `app.log` file
4. Verify all files are in correct locations
5. Ensure OpenAI account has credits

---

## 📞 Quick Commands Reference

```bash
# Activate virtual environment
source venv/bin/activate

# Deactivate virtual environment
deactivate

# Run server
python app.py

# Test health
curl http://localhost:5000/api/health

# View logs
tail -f app.log

# Stop server
Ctrl + C
```

---

**You're all set! 🚀**

Server running on http://localhost:5000

Test endpoint: http://localhost:5000/api/test
