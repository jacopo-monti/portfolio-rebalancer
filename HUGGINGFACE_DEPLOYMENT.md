# Hugging Face Spaces Deployment Guide

This guide explains how to deploy the Portfolio Rebalancer application to Hugging Face Spaces.

## Overview

The repository has been reorganized to support **zero-configuration deployment** to Hugging Face Spaces while maintaining full backward compatibility for local development.

## Repository Structure for Hugging Face Spaces

```
portfolio-rebalancer/
├── app.py                          # Main Streamlit application (entry point)
├── requirements.txt                # Python dependencies
├── packages.txt                    # System-level dependencies
├── .python-version                 # Python version specification
├── README_HF.md                    # Hugging Face Space README with metadata
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── src/
│   └── portfolio_rebalancer/       # Core Python package
│       ├── __init__.py
│       ├── engine.py
│       ├── models.py
│       └── policies/
├── webapp/
│   ├── __init__.py
│   ├── ui_helpers.py
│   └── translations.py
├── setup.py                        # Package installation configuration
└── pyproject.toml                  # Project metadata
```

## Key Files for Deployment

### 1. `app.py`
- **Purpose**: Main entry point for the Streamlit application
- **Location**: Root directory (required by Hugging Face)
- **Note**: Already correctly positioned

### 2. `requirements.txt`
- **Purpose**: Lists all Python dependencies
- **Contents**:
  - `streamlit>=1.28.0` - Web framework
  - `pandas>=1.5.0` - Data processing
  - `openpyxl>=3.0.0` - Excel file support
  - `.` - Installs local package from source

### 3. `packages.txt`
- **Purpose**: System-level dependencies (apt packages)
- **Contents**:
  - `libxml2-dev` - Required for openpyxl XML processing
  - `libxslt-dev` - XSLT support

### 4. `.streamlit/config.toml`
- **Purpose**: Streamlit configuration optimized for Spaces
- **Key settings**:
  - Server port: 7860 (Hugging Face default)
  - CORS disabled (handled by Hugging Face)
  - WebSocket compression enabled
  - Custom theme colors

### 5. `.python-version`
- **Purpose**: Specifies Python version for deployment
- **Value**: 3.10 (recommended for stability)

### 6. `README_HF.md`
- **Purpose**: Space description with YAML metadata
- **YAML Frontmatter**:
  ```yaml
  ---
  title: Portfolio Rebalancer
  emoji: 📊
  colorFrom: green
  colorTo: blue
  sdk: streamlit
  sdk_version: 1.28.0
  app_file: app.py
  pinned: false
  license: other
  ---
  ```

## Deployment Steps

### Option 1: Direct Git Integration (Recommended)

1. **Create a Hugging Face Account**
   - Visit https://huggingface.co/
   - Sign up or log in

2. **Create a New Space**
   - Go to https://huggingface.co/spaces
   - Click "+ New Space"
   - Choose:
     - **Space name**: `portfolio-rebalancer` (or your preferred name)
     - **License**: Other
     - **SDK**: Streamlit
     - **Hardware**: CPU basic (free tier)
     - **Visibility**: Public or Private

3. **Connect Your GitHub Repository**
   - After creating the Space, go to **Settings** → **Repository**
   - Click "Connect to GitHub"
   - Authorize Hugging Face to access your repository
   - Select `jacopo-monti/portfolio-rebalancer`
   - Choose branch: `repository-reorganization-for-huggingfaces`

4. **Configure Build**
   - Hugging Face will automatically detect:
     - `app.py` as entry point
     - `requirements.txt` for dependencies
     - `.streamlit/config.toml` for configuration
   - Build will start automatically

5. **Wait for Deployment**
   - Build typically takes 2-5 minutes
   - You can monitor progress in the Space's "Logs" tab
   - Once complete, the app will be live

### Option 2: Manual Upload

1. **Create a New Space** (as above)

2. **Clone the Space Repository**
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/portfolio-rebalancer
   cd portfolio-rebalancer
   ```

3. **Copy Files from This Repository**
   ```bash
   # From your portfolio-rebalancer directory
   cp -r app.py requirements.txt packages.txt .python-version src/ webapp/ .streamlit/ YOUR_HF_SPACE_DIR/
   cp README_HF.md YOUR_HF_SPACE_DIR/README.md
   ```

4. **Commit and Push**
   ```bash
   cd YOUR_HF_SPACE_DIR
   git add .
   git commit -m "Initial deployment"
   git push
   ```

5. **Wait for Build**
   - Hugging Face will automatically rebuild
   - Monitor in the Spaces dashboard

## Verification

### 1. Check Build Logs
- Go to your Space → "Logs" tab
- Verify:
  - ✅ Python 3.10 detected
  - ✅ Dependencies installed successfully
  - ✅ Streamlit server started on port 7860
  - ✅ No import errors

### 2. Test Functionality
- Open the Space URL
- Verify:
  - ✅ Language selector appears
  - ✅ All three tabs are accessible
  - ✅ Default portfolio loads
  - ✅ Can add/edit assets
  - ✅ Rebalancing analysis runs successfully
  - ✅ Tables display correctly
  - ✅ Language switching works

### 3. Common Issues and Solutions

#### Build Fails: "Package not found"
- **Cause**: Missing dependency in requirements.txt
- **Solution**: Check logs for missing package name, add to requirements.txt

#### Runtime Error: "Module not found"
- **Cause**: Import path issue
- **Solution**: Verify package installation with `.` in requirements.txt

#### App Doesn't Load: "Connection timeout"
- **Cause**: Streamlit config issue
- **Solution**: Check `.streamlit/config.toml` port is 7860

#### Slow Performance
- **Cause**: Free tier CPU limitations
- **Solution**: Upgrade to better hardware tier in Space settings

## Environment Variables

If you need to add environment variables (e.g., API keys):

1. Go to Space Settings → "Variables and secrets"
2. Click "New secret"
3. Add name and value
4. Restart the Space

## Hardware Requirements

### Minimum (Free Tier)
- CPU: 2 vCPUs
- RAM: 16 GB
- Storage: 50 GB (ephemeral)
- **Sufficient for**: Demo, testing, light usage

### Recommended (Paid)
- CPU: 4+ vCPUs
- RAM: 32+ GB
- **Better for**: Production, multiple concurrent users

## Maintenance

### Updating the Application

**If using GitHub integration:**
1. Push changes to your GitHub repository
2. Hugging Face automatically rebuilds

**If using manual upload:**
1. Clone the Space repository
2. Make changes
3. Commit and push

### Monitoring

- **Logs**: Real-time application logs in Spaces dashboard
- **Analytics**: User statistics (if public Space)
- **Health**: Automatic health checks by Hugging Face

## Security Considerations

1. **No Data Persistence**: All data is in-memory, lost on restart
2. **Public Access**: If Space is public, anyone can use it
3. **No Authentication**: No built-in user authentication
4. **Rate Limiting**: Applied by Hugging Face based on tier

## Cost

- **Free Tier**: CPU basic (2 vCPU, 16GB RAM) - $0/month
- **Upgraded Hardware**: Varies, check Hugging Face pricing
- **Private Spaces**: Requires PRO subscription ($9/month)

## Support

- **Hugging Face Docs**: https://huggingface.co/docs/hub/spaces
- **Community Forum**: https://discuss.huggingface.co/
- **Status**: https://status.huggingface.co/

## Backward Compatibility

All changes maintain full backward compatibility:

✅ **Local development**: `streamlit run app.py` still works  
✅ **Package installation**: `pip install -e .` unchanged  
✅ **Testing**: `pytest` runs normally  
✅ **CLI tools**: All examples still function  
✅ **Excel export**: Functionality preserved

## Next Steps

1. ✅ Repository reorganization complete
2. ✅ Deployment files created
3. ✅ Configuration optimized
4. ◻ Deploy to Hugging Face Spaces (manual step)
5. ◻ Test deployed application
6. ◻ Share Space URL with users

## Questions?

For issues specific to this repository:
- GitHub Issues: https://github.com/jacopo-monti/portfolio-rebalancer/issues

For Hugging Face Spaces issues:
- Hugging Face Forums: https://discuss.huggingface.co/
