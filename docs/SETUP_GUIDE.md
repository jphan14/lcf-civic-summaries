# LCF Civic Summaries - Complete Setup Guide

## 📋 **Prerequisites**

Before starting, ensure you have:
- ✅ QNAP NAS with Python 3 installed
- ✅ OpenAI API key (for AI summaries)
- ✅ Gmail account with App Password (for email notifications - optional)
- ✅ Downloaded the latest system package

## 🚀 **Step 1: Initial Installation**

### **1.1 Extract Files**
```bash
# Navigate to your project directory
cd "/share/Multimedia/Projects/LCF City Notes/"

# Extract the system files
unzip lcf_historical_archive_system.zip
cd lcf-tracker-github
```

### **1.2 Install Dependencies**
```bash
# Install required Python packages
pip3 install schedule requests beautifulsoup4 PyPDF2 openai
```

### **1.3 Configure Settings**
Edit `config.json` with your settings:
```json
{
  "schedule_day": "monday",
  "schedule_time": "08:00",
  "send_email": true,
  "email_from": "your_email@gmail.com",
  "email_to": "your_email@gmail.com",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "your_email@gmail.com",
  "smtp_password": "your_16_character_app_password_no_spaces",
  "smtp_use_tls": true,
  "openai_api_key": "your_openai_api_key_here",
  "openai_model": "gpt-4.1-mini"
}
```

## 🏛️ **Step 2: One-Time Historical Archive Setup**

### **2.1 Create Historical Archive Structure**
```bash
# Create the 2025 historical archive
python3 historical_archive_fetcher.py
```
**Expected Output:**
```
✅ Created historical archive with 111 documents across 8 government bodies
📁 Archive saved to: historical_archive_2025/
```

### **2.2 Process Real Documents (Recommended)**
```bash
# Create manual downloads directory
mkdir -p manual_downloads

# Download PDFs manually from https://lcf.ca.gov/city-clerk/agenda-minutes/
# Place them in the manual_downloads/ folder
# Then process them:
python3 manual_document_processor.py

# Add to historical archive:
python3 append_to_archive.py
```

### **2.3 Generate Historical Summaries (Optional)**
```bash
# This processes all historical documents with AI (takes time)
python3 historical_summarizer.py
```
**Note:** This can take 30+ minutes for all documents. You can skip this initially and add real documents instead.

## 🧪 **Step 3: Test the Complete System**

### **3.1 Test Core Functionality**
```bash
# Test the main workflow
python3 test_workflow.py
```
**Expected Output:**
```
✅ Dependencies: PASS
✅ Configuration: PASS
✅ Document Fetch: PASS
✅ Summarization: PASS
✅ Email Reporting: PASS
✅ Overall Result: PASS
```

### **3.2 Test Website Integration**
```bash
# Test website data generation
python3 update_website_standalone.py
```
**Expected Output:**
```
✅ Website data updated successfully
📊 Loaded summaries for 8 government bodies
📁 Website data saved to: website_data.json
```

### **3.3 Test Historical Archive Integration**
```bash
# Test archive append functionality
python3 append_to_archive.py
```
**Expected Output:**
```
✅ Archive append process completed successfully!
📈 Summary: X new documents added to archive
```

### **3.4 Test Email Configuration (Optional)**
```bash
# Test email settings
python3 test_email_config.py
```
**Expected Output:**
```
✅ Email configuration is valid
✅ SMTP connection successful
✅ Test email sent successfully
```

## 📅 **Step 4: Set Up Automated Scheduler**

### **4.1 Test Scheduler**
```bash
# Test the scheduler (runs once then exits)
python3 scheduler.py --test
```

### **4.2 Start Scheduler Service**

**Option A: Run in Background**
```bash
# Start scheduler in background
nohup python3 scheduler.py > scheduler.log 2>&1 &

# Check if it's running
ps aux | grep scheduler.py
```

**Option B: Create System Service (Advanced)**
```bash
# Create service file
sudo nano /etc/systemd/system/lcf-tracker.service

# Add this content:
[Unit]
Description=LCF Government Tracker
After=network.target

[Service]
Type=simple
User=admin
WorkingDirectory=/share/Multimedia/Projects/LCF City Notes/lcf-tracker-github
ExecStart=/usr/bin/python3 scheduler.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start service
sudo systemctl enable lcf-tracker.service
sudo systemctl start lcf-tracker.service
sudo systemctl status lcf-tracker.service
```

## 🌐 **Step 5: Website Deployment and Updates**

### **5.1 Verify Website Data**
```bash
# Check that website data files exist
ls -la website_data.json
ls -la combined_website_data.json
ls -la historical_summaries_2025/
```

### **5.2 Test Website Update Process**
```bash
# Run complete workflow with website update
python3 test_workflow.py

# Verify website was updated
python3 update_website_standalone.py

# Check for generated reports
ls -la lcf_civic_report_*.html
```

### **5.3 Monitor Website Integration**
The website automatically updates when your scheduler runs. Check these files after each run:
- `website_data.json` - Current summaries for website
- `combined_website_data.json` - Combined current + historical data
- `historical_summaries_2025/` - Historical archive data

## 🔄 **Step 6: Ongoing Weekly Workflow**

### **6.1 Automated Process**
Once the scheduler is running, it automatically:
1. ✅ Fetches new meeting documents
2. ✅ Generates AI summaries
3. ✅ Updates the website data
4. ✅ Appends to historical archive
5. ✅ Sends email reports (if configured)

### **6.2 Manual Document Addition (As Needed)**
```bash
# When you download new PDFs manually:
# 1. Place PDFs in manual_downloads/
# 2. Process them:
python3 manual_document_processor.py

# 3. Add to archive:
python3 append_to_archive.py

# 4. Update website:
python3 update_website_standalone.py
```

## 🔍 **Step 7: Monitoring and Maintenance**

### **7.1 Check Scheduler Status**
```bash
# View scheduler logs
tail -f scheduler.log

# Check if scheduler is running
ps aux | grep scheduler.py
```

### **7.2 Check System Health**
```bash
# Run health check
python3 test_workflow.py

# Check recent reports
ls -la lcf_civic_report_*.html | tail -5

# Check archive statistics
cat historical_summaries_2025/archive_stats.json
```

### **7.3 View Generated Reports**
```bash
# Open latest HTML report in browser
# Or check the text version:
cat lcf_civic_report_*.txt | tail -50
```

## 📊 **Step 8: Verification Checklist**

After setup, verify these components are working:

### **Core System:**
- [ ] `test_workflow.py` passes all tests
- [ ] `document_summaries.json` is generated
- [ ] AI summaries are being created
- [ ] Email reports are generated (HTML and text)

### **Historical Archive:**
- [ ] `historical_archive_2025/` directory exists
- [ ] `historical_summaries_2025/` directory exists
- [ ] `append_to_archive.py` runs without errors
- [ ] Archive statistics are updated

### **Website Integration:**
- [ ] `website_data.json` is generated
- [ ] `combined_website_data.json` includes historical data
- [ ] `update_website_standalone.py` runs successfully

### **Scheduler:**
- [ ] Scheduler process is running
- [ ] Scheduled time is correct in config
- [ ] Logs show successful runs

### **Email (Optional):**
- [ ] `test_email_config.py` passes
- [ ] Test emails are received
- [ ] SMTP settings are correct

## 🚨 **Troubleshooting Common Issues**

### **OpenAI API Errors:**
```bash
# Check API key in config.json
# Ensure model is "gpt-4.1-mini"
# Check quota at https://platform.openai.com/account/usage
```

### **Email Errors:**
```bash
# Verify App Password has no spaces
# Check Gmail 2FA is enabled
# Test with test_email_config.py
```

### **Scheduler Not Running:**
```bash
# Check process: ps aux | grep scheduler
# Check logs: tail -f scheduler.log
# Restart: python3 scheduler.py &
```

### **Website Not Updating:**
```bash
# Run manually: python3 update_website_standalone.py
# Check file permissions
# Verify JSON files are generated
```

## 🎯 **Success Indicators**

Your system is working correctly when:
1. ✅ **Weekly reports** are generated automatically
2. ✅ **Historical archive** grows with new meetings
3. ✅ **Website data** is updated regularly
4. ✅ **Email notifications** are received (if enabled)
5. ✅ **No error messages** in logs
6. ✅ **All test scripts** pass

## 📞 **Support**

If you encounter issues:
1. Check the relevant log files
2. Run the test scripts to identify problems
3. Verify configuration settings
4. Check file permissions and paths

Your LCF Civic Summaries system is now ready to provide comprehensive government transparency for La Cañada Flintridge! 🏛️✨

