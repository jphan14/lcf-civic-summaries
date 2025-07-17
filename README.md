# LCF Civic Summaries

A comprehensive government transparency platform for La Cañada Flintridge, providing automated meeting summaries and historical archives of all city government activities.

## 🏛️ **Overview**

This system automatically tracks, summarizes, and publishes meeting minutes and agendas from all La Cañada Flintridge government bodies, making local government more accessible to residents.

### **Government Bodies Tracked:**
- City Council
- Planning Commission  
- Design Commission
- Public Safety Commission
- Public Works and Traffic Commission
- Investment & Financing Advisory Committee
- Sustainability and Resilience Commission
- Parks and Recreation Commission

## 🎯 **Features**

- **🤖 AI-Powered Summaries**: Detailed, readable summaries of all meetings
- **📚 Historical Archive**: Complete 2025 government record
- **🔍 Search & Filter**: Find any topic across all meetings
- **📱 Mobile-Responsive**: Works on all devices
- **🔗 Document Links**: Direct access to official PDFs
- **⚡ Automated Updates**: Weekly processing with minimal manual intervention
- **🌐 Public API**: Clean REST endpoints for external integrations

## 🏗️ **Architecture**

### **Backend (QNAP NAS)**
- Document fetching and processing
- AI summarization using OpenAI
- REST API server with CORS support
- Automated scheduling and email reports

### **Frontend Options**
- **Option 1**: Built-in Flask website (included)
- **Option 2**: External website builder (Lovable, Webflow, etc.) via API
- **Option 3**: Custom React/Vue.js application

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+
- OpenAI API key
- QNAP NAS or Linux server
- Email account (Gmail recommended)

### **Installation**
```bash
git clone https://github.com/YOUR_USERNAME/lcf-civic-summaries.git
cd lcf-civic-summaries
pip install -r requirements.txt
```

### **Configuration**
1. Copy `config.example.json` to `config.json`
2. Add your OpenAI API key and email settings
3. Configure government body URLs and schedules

### **Run Tests**
```bash
python test_workflow.py
```

### **Start API Server**
```bash
python start_api_server.py
```

### **Schedule Automation**
```bash
nohup python scheduler.py > scheduler.log 2>&1 &
```

## 📡 **API Endpoints**

Base URL: `http://your-server:5000`

- `GET /api/health` - Health check
- `GET /api/current` - Recent meeting summaries  
- `GET /api/archive` - Historical 2025 data
- `GET /api/all` - Combined current and archive data
- `GET /api/bodies` - List of government bodies
- `GET /api/search?q=query` - Search across all documents

## 📁 **Project Structure**

```
lcf-civic-summaries/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── config.example.json               # Configuration template
├── 
├── core/                             # Core system files
│   ├── fetch_all_meetings.py        # Document fetching
│   ├── summarize_all_meetings.py    # AI summarization
│   ├── send_consolidated_email.py   # Email reporting
│   ├── scheduler.py                 # Automated scheduling
│   └── test_workflow.py             # System testing
├── 
├── api/                             # API server
│   ├── api_server.py               # Main API server
│   ├── start_api_server.py         # Production startup
│   └── requirements_api.txt        # API dependencies
├── 
├── website/                        # Built-in website (optional)
│   ├── static/                    # HTML/CSS/JS files
│   └── templates/                 # Flask templates
├── 
├── utils/                         # Utility scripts
│   ├── manual_document_processor.py  # Manual PDF processing
│   ├── historical_archive_fetcher.py # Historical data creation
│   ├── update_website_standalone.py  # Website updates
│   └── test_email_config.py         # Email testing
├── 
├── docs/                          # Documentation
│   ├── SETUP_GUIDE.md            # Detailed setup instructions
│   ├── LOVABLE_INTEGRATION.md    # External website integration
│   ├── API_DOCUMENTATION.md      # API reference
│   └── TROUBLESHOOTING.md        # Common issues and solutions
├── 
└── data/                          # Data storage (created at runtime)
    ├── meeting_documents/         # Downloaded PDFs
    ├── historical_summaries_2025/ # Archive data
    └── logs/                      # System logs
```

## 🔧 **Configuration Options**

### **Basic Settings**
- OpenAI API key and model selection
- Email SMTP configuration
- Schedule timing (weekly, daily, etc.)
- Government body URLs and selectors

### **Advanced Settings**
- AI prompt customization
- Rate limiting and retry logic
- Logging levels and retention
- CORS and security settings

## 🌐 **Deployment Options**

### **Option 1: QNAP NAS (Recommended)**
- Install directly on QNAP using Container Station or native Python
- Automatic startup and monitoring
- Local network access with port forwarding for public API

### **Option 2: Cloud Server**
- Deploy to AWS, DigitalOcean, or similar
- Use systemd for service management
- Configure reverse proxy (nginx) for production

### **Option 3: Docker**
```bash
docker build -t lcf-civic-summaries .
docker run -d -p 5000:5000 lcf-civic-summaries
```

## 🎨 **Frontend Integration**

### **Built-in Website**
The system includes a complete Flask-based website ready to use.

### **External Website Builders**
Integrate with modern website builders:
- **Lovable**: AI-powered React websites
- **Webflow**: Professional design tools
- **Bubble**: No-code applications
- **Custom**: React, Vue.js, or any framework

See `docs/LOVABLE_INTEGRATION.md` for detailed integration guide.

## 📊 **Data Flow**

```
1. Scheduled Job Runs
   ↓
2. Fetch Meeting Documents (PDFs)
   ↓
3. Extract Text Content
   ↓
4. Generate AI Summaries
   ↓
5. Update Historical Archive
   ↓
6. Refresh Website Data
   ↓
7. Send Email Report (Optional)
   ↓
8. API Serves Updated Data
```

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

- **Documentation**: See `docs/` directory
- **Issues**: Open a GitHub issue
- **Email**: Contact the maintainer

## 🙏 **Acknowledgments**

- La Cañada Flintridge City Government for providing public access to meeting documents
- OpenAI for AI summarization capabilities
- The open-source community for the tools and libraries used

## 📈 **Roadmap**

- [ ] Multi-language support
- [ ] Advanced search with filters
- [ ] Email subscription management
- [ ] Mobile app development
- [ ] Integration with other government transparency tools
- [ ] Analytics and usage tracking

---

**Made with ❤️ for government transparency and civic engagement**

