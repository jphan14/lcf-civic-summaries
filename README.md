# LCF Civic Summaries

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template-id)

An automated system for tracking and summarizing La Cañada Flintridge government meetings, providing AI-generated summaries and maintaining a searchable archive of civic activities.

## 🌟 Features

- **Automated Document Fetching**: Retrieves meeting agendas and minutes from city websites
- **AI-Powered Summarization**: Generates detailed, readable summaries using OpenAI GPT models
- **Historical Archive**: Maintains a comprehensive archive of all 2025 government activities
- **Public API**: RESTful API for accessing meeting data and summaries
- **Email Notifications**: Weekly consolidated email reports
- **Web Integration**: Designed for seamless integration with external website builders
- **Multi-Government Body Support**: Tracks 8+ government bodies including City Council and commissions

## 🏛️ Government Bodies Tracked

- City Council
- Planning Commission
- Public Safety Commission
- Parks & Recreation Commission
- Design Review Board
- Environmental Commission
- Traffic & Safety Commission
- Investment & Financing Advisory Committee

## 🚀 Quick Deploy to Railway

1. Click the "Deploy on Railway" button above
2. Connect your GitHub account
3. Configure environment variables (see below)
4. Deploy!

## 🔧 Environment Variables

Copy `.env.example` to `.env` and configure the following variables:

### Required Variables

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Email Configuration (for reports)
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=your_email@gmail.com
```

### Optional Variables

```env
# Application Settings
ENVIRONMENT=production
DEBUG=false
USE_AI_SUMMARIES=true
MAX_API_CALLS_PER_RUN=20

# Scheduling
SCHEDULE_TIME=09:00
SCHEDULE_DAY=monday
TIMEZONE=America/Los_Angeles

# Email Settings
SEND_EMAIL=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

## 📡 API Endpoints

### Health Check
```
GET /api/health
```
Returns basic health status

### Current Summaries
```
GET /api/summaries
```
Returns latest meeting summaries

### Historical Archive
```
GET /api/archive
```
Returns historical meeting data organized by month

### Search
```
GET /api/search?q=budget&body=City Council
```
Search through summaries and archive

### Government Bodies
```
GET /api/government-bodies
```
Returns list of tracked government bodies

## 🏗️ Architecture

### Services

**Web Service**: Runs the API server (`api_server.py`)
- Serves API endpoints for external applications
- Handles CORS for web integration
- Provides health monitoring

**Worker Service**: Runs the scheduler (`scheduler.py`)
- Executes weekly document processing
- Manages AI summarization
- Sends email reports
- Updates website data

### Data Flow

1. **Fetch**: Retrieve documents from city websites or manual uploads
2. **Summarize**: Generate AI summaries with fallback options
3. **Archive**: Update historical archive with new data
4. **Publish**: Update API data and send email reports

## 🔄 Scheduled Processing

The system runs weekly processing jobs that:

1. Fetch new meeting documents
2. Generate AI summaries
3. Update the historical archive
4. Refresh API data
5. Send email reports

Configure the schedule using environment variables:
- `SCHEDULE_DAY`: Day of week (monday, tuesday, etc.)
- `SCHEDULE_TIME`: Time in HH:MM format (24-hour)
- `TIMEZONE`: Timezone for scheduling

## 🌐 Web Integration

This API is designed to integrate with external website builders like:

- **Lovable**: Modern React applications
- **Webflow**: Professional websites
- **Bubble**: No-code applications

### Integration Example

```javascript
// Fetch current summaries
const response = await fetch('https://your-railway-url/api/summaries');
const data = await response.json();

// Display summaries in your website
data.summaries.forEach(summary => {
    console.log(summary.government_body, summary.title, summary.summary);
});
```

## 📧 Email Reports

Weekly email reports include:
- Summary of new meetings and decisions
- Links to full documents
- Archive updates
- System status

Configure email settings in environment variables to enable reports.

## 🛠️ Development

### Local Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and configure
4. Run the API server: `python src/api_server.py`
5. Run the scheduler: `python src/scheduler.py`

### Testing

```bash
# Test the complete workflow
python src/scheduler.py --test --run

# Test individual components
python src/fetch_all_meetings.py
python src/summarize_all_meetings.py
```

## 📊 Monitoring

Railway provides built-in monitoring for:
- Service uptime and health
- API response times
- Resource usage
- Error logs

Access logs and metrics through the Railway dashboard.

## 🔒 Security

- Environment variables for sensitive data
- HTTPS endpoints by default
- CORS configuration for web integration
- Rate limiting for API protection

## 💰 Cost Optimization

- Configurable API call limits
- Intelligent caching
- Efficient scheduling
- Resource monitoring

Typical monthly costs:
- Railway hosting: $5-15
- OpenAI API: $2-10
- Total: $7-25/month

## 🤝 Contributing

This project serves the La Cañada Flintridge community and the broader civic technology ecosystem. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: See the `docs/` directory
- **Issues**: Report bugs and feature requests on GitHub
- **Community**: Join discussions about civic technology

## 🎯 Impact

This project promotes government transparency by:
- Making meeting information more accessible
- Providing searchable summaries of government activities
- Enabling community engagement with local government
- Supporting informed civic participation

---

**Built with ❤️ for the La Cañada Flintridge community**

