# 🚀 Streamlit Cloud Deployment Guide

## Prerequisites

1. **GitHub Account**: Your code must be in a GitHub repository
2. **Streamlit Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **Groq API Key**: Get your free API key from [Groq Console](https://console.groq.com)

## Step-by-Step Deployment

### 1. Prepare Your Repository

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - LangGraph Chatbot"
   git branch -M main
   git remote add origin https://github.com/yourusername/your-repo-name.git
   git push -u origin main
   ```

### 2. Deploy on Streamlit Community Cloud

1. **Visit Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

2. **Create New App**:
   - Click "New app"
   - Select your GitHub repository
   - Choose branch: `main`
   - Main file path: `app.py`
   - App name: `your-chatbot-name` (optional)

3. **Configure Secrets**:
   - In the deployment settings, click "Advanced settings"
   - Add your secrets in the "Secrets" section:
   ```toml
   GROQ_API_KEY = "your_actual_groq_api_key_here"
   ```

4. **Deploy**:
   - Click "Deploy!"
   - Wait for the deployment to complete (usually 2-3 minutes)

### 3. Environment Variables Setup

Your app needs these environment variables:

- **GROQ_API_KEY** (Required): Your Groq API key for the LLM
- **ALPHA_VANTAGE_API_KEY** (Optional): The stock price tool uses a built-in key, but you can provide your own

### 4. Verify Deployment

Once deployed, your app will be available at:
`https://your-app-name.streamlit.app`

Test these features:
- ✅ Basic chat functionality
- ✅ Web search tool
- ✅ Stock price lookup
- ✅ Calculator tool
- ✅ Conversation persistence

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**:
   - Ensure all dependencies are in `requirements.txt`
   - Check for version conflicts

2. **API Key Issues**:
   - Verify GROQ_API_KEY is correctly set in Streamlit secrets
   - Check API key format (should start with "gsk_")

3. **Database Issues**:
   - The app automatically creates a temporary database in cloud environment
   - Conversations are preserved during the session but reset on app restart

4. **Memory Issues**:
   - Streamlit Community Cloud has memory limits
   - Large conversation histories might cause issues

### Performance Optimization

1. **Resource Limits**:
   - Streamlit Community Cloud: 1 CPU, 800MB RAM
   - Keep conversation history reasonable size
   - Consider implementing conversation pruning

2. **Response Times**:
   - First response might be slower due to cold start
   - Subsequent responses are typically faster

## 📱 Usage Tips

1. **Mobile Friendly**: The app works well on mobile devices
2. **Sharing**: Share your app URL with others
3. **Updates**: Push to GitHub to update your deployed app
4. **Monitoring**: Check Streamlit Cloud dashboard for app health

## 🆙 Updating Your App

To update your deployed app:

1. Make changes to your code locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update: your changes description"
   git push
   ```
3. Streamlit Cloud will automatically redeploy (takes 1-2 minutes)

## 💡 Advanced Configuration

### Custom Domain (Premium)
- Streamlit Community Cloud apps get a `.streamlit.app` domain
- Custom domains require Streamlit for Teams

### Scaling
- For higher traffic, consider Streamlit for Teams
- For enterprise use, deploy on your own infrastructure

## 📞 Support

- **Streamlit Community**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **Documentation**: [docs.streamlit.io](https://docs.streamlit.io)
- **GitHub Issues**: Report bugs in your repository

## 🎉 Your App is Live!

Once deployed, your LangGraph chatbot will be accessible to anyone with the URL. Share it with friends, add it to your portfolio, or use it for demonstrations!

**Sample URL**: `https://langgraph-chatbot.streamlit.app`

---

**Note**: Keep your API keys secure and never commit them to your repository. Always use Streamlit secrets for sensitive information.