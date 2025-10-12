#!/usr/bin/env python3
"""
Post Description Analysis Script

This script analyzes posts_data.json to identify:
1. Posts with descriptions exceeding 140-145 character SEO limits
2. Posts with missing descriptions (using fallback from content)

Usage:
  python scripts/analyze_descriptions.py [posts_file]

If no file is specified, defaults to posts_data.json
"""
import json
import sys
from pathlib import Path

def analyze_posts_data(posts_file='posts_data.json'):
    """Analyze posts data for description length violations and missing descriptions"""
    posts_path = Path(posts_file)

    if not posts_path.exists():
        print(f"No {posts_file} found. Cannot analyze descriptions.")
        return [], []

    try:
        with posts_path.open('r', encoding='utf-8') as f:
            posts_data = json.load(f)
    except Exception as e:
        print(f"Error reading {posts_file}: {e}")
        return [], []

    print(f"Analyzing {len(posts_data)} posts from {posts_file}...")

    long_descriptions = []
    missing_descriptions = []

    for post in posts_data:
        title = post.get('title', 'Untitled')
        description = post.get('description', '')
        url = post.get('link', 'No URL')

        # Check for missing descriptions
        if not description or len(description.strip()) == 0:
            missing_descriptions.append({
                'title': title,
                'url': url,
                'reason': 'Empty or missing description'
            })
            print(f"⚠️  WARNING: Missing description for post '{title}'")
        # Check for descriptions that exceed the 140-145 char limit
        elif len(description) > 145:
            long_descriptions.append({
                'title': title,
                'url': url,
                'description': description,
                'length': len(description),
                'status': 'EXCEEDS LIMIT'
            })
        elif len(description) > 140:
            long_descriptions.append({
                'title': title,
                'url': url,
                'description': description,
                'length': len(description),
                'status': 'NEAR LIMIT'
            })

    return long_descriptions, missing_descriptions

def generate_report(long_descriptions, missing_descriptions):
    """Generate a formatted report"""
    print("\n" + "=" * 80)
    print("POST DESCRIPTION ANALYSIS REPORT")
    print("=" * 80)

    print("\n📊 SUMMARY")
    print(f"Posts with descriptions exceeding 140-145 characters: {len(long_descriptions)}")
    print(f"Posts with missing descriptions: {len(missing_descriptions)}")

    if long_descriptions:
        print("\n📏 POSTS WITH LONG DESCRIPTIONS (>140 chars)")
        print("-" * 50)
        for i, item in enumerate(long_descriptions, 1):
            status_icon = "🔴" if item['status'] == 'EXCEEDS LIMIT' else "🟡"
            print(f"{i}. {status_icon} {item['title']} ({item['length']} chars) [{item['status']}]")
            print(f"   URL: {item['url']}")
            print(f"   Description: {item['description'][:100]}...")
            print()

    if missing_descriptions:
        print("\n❌ POSTS WITH MISSING DESCRIPTIONS")
        print("-" * 40)
        for i, item in enumerate(missing_descriptions, 1):
            print(f"{i}. {item['title']} - {item['reason']}")
            print(f"   URL: {item['url']}")
            print()

    # Generate markdown for follow-up comments
    if long_descriptions or missing_descriptions:
        print("\n📝 FOLLOW-UP COMMENT (Markdown format):")
        print("-" * 50)
        print("## Post Description Analysis Results")
        print()

        if long_descriptions:
            print("### Posts with descriptions exceeding 140-145 character limit:")
            for item in long_descriptions:
                status = "⚠️ Near limit" if item['status'] == 'NEAR LIMIT' else "🔴 Exceeds limit"
                print(f"- **{item['title']}** ({item['length']} chars) - {status}")
                print(f"  - URL: {item['url']}")
                print(f"  - Description: `{item['description'][:100]}...`")
                print()

        if missing_descriptions:
            print("### Posts with missing descriptions (using fallback):")
            for item in missing_descriptions:
                print(f"- **{item['title']}** - {item['reason']}")
                print(f"  - URL: {item['url']}")
                print()
    else:
        print("\n✅ All post descriptions are within acceptable limits!")

def main():
    # Analyze the current posts_data.json file or provided argument
    posts_file = sys.argv[1] if len(sys.argv) > 1 else 'posts_data.json'
    long_descriptions, missing_descriptions = analyze_posts_data(posts_file)
    generate_report(long_descriptions, missing_descriptions)

if __name__ == "__main__":
    main()
