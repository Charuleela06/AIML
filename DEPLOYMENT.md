# 🚀 Deployment Guide - EQREV Hackathon

This guide covers multiple deployment options for the Agentic AI for Quick Commerce system.

## 🌟 Hugging Face Spaces (Recommended)

### Option 1: Direct Upload

1. **Create a new Space**:
   - Go to [Hugging Face Spaces](https://huggingface.co/new-space)
   - Choose "Streamlit" as the SDK
   - Name it: `quick-commerce-ai-agent`

2. **Upload files**:
   - Upload all files from this repository
   - Ensure `app.py` is in the root directory

3. **Configure environment variables** (optional):
   - Go to Settings → Variables
   - Add `OPENAI_API_KEY` if you have one
   - Add `N8N_WEBHOOK_URL` if using n8n

4. **Deploy**:
   - The space will automatically build and deploy
   - Access your app at: `https://huggingface.co/spaces/yourusername/quick-commerce-ai-agent`

### Option 2: Git Integration

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Initial commit - EQREV Hackathon"
   git push origin main
   ```

2. **Connect to Hugging Face**:
   - In your Space settings, connect your GitHub repository
   - Set the root directory if needed

## 🐳 Docker Deployment

### Local Docker

```bash
# Build the image
docker build -t quick-commerce-ai .

# Run the container
docker run -p 8501:8501 quick-commerce-ai

# Access at http://localhost:8501
```

### Docker Hub

```bash
# Tag and push
docker tag quick-commerce-ai yourusername/quick-commerce-ai
docker push yourusername/quick-commerce-ai

# Pull and run
docker pull yourusername/quick-commerce-ai
docker run -p 8501:8501 yourusername/quick-commerce-ai
```

## ☁️ Cloud Deployment Options

### 1. Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Deploy!

### 2. Render

1. Create a new Web Service
2. Connect your GitHub repository
3. Use the Dockerfile
4. Set environment variables
5. Deploy

### 3. Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### 4. Heroku

```bash
# Install Heroku CLI
# Create Procfile
echo "web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0" > Procfile

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

## 🔧 Environment Configuration

### Required Environment Variables

```env
# Optional - for OpenAI integration
OPENAI_API_KEY=your_api_key_here

# Optional - for n8n automation
N8N_WEBHOOK_URL=http://your-n8n-instance.com/webhook/quick-commerce

# Database (automatically configured)
DATABASE_URL=sqlite:///data/quick_commerce.db
```

### Hugging Face Spaces Configuration

In your Space settings, add these variables:
- `OPENAI_API_KEY`: Your OpenAI API key (optional)
- `N8N_WEBHOOK_URL`: Your n8n webhook URL (optional)

## 📊 System Requirements

### Minimum Requirements
- **CPU**: 1 vCPU
- **RAM**: 2 GB
- **Storage**: 1 GB
- **Python**: 3.8+

### Recommended Requirements
- **CPU**: 2 vCPU
- **RAM**: 4 GB
- **Storage**: 2 GB
- **Python**: 3.9+

## 🚀 Quick Start Commands

### Local Development

```bash
# Clone repository
git clone <your-repo-url>
cd AIML

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate sample data
python backend/data_generator.py
python backend/models.py

# Run Streamlit app
streamlit run frontend/app.py
```

### Production Deployment

```bash
# For Hugging Face Spaces - just upload files
# For Docker
docker build -t quick-commerce-ai .
docker run -p 8501:8501 quick-commerce-ai

# For Streamlit Cloud - push to GitHub and connect
```

## 🔍 Health Checks

The application includes health check endpoints:

- **Streamlit**: `/_stcore/health`
- **FastAPI**: `/health`

## 📈 Performance Optimization

### For Hugging Face Spaces
- Use `packages.txt` for system dependencies
- Optimize Dockerfile layers
- Use `.dockerignore` to exclude unnecessary files

### For Production
- Enable caching for database queries
- Use connection pooling
- Implement rate limiting
- Add monitoring and logging

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**:
   - Ensure all dependencies are in `requirements.txt`
   - Check Python path configuration

2. **Database Issues**:
   - Verify data generation completed
   - Check file permissions

3. **API Connection Issues**:
   - Verify environment variables
   - Check network connectivity

4. **Memory Issues**:
   - Increase RAM allocation
   - Optimize data loading

### Debug Mode

```bash
# Enable debug logging
export STREAMLIT_LOGGER_LEVEL=debug
streamlit run app.py
```

## 📞 Support

For deployment issues:
1. Check the logs in your deployment platform
2. Verify all files are uploaded correctly
3. Ensure environment variables are set
4. Test locally first

## 🎯 Deployment Checklist

- [ ] All files uploaded/committed
- [ ] Environment variables configured
- [ ] Dependencies installed
- [ ] Sample data generated
- [ ] Health checks passing
- [ ] Application accessible
- [ ] AI agent responding
- [ ] Database working
- [ ] Visualizations loading

## 🏆 Final Deployment

Once deployed, your application should be accessible at:
- **Hugging Face Spaces**: `https://huggingface.co/spaces/yourusername/quick-commerce-ai-agent`
- **Local**: `http://localhost:8501`
- **Docker**: `http://localhost:8501`

Test the following scenarios:
1. "Allocate 1000 units of Smartphone"
2. "Which items need urgent restocking?"
3. "Which cities are underperforming this week?"

---

**Ready to deploy! 🚀**
