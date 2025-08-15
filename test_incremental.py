#!/usr/bin/env python3
"""
Test script to verify the incremental update logic works correctly
"""

import sys
import os
sys.path.append('scripts')

# Mock feedparser entry for testing
class MockEntry:
    def __init__(self, title, link, date, content):
        self.title = title
        self.link = link
        self.published = date
        self.content = [type('obj', (object,), {'value': content})]

# Import the Post class and functions we want to test
from generate_site import Post, find_new_posts

def test_find_new_posts():
    print("Testing find_new_posts function...")
    
    # Create existing posts (older)
    existing_entry1 = MockEntry("Old Post 1", "https://dev.to/test/old-1", "Mon, 10 Aug 2025 10:00:00 +0000", "<p>Old content 1</p>")
    existing_entry2 = MockEntry("Old Post 2", "https://dev.to/test/old-2", "Sun, 09 Aug 2025 10:00:00 +0000", "<p>Old content 2</p>")
    existing_posts = [Post(existing_entry1), Post(existing_entry2)]
    
    # Create RSS posts (newest first, some overlap with existing)
    rss_entry1 = MockEntry("New Post 1", "https://dev.to/test/new-1", "Wed, 13 Aug 2025 10:00:00 +0000", "<p>New content 1</p>")
    rss_entry2 = MockEntry("New Post 2", "https://dev.to/test/new-2", "Tue, 12 Aug 2025 10:00:00 +0000", "<p>New content 2</p>")
    rss_entry3 = MockEntry("Old Post 1", "https://dev.to/test/old-1", "Mon, 10 Aug 2025 10:00:00 +0000", "<p>Old content 1</p>")  # This one exists
    rss_entry4 = MockEntry("Old Post 2", "https://dev.to/test/old-2", "Sun, 09 Aug 2025 10:00:00 +0000", "<p>Old content 2</p>")  # This one exists too
    
    rss_posts = [Post(rss_entry1), Post(rss_entry2), Post(rss_entry3), Post(rss_entry4)]
    
    # Test: should return only the first 2 new posts, stop when it hits the first existing one
    new_posts = find_new_posts(rss_posts, existing_posts)
    
    assert len(new_posts) == 2, f"Expected 2 new posts, got {len(new_posts)}"
    assert new_posts[0].title == "New Post 1", f"Expected 'New Post 1', got '{new_posts[0].title}'"
    assert new_posts[1].title == "New Post 2", f"Expected 'New Post 2', got '{new_posts[1].title}'"
    
    print("✓ find_new_posts works correctly")

def test_first_run_scenario():
    print("Testing first run scenario...")
    
    # First run: no existing posts
    rss_entry1 = MockEntry("First Post", "https://dev.to/test/first", "Wed, 13 Aug 2025 10:00:00 +0000", "<p>First content</p>")
    rss_posts = [Post(rss_entry1)]
    existing_posts = []
    
    new_posts = find_new_posts(rss_posts, existing_posts)
    
    assert len(new_posts) == 1, f"Expected 1 new post, got {len(new_posts)}"
    assert new_posts[0].title == "First Post", f"Expected 'First Post', got '{new_posts[0].title}'"
    
    print("✓ First run scenario works correctly")

def test_no_new_posts():
    print("Testing no new posts scenario...")
    
    # All RSS posts already exist
    existing_entry = MockEntry("Existing Post", "https://dev.to/test/existing", "Mon, 10 Aug 2025 10:00:00 +0000", "<p>Existing content</p>")
    existing_posts = [Post(existing_entry)]
    
    rss_entry = MockEntry("Existing Post", "https://dev.to/test/existing", "Mon, 10 Aug 2025 10:00:00 +0000", "<p>Existing content</p>")
    rss_posts = [Post(rss_entry)]
    
    new_posts = find_new_posts(rss_posts, existing_posts)
    
    assert len(new_posts) == 0, f"Expected 0 new posts, got {len(new_posts)}"
    
    print("✓ No new posts scenario works correctly")

if __name__ == "__main__":
    test_first_run_scenario()
    test_no_new_posts()
    test_find_new_posts()
    print("\n✅ All tests passed!")