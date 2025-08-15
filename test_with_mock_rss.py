#!/usr/bin/env python3
"""
Test the complete incremental update workflow with simulated RSS data
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Set environment variables
os.environ['DEVTO_USERNAME'] = 'anchildress1'
os.environ['PAGES_REPO'] = 'anchildress1/devto-mirror'

# Mock feedparser.parse to return controlled data
class MockEntry:
    def __init__(self, title, link, date, content):
        self.title = title
        self.link = link
        self.published = date
        self.content = [type('obj', (object,), {'value': content})]

class MockFeed:
    def __init__(self, entries):
        self.entries = entries
        self.bozo = False

def create_mock_rss_entries():
    """Create mock RSS entries for testing"""
    return [
        MockEntry(
            "Super New Post About AI",
            "https://dev.to/anchildress1/super-new-post-about-ai",
            "Fri, 16 Aug 2025 14:00:00 +0000",  # Very recent
            "<p>This is a super new post about AI that just came out.</p>"
        ),
        MockEntry(
            "Another New Post About Copilot",
            "https://dev.to/anchildress1/another-new-post-about-copilot", 
            "Thu, 15 Aug 2025 18:00:00 +0000",  # Also recent
            "<p>This is another new post about GitHub Copilot.</p>"
        ),
        MockEntry(
            "Everything I Know About GitHub Copilot Instructions — From Zero to Onboarded (For Real) ⚡",
            "https://dev.to/anchildress1/everything-i-know-about-github-copilot-instructions-from-zero-to-onboarded-for-r",
            "Wed, 13 Aug 2025 11:45:00 +0000",  # This one should already exist
            "<p>Existing post content...</p>"
        )
    ]

def test_incremental_update():
    """Test the complete incremental update workflow"""
    print("🧪 Testing incremental update workflow...")
    
    # Create a working directory
    test_dir = Path("test_incremental_temp")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    # Copy necessary files
    shutil.copy("scripts/generate_site.py", test_dir)
    shutil.copy("posts_data.json", test_dir)
    shutil.copy("comments.txt", test_dir)
    
    # Change to test directory
    original_cwd = os.getcwd()
    os.chdir(test_dir)
    
    try:
        # Mock feedparser.parse in the generate_site module
        sys.path.insert(0, '.')
        
        # Create the modified script that uses our mock data
        with open("generate_site.py", "r") as f:
            script_content = f.read()
        
        # Replace the feedparser.parse call with our mock
        mock_rss_code = '''
# MOCK RSS DATA FOR TESTING
class MockEntry:
    def __init__(self, title, link, date, content):
        self.title = title
        self.link = link
        self.published = date
        self.content = [type('obj', (object,), {'value': content})]

class MockFeed:
    def __init__(self, entries):
        self.entries = entries
        self.bozo = False

# Create mock RSS entries for testing
mock_entries = [
    MockEntry(
        "Super New Post About AI",
        "https://dev.to/anchildress1/super-new-post-about-ai",
        "Fri, 16 Aug 2025 14:00:00 +0000",
        "<p>This is a super new post about AI that just came out.</p>"
    ),
    MockEntry(
        "Another New Post About Copilot",
        "https://dev.to/anchildress1/another-new-post-about-copilot", 
        "Thu, 15 Aug 2025 18:00:00 +0000",
        "<p>This is another new post about GitHub Copilot.</p>"
    ),
    MockEntry(
        "Everything I Know About GitHub Copilot Instructions — From Zero to Onboarded (For Real) ⚡",
        "https://dev.to/anchildress1/everything-i-know-about-github-copilot-instructions-from-zero-to-onboarded-for-r",
        "Wed, 13 Aug 2025 11:45:00 +0000",
        "<p>Existing post content...</p>"
    )
]

feed = MockFeed(mock_entries)
print("Using mock RSS feed with entries:")
for entry in feed.entries:
    print(f"  - {entry.title} ({entry.published})")
'''
        
        # Replace the RSS fetching section
        rss_section_start = script_content.find("FEED_URL = f\"https://dev.to/feed/{DEVTO_USERNAME}\"")
        rss_section_end = script_content.find("feed = MockFeed()")
        if rss_section_end == -1:
            rss_section_end = script_content.find("# ----------------------------\n# Templates (posts + index)")
        
        new_script = (
            script_content[:rss_section_start] + 
            mock_rss_code + "\n\n" +
            script_content[rss_section_end + (len("feed = MockFeed()") if "feed = MockFeed()" in script_content else 0):]
        )
        
        with open("generate_site_test.py", "w") as f:
            f.write(new_script)
        
        # Make posts directory
        Path("posts").mkdir(exist_ok=True)
        
        # Run the test script
        print("\n📋 Running incremental update test...")
        result = os.system("python generate_site_test.py")
        
        if result == 0:
            print("✅ Script executed successfully!")
            
            # Check results
            if Path("index.html").exists():
                with open("index.html", "r") as f:
                    index_content = f.read()
                
                # Count posts in index
                post_count = index_content.count('href="posts/')
                print(f"📊 Posts in index.html: {post_count}")
                
                # Check if new posts are at the top
                if "Super New Post About AI" in index_content:
                    print("✅ New post 'Super New Post About AI' found in index")
                else:
                    print("❌ New post 'Super New Post About AI' NOT found in index")
                
                if "Another New Post About Copilot" in index_content:
                    print("✅ New post 'Another New Post About Copilot' found in index")
                else:
                    print("❌ New post 'Another New Post About Copilot' NOT found in index")
                
                # Check if new post files were created
                new_post_files = [
                    "posts/super-new-post-about-ai.html",
                    "posts/another-new-post-about-copilot.html"
                ]
                
                for post_file in new_post_files:
                    if Path(post_file).exists():
                        print(f"✅ Post file {post_file} was created")
                    else:
                        print(f"❌ Post file {post_file} was NOT created")
                
                # Check posts_data.json was updated
                if Path("posts_data.json").exists():
                    with open("posts_data.json", "r") as f:
                        posts_data = json.load(f)
                    print(f"📊 Total posts in posts_data.json: {len(posts_data)}")
                    
                    # Check if new posts are at the beginning
                    if posts_data and posts_data[0]['title'] == "Super New Post About AI":
                        print("✅ Newest post is at the beginning of posts_data.json")
                    else:
                        print("❌ Posts order may not be correct in posts_data.json")
                
            else:
                print("❌ index.html was not created")
        else:
            print(f"❌ Script failed with exit code {result}")
            
    finally:
        # Clean up
        os.chdir(original_cwd)
        if test_dir.exists():
            shutil.rmtree(test_dir)

if __name__ == "__main__":
    test_incremental_update()