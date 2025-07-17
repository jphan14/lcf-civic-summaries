# Railway Deployment Guide

This guide covers deploying the LCF Civic Summaries system to Railway.app.

## Quick Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

## Manual Deployment

### 1. Prerequisites

- GitHub account
- Railway account (sign up at [railway.app](https://railway.app))
- OpenAI API key
- Gmail account with App Password (for email reports)

### 2. Repository Setup

1. Fork or clone this repository to your GitHub account
2. Ensure all files are present:
   - `Procfile` - Defines web and worker processes
   - `requirements.txt` - Python dependencies
   - `railway.json` - Railway configuration
   - `.env.example` - Environment variables template

### 3. Railway Project Creation

1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `lcf-civic-summaries` repository
5. Railway will automatically detect the Python application

### 4. Environment Variables

In your Railway project dashboard, go to the "Variables" tab and add:

#### Required Variables

```
OPENAI_API_KEY=your_openai_api_key_here
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=your_email@gmail.com
```

#### Optional Variables

```
ENVIRONMENT=production
DEBUG=false
USE_AI_SUMMARIES=true
MAX_API_CALLS_PER_RUN=20
SCHEDULE_TIME=09:00
SCHEDULE_DAY=monday
TIMEZONE=America/Los_Angeles
SEND_EMAIL=true
```

### 5. Service Configuration

Railway automatically creates two services based on your `Procfile`:

- **Web Service**: Runs the API server
- **Worker Service**: Runs the scheduler

Both services share the same environment variables and data storage.

### 6. Domain Configuration

Railway automatically assigns a domain like:
`https://lcf-civic-summaries-production.up.railway.app`

You can also configure a custom domain in the Railway dashboard.

### 7. Testing Deployment

After deployment, test your API endpoints:

```bash
# Health check
curl https://your-railway-url/api/health

# Current summaries
curl https://your-railway-url/api/summaries

# Historical archive
curl https://your-railway-url/api/archive
```

### 8. Monitoring

Railway provides built-in monitoring:

- **Logs**: Real-time application logs
- **Metrics**: CPU, memory, and network usage
- **Uptime**: Service availability tracking

Access these through the Railway dashboard.

## Environment Variables Reference

### Application Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `production` | Application environment |
| `DEBUG` | `false` | Enable debug logging |
| `DATA_DIR` | `data` | Data storage directory |
| `PORT` | `5000` | API server port (set by Railway) |

### OpenAI Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *required* | OpenAI API key |
| `OPENAI_MODEL` | `gpt-3.5-turbo` | AI model to use |
| `MAX_TOKENS` | `1000` | Maximum tokens per summary |
| `USE_AI_SUMMARIES` | `true` | Enable AI summarization |
| `MAX_API_CALLS_PER_RUN` | `20` | API call limit per run |
| `API_CALL_DELAY` | `2.0` | Delay between API calls |

### Email Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SMTP_SERVER` | `smtp.gmail.com` | SMTP server |
| `SMTP_PORT` | `587` | SMTP port |
| `SMTP_USERNAME` | *required* | Email username |
| `SMTP_PASSWORD` | *required* | Email password/app password |
| `EMAIL_FROM` | *required* | Sender email |
| `EMAIL_TO` | *required* | Recipient email |
| `SEND_EMAIL` | `true` | Enable email reports |

### Scheduling Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SCHEDULE_TIME` | `09:00` | Daily run time (HH:MM) |
| `SCHEDULE_DAY` | `monday` | Day of week for runs |
| `TIMEZONE` | `America/Los_Angeles` | Timezone for scheduling |

### Optional Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ALERT_WEBHOOK_URL` | - | Webhook for alerts |

## Troubleshooting

### Common Issues

**Build Failures**
- Check `requirements.txt` for correct package versions
- Verify Python version compatibility

**Environment Variable Errors**
- Ensure all required variables are set
- Check for typos in variable names
- Verify API key formats

**API Connection Issues**
- Verify CORS is enabled in `api_server.py`
- Check Railway-assigned URL
- Test endpoints individually

**Scheduled Job Problems**
- Check worker service logs
- Verify schedule configuration
- Test manual job execution

### Getting Help

1. Check Railway logs in the dashboard
2. Review the main project README
3. Open an issue on GitHub
4. Contact Railway support for platform issues

## Cost Optimization

### Railway Costs

- **Free Tier**: 500 hours/month compute time
- **Pro Plan**: $5/month base + usage
- **Typical Usage**: $5-15/month for this application

### OpenAI Costs

- **GPT-3.5-turbo**: ~$0.002 per 1K tokens
- **Typical Usage**: $2-10/month depending on document volume
- **Cost Control**: Use `MAX_API_CALLS_PER_RUN` to limit usage

### Total Monthly Cost

Typical range: $7-25/month for a complete civic transparency platform.

## Scaling

Railway automatically handles:
- **Load balancing** for the web service
- **Auto-scaling** based on demand
- **Resource allocation** optimization

For high-traffic scenarios, consider:
- Upgrading to Railway Pro plan
- Implementing caching strategies
- Optimizing API response times

## Security

Railway provides:
- **HTTPS by default** for all endpoints
- **Environment variable encryption**
- **Network isolation** between services
- **Automatic security updates**

Additional security measures:
- Rotate API keys regularly
- Monitor access logs
- Use strong passwords for email accounts
- Enable 2FA on all accounts

## Backup and Recovery

Railway automatically backs up:
- Application code (via GitHub)
- Environment variables
- Service configurations

For data backup:
- Implement custom backup scripts
- Use external storage services
- Export data regularly

## Updates and Maintenance

### Automatic Updates

Railway automatically:
- Deploys changes when you push to GitHub
- Updates infrastructure and security patches
- Manages SSL certificates

### Manual Maintenance

Regularly:
- Review and update dependencies
- Monitor resource usage
- Check API usage and costs
- Update documentation

### Version Control

Use Git tags for releases:
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

Railway can deploy specific tags for stable releases.

