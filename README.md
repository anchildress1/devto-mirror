# Dev.to Mirror - Incremental Updates

This repository mirrors blog posts from Dev.to using an incremental update system that preserves historical posts.

## How it works

### First Run
- Fetches all posts from the RSS feed
- Generates HTML files for all posts
- Creates `posts_data.json` to track all posts
- Generates `index.html` and `sitemap.xml`

### Subsequent Runs  
- Fetches latest posts from RSS feed
- Compares against existing posts in `posts_data.json`
- Only processes NEW posts (stops when it finds an existing post)
- Generates HTML files only for new posts
- Updates `posts_data.json` with new posts at the top
- Regenerates `index.html` and `sitemap.xml` with complete post list

## Key Benefits

1. **Preserves History**: Maintains all historical posts, not just the last 30 days from RSS
2. **Efficient**: Only generates HTML for new posts, skips existing ones
3. **Rolling Updates**: New posts appear at the top, creating a growing archive
4. **Fast**: No need to regenerate existing content

## Files

- `scripts/generate_site.py` - Main script with incremental update logic
- `posts_data.json` - Persistent storage of all posts (auto-generated)
- `.github/workflows/publish.yaml` - GitHub Actions workflow (runs daily)

## Environment Variables

- `DEVTO_USERNAME` - Your Dev.to username
- `PAGES_REPO` - GitHub repository in format "username/repo"

## Manual Usage

```bash
export DEVTO_USERNAME="your-username"
# PAGES_REPO is automatically calculated from your repository information
python scripts/generate_site.py
```

The script automatically detects first run vs subsequent runs and behaves accordingly.

## Forking and Using This Mirror

### Quick Setup for Your Own Dev.to Mirror

1. **Fork this repository**
   ```bash
   # Click "Fork" on GitHub or use GitHub CLI
   gh repo fork anchildress1/devto-mirror --clone
   ```

2. **Configure your Dev.to username**
   - Go to your forked repository settings
   - Navigate to Settings → Secrets and variables → Repository variables
   - Add a new variable:
     - Name: `DEVTO_USERNAME`
     - Value: `your-devto-username`

3. **Enable GitHub Pages**
   - Go to Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main` (or your default branch)
   - Folder: `/ (root)`

4. **Run the initial setup**
   - Go to Actions tab
   - Click on "Dev.to Mirror (Static, Hourly)"
   - Click "Run workflow" → "Run workflow"
   - Wait for completion

5. **Your mirror is ready!**
   - Visit `https://yourusername.github.io/devto-mirror`
   - Posts will auto-update daily at 2:15 PM UTC

### Reset All - Restore to Original State

If you want to completely reset your forked repository back to its original state (useful for troubleshooting or starting fresh):

1. **Trigger the reset workflow**
   - Go to Actions tab in your forked repository
   - Click on "Reset All - Restore Repository to Original State"
   - Click "Run workflow"
   - In the confirmation field, type exactly: `RESET`
   - Click "Run workflow"

2. **Review and approve the reset**
   - The workflow will show you what will be deleted
   - It will pause and wait for your manual approval
   - **⚠️ Warning**: This action cannot be undone!
   - Only the person who started the workflow can approve it

3. **What gets reset:**
   - 🗂️ All generated blog post HTML files (`posts/` directory)
   - 📄 Generated `index.html`, `sitemap.xml`, `posts_data.json`
   - 🔗 GitHub Pages site is disabled
   - 🎯 Repository returns to clean, original state

4. **After reset:**
   - Re-run the setup process above to recreate your mirror
   - All previous blog post content will be regenerated fresh

### Troubleshooting

- **No posts appearing**: Check that `DEVTO_USERNAME` variable is set correctly
- **Pages not updating**: Verify GitHub Pages is enabled and workflow is running
- **Want to start fresh**: Use the "Reset All" workflow described above