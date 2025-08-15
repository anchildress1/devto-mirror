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
export PAGES_REPO="username/repo"
python scripts/generate_site.py
```

The script automatically detects first run vs subsequent runs and behaves accordingly.