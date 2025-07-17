# LCF Civic Summaries - Lovable Integration Guide

## 🎯 **Architecture Overview**

**QNAP NAS (Backend API):**
- Runs tracker scripts and generates data
- Provides REST API endpoints
- Handles CORS for public access
- No frontend code to maintain

**Lovable (Frontend):**
- Modern React-based website
- Fetches data from QNAP API
- Easy drag-and-drop updates
- Professional hosting and design

## 🚀 **QNAP Setup (Backend)**

### **1. Install API Server**
```bash
cd "/share/Multimedia/Projects/LCF City Notes/lcf-tracker-github"
pip3 install -r requirements_api.txt
```

### **2. Start API Server**
```bash
# Test mode
python3 api_server.py

# Production mode (recommended)
nohup python3 start_api_server.py > api_server.log 2>&1 &
```

### **3. Verify API is Running**
```bash
curl http://YOUR_QNAP_IP:5000/api/health
```

### **4. Make API Publicly Accessible**
In your QNAP router/firewall settings:
- Open port 5000
- Forward port 5000 to your QNAP IP
- Note your public IP or set up dynamic DNS

## 📡 **API Endpoints**

Your QNAP will provide these endpoints:

### **Base URL:** `http://YOUR_PUBLIC_IP:5000`

### **Available Endpoints:**

#### **Health Check**
```
GET /api/health
```
Returns server status and timestamp.

#### **Current Summaries**
```
GET /api/current
```
Returns recent meeting summaries and agendas.

#### **Historical Archive**
```
GET /api/archive
```
Returns complete 2025 historical data.

#### **All Data**
```
GET /api/all
```
Returns both current and archive data in one call.

#### **Government Bodies**
```
GET /api/bodies
```
Returns list of all government bodies.

#### **Search**
```
GET /api/search?q=budget&body=City Council&type=agenda
```
Search across all documents with optional filters.

## 🎨 **Lovable Setup (Frontend)**

### **1. Create New Lovable Project**
Go to [Lovable.dev](https://lovable.dev) and create a new project.

### **2. Use These Prompts**

#### **Initial Setup Prompt:**
```
Create a modern, responsive website for "LCF Civic Summaries" - a La Cañada Flintridge government transparency platform. 

Features needed:
- Clean, professional design with blue/white color scheme
- Header with logo and title "LCF Civic Summaries"
- Two main sections: "Current Summaries" and "2025 Archive" with tab navigation
- Search functionality across all documents
- Filter by government body and document type
- Mobile-responsive design
- Cards layout for displaying meeting summaries

The site will fetch data from an external API at: http://YOUR_PUBLIC_IP:5000/api/current and /api/archive

Each document should display:
- Title
- Date
- Summary text
- "AI Summary" or "Auto Summary" badge
- Link to view full document
- Government body name

Include loading states and error handling for API calls.
```

#### **API Integration Prompt:**
```
Add API integration to fetch data from these endpoints:

Base URL: http://YOUR_PUBLIC_IP:5000

Endpoints:
- GET /api/current - Returns current meeting summaries
- GET /api/archive - Returns historical 2025 data
- GET /api/search?q=QUERY - Search functionality

Response format:
{
  "success": true,
  "data": {
    "City Council": {
      "agendas": [...],
      "minutes": [...]
    },
    "Planning Commission": {
      "agendas": [...],
      "minutes": [...]
    }
  },
  "stats": {
    "total_documents": 10,
    "total_bodies": 8,
    "ai_summaries": 8
  }
}

Each document has:
- id, title, date, summary, url, type, ai_generated, body

Add proper error handling and loading states.
```

#### **Styling Prompt:**
```
Improve the design with:
- Professional government website styling
- Blue gradient header background
- Clean white cards with subtle shadows
- Hover effects on cards
- Proper typography hierarchy
- Mobile-responsive grid layout
- Loading spinners
- Error states with retry buttons
- Badge styling for "AI Summary" vs "Auto Summary"
- Professional footer with links to official city website
```

### **3. Test Integration**
Once your Lovable site is built:
1. Replace `YOUR_PUBLIC_IP` with your actual QNAP public IP
2. Test the API endpoints work from your browser
3. Verify data loads correctly in Lovable

## 🔧 **Configuration**

### **API Server Configuration**
Edit `api_server.py` to customize:
- Port number (default: 5000)
- CORS settings
- Data file locations
- Mock data for testing

### **QNAP Network Setup**
1. **Find QNAP IP:** Check your router admin panel
2. **Port Forwarding:** Forward external port 5000 to QNAP:5000
3. **Dynamic DNS:** Set up DDNS for consistent URL
4. **Firewall:** Allow port 5000 in QNAP firewall

## 📊 **Data Flow**

```
1. QNAP Tracker Scripts → Generate JSON data files
2. QNAP API Server → Serves data via REST endpoints  
3. Lovable Website → Fetches data and displays beautifully
4. Users → Access professional website with latest data
```

## 🔄 **Ongoing Updates**

### **Content Updates (QNAP):**
Your existing workflow continues:
```bash
python3 test_workflow.py  # Generates new summaries
# API automatically serves updated data
```

### **Design Updates (Lovable):**
- Use natural language prompts to modify design
- No HTML/CSS debugging needed
- Changes deploy automatically

## 🎯 **Benefits of This Setup**

✅ **Separation of Concerns:** Data processing (QNAP) vs. Presentation (Lovable)
✅ **Easy Updates:** Modify design without touching backend code
✅ **Professional Hosting:** Lovable handles hosting, SSL, CDN
✅ **Mobile Responsive:** Automatic responsive design
✅ **No Maintenance:** No HTML/CSS bugs to fix
✅ **Scalable:** Easy to add features via Lovable prompts

## 🆘 **Troubleshooting**

### **API Not Accessible:**
- Check QNAP firewall settings
- Verify port forwarding in router
- Test local access first: `http://QNAP_LOCAL_IP:5000/api/health`

### **CORS Errors:**
- API server includes CORS headers
- If issues persist, check browser console for specific errors

### **No Data Loading:**
- Verify API endpoints return data
- Check Lovable console for JavaScript errors
- Ensure API URL is correct in Lovable code

## 🎉 **Result**

You'll have a professional government transparency website that:
- Updates automatically with your QNAP data
- Looks great on all devices
- Is easy to modify without coding
- Serves the La Cañada Flintridge community professionally

Your residents will have beautiful, searchable access to all government activities!

