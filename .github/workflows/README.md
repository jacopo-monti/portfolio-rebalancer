# GitHub Actions Workflows

This directory contains GitHub Actions workflows for the Portfolio Rebalancer project.

**All workflows are configured for MANUAL EXECUTION ONLY** to conserve GitHub Actions quota.

---

## 📊 Available Workflows

### 1. Tests (`tests.yml`)

**Purpose:** Run comprehensive test suite across multiple platforms and Python versions

**Trigger:** Manual only (`workflow_dispatch`)

**What it does:**
- Runs pytest test suite with coverage
- Tests on 3 OS platforms: Ubuntu, macOS, Windows
- Tests on 5 Python versions: 3.8, 3.9, 3.10, 3.11, 3.12
- Uploads coverage reports to Codecov
- Provides test summary at the end

**Configuration:**
You can customize which platforms and Python versions to test:
- **python-versions**: Comma-separated list (default: `3.8,3.9,3.10,3.11,3.12`)
- **os-platforms**: Comma-separated list (default: `ubuntu-latest,macos-latest,windows-latest`)

**How to run:**

1. Go to **Actions** tab in GitHub
2. Select **"Tests"** workflow from the left sidebar
3. Click **"Run workflow"** button (top right)
4. (Optional) Customize Python versions or OS platforms
5. Choose branch to test
6. Click **"Run workflow"** to confirm

**Example configurations:**

```yaml
# Quick test (only latest Python on Ubuntu)
python-versions: "3.12"
os-platforms: "ubuntu-latest"

# Cross-platform test (single Python version)
python-versions: "3.10"
os-platforms: "ubuntu-latest,macos-latest,windows-latest"

# Full test suite (default)
python-versions: "3.8,3.9,3.10,3.11,3.12"
os-platforms: "ubuntu-latest,macos-latest,windows-latest"
```

**Why manual only?**

Previously, tests ran automatically on every push and PR, causing:
- 15 parallel jobs per trigger (3 OS × 5 Python versions)
- Rapid GitHub Actions quota exhaustion
- Unnecessary runs for minor documentation changes

Now, tests run only when explicitly needed, conserving quota for important validations.

---

### 2. Deploy to Hugging Face Spaces (`deploy-to-huggingface.yml`)

**Purpose:** Deploy the application to Hugging Face Spaces

**Trigger:** Manual only (`workflow_dispatch`) with confirmation

**What it does:**
1. Validates Hugging Face configuration
2. Prepares HF-compatible repository version:
   - Removes GitHub `README.md`
   - Renames `README_HF.md` to `README.md`
3. Commits and force-pushes to Hugging Face Space
4. Provides deployment summary with URL

**Configuration:**

The workflow uses repository variables for configuration:

| Variable | Description | Example |
|----------|-------------|----------|
| `HF_USERNAME` | Hugging Face username or organization | `Jacmon` |
| `HF_SPACE_NAME` | Name of the Space repository | `Portfolio-rebalancer` |

**Required secret:**

| Secret | Description | How to get |
|--------|-------------|------------|
| `HF_TOKEN` | Hugging Face access token | [Settings > Access Tokens](https://huggingface.co/settings/tokens) |

**How to set up:**

1. **Create Hugging Face token:**
   - Go to https://huggingface.co/settings/tokens
   - Create a new token with **write** access
   - Copy the token (you'll only see it once!)

2. **Add token to GitHub secrets:**
   - Go to repository **Settings** > **Secrets and variables** > **Actions**
   - Click **New repository secret**
   - Name: `HF_TOKEN`
   - Value: (paste your HF token)
   - Click **Add secret**

3. **Set repository variables:**
   - Go to repository **Settings** > **Secrets and variables** > **Actions**
   - Click **Variables** tab
   - Click **New repository variable**
   - Add `HF_USERNAME` with your HF username
   - Add `HF_SPACE_NAME` with your Space name

**How to deploy:**

1. Go to **Actions** tab in GitHub
2. Select **"Deploy to Hugging Face Spaces"** workflow
3. Click **"Run workflow"** button
4. **Type "deploy" in the confirmation field** (required!)
5. Choose branch to deploy (usually `main`)
6. Click **"Run workflow"** to confirm
7. Wait 1-2 minutes for deployment and HF rebuild
8. Visit your Space URL to verify

**Confirmation requirement:**

You **must** type `deploy` in the confirmation field. This prevents accidental deployments.

```
Type "deploy" to confirm deployment to Hugging Face: deploy
```

If you type anything else, the workflow will cancel with a helpful message.

**README handling:**

This workflow ensures proper README separation:

| Repository | README File | Source |
|------------|-------------|--------|
| **GitHub** | `README.md` | GitHub-optimized (installation, dev docs, etc.) |
| **Hugging Face** | `README.md` | Derived from `README_HF.md` (user-focused, HF metadata) |

During deployment:
1. GitHub `README.md` is **removed**
2. `README_HF.md` is **renamed** to `README.md`
3. Only the HF README appears in the Space

**Fallback behavior:**

If `HF_USERNAME` or `HF_SPACE_NAME` variables are not set, the workflow uses hardcoded defaults:
- Username: `Jacmon`
- Space: `Portfolio-rebalancer`

**Set the repository variables for production use!**

---

## 🔧 Troubleshooting

### Tests workflow fails

**Problem:** Test job fails on specific platform or Python version

**Solution:**
1. Check the failed job logs for details
2. Run tests locally on that platform/version
3. Fix the code or test
4. Run workflow again to verify

**Problem:** Codecov upload fails

**Solution:**
- This is non-critical (tests still pass)
- Check if `CODECOV_TOKEN` is set (optional)
- Codecov upload is set to not fail CI

---

### Deployment workflow fails

**Problem:** "HF_TOKEN secret not configured"

**Solution:**
1. Go to repository Settings > Secrets and variables > Actions
2. Add `HF_TOKEN` secret with your HF access token
3. Run workflow again

**Problem:** "README_HF.md not found"

**Solution:**
1. Ensure `README_HF.md` exists in the repository root
2. Check you're deploying from the correct branch
3. Verify the file wasn't accidentally deleted

**Problem:** "Failed to push to Hugging Face"

**Solution:**
1. Verify `HF_TOKEN` has **write** permissions
2. Check HF Space exists and you have access
3. Verify `HF_USERNAME` and `HF_SPACE_NAME` are correct
4. Check Hugging Face status page for outages

**Problem:** "Deployment cancelled" message

**Solution:**
- You didn't type `deploy` in the confirmation field
- Run workflow again and type exactly: `deploy`

---

## 📊 Monitoring

### GitHub Actions quota

Check your Actions quota usage:
1. Go to repository **Settings** > **Billing and plans**
2. View **Actions** usage for the current billing cycle
3. Free tier: 2,000 minutes/month (private repos)
4. Public repos: Unlimited minutes

### Hugging Face Space status

After deployment, monitor your Space:
1. Visit: `https://huggingface.co/spaces/<USERNAME>/<SPACE_NAME>`
2. Check **Logs** tab for build/runtime issues
3. Verify app loads correctly
4. Test functionality

---

## 📅 Workflow History

### Version 2.0 (Current) - Manual Execution Only

**Date:** February 2026

**Changes:**
- Converted all workflows to manual-only execution
- Added configurable test matrix inputs
- Replaced simple HF sync with comprehensive deploy workflow
- Added README swap logic for repository separation
- Added confirmation requirement for deployments
- Added extensive logging and error handling
- Added fallback configuration with warnings

**Why:** Conserve GitHub Actions quota and prevent accidental deploys

### Version 1.0 - Automatic Execution

**Date:** Initial setup

**Changes:**
- Tests ran on every push and PR
- HF sync ran on every push to main
- Simple git push to HF without README handling

**Issues:** Rapid quota exhaustion, no control over deployments

---

## 📚 Best Practices

### Running tests

1. **Before major changes:** Run full test suite on all platforms
2. **During development:** Run quick tests (single Python version, Ubuntu only)
3. **Before release:** Run full test suite to ensure compatibility
4. **After dependency updates:** Test all Python versions

### Deploying to Hugging Face

1. **Test locally first:** Run `streamlit run app.py` to verify
2. **Check README_HF.md:** Ensure it's up-to-date with app features
3. **Review changes:** Check what will be deployed
4. **Deploy from main:** Always deploy from a stable branch
5. **Verify deployment:** Visit Space and test functionality
6. **Monitor logs:** Check for any runtime errors

### Repository maintenance

1. **Keep READMEs separate:** Don't merge GitHub and HF READMEs
2. **Update both READMEs:** When making changes, update both versions
3. **Test workflows periodically:** Run tests occasionally to catch regressions
4. **Monitor quota:** Keep an eye on Actions usage
5. **Review workflow runs:** Check logs for any warnings or issues

---

## ❓ FAQ

**Q: Why are workflows manual-only?**

A: To conserve GitHub Actions quota. Previously, automatic tests ran 15 jobs per push/PR, rapidly exhausting the monthly quota.

**Q: Can I re-enable automatic tests?**

A: Yes, but not recommended. If you have unlimited Actions quota, you can add `push:` and `pull_request:` triggers back to `tests.yml`.

**Q: Why two separate READMEs?**

A: GitHub and Hugging Face have different audiences and requirements:
- GitHub README: Developer-focused (installation, dev setup, contributing)
- HF README: User-focused (how to use the app, features, limitations)

**Q: Does deployment overwrite the HF repository?**

A: Yes, it force-pushes to keep repos in sync. The HF repo is treated as a deployment target, not a source of truth.

**Q: What happens if deployment fails midway?**

A: The workflow will fail and roll back. Your HF Space will remain in its previous state. Fix the issue and run the workflow again.

**Q: Can I deploy from a feature branch?**

A: Yes, but it's not recommended. Deploy from `main` or stable release branches only.

**Q: How do I know if deployment succeeded?**

A: Check the workflow logs for "✅ DEPLOYMENT SUCCESSFUL" message. Then visit your Space URL to verify.

---

## 📧 Support

If you encounter issues with workflows:

1. **Check workflow logs** - Most issues are clearly logged
2. **Review this README** - Solutions for common problems
3. **Check GitHub Actions docs** - https://docs.github.com/actions
4. **Check Hugging Face docs** - https://huggingface.co/docs/hub/spaces
5. **Open an issue** - Describe the problem with logs

---

**Last Updated:** February 2026  
**Workflow Version:** 2.0 (Manual Execution Only)
