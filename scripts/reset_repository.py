#!/usr/bin/env python3
"""
Reset Repository Script
Restores the devto-mirror repository to its original state by removing all generated content.
"""

import shutil
import json
from pathlib import Path


def reset_repository():
    """Reset the repository to its original state"""
    repo_root = Path(__file__).parent.parent

    print("🚨 Starting repository reset process...")
    print(f"📁 Repository root: {repo_root}")

    # Files and directories to remove
    items_to_remove = [
        "posts",            # Directory containing all blog post HTML files
        "index.html",       # Generated index page
        "sitemap.xml",      # Generated sitemap
        "posts_data.json",  # Posts data tracking file
        "robots.txt"        # Generated robots.txt (if it exists)
    ]

    removed_items = []

    for item in items_to_remove:
        item_path = repo_root / item

        if item_path.exists():
            try:
                if item_path.is_dir():
                    shutil.rmtree(item_path)
                    print(f"🗂️  Removed directory: {item}")
                else:
                    item_path.unlink()
                    print(f"📄 Removed file: {item}")
                removed_items.append(item)
            except Exception as e:
                print(f"❌ Error removing {item}: {e}")
        else:
            print(f"ℹ️  {item} does not exist, skipping")

    # Create a reset summary
    reset_summary = {
        "reset_timestamp": "Reset completed",
        "removed_items": removed_items,
        "status": "Repository restored to original state"
    }

    # Optional: Create a temporary reset log (will be removed by git add -A)
    reset_log_path = repo_root / "RESET_LOG.json"
    with open(reset_log_path, 'w', encoding='utf-8') as f:
        json.dump(reset_summary, f, indent=2)

    print("\n✅ Reset process completed!")
    print("📋 Summary of removed items:")
    for item in removed_items:
        print(f"   - {item}")

    if not removed_items:
        print("ℹ️  No items needed to be removed - repository may already be in original state")

    print("\n🔄 Next steps:")
    print("   1. Review the changes in the workflow")
    print("   2. Approve the workflow to commit the reset")
    print("   3. GitHub Pages will be disabled automatically")
    print("   4. Repository will be ready for fresh setup")


if __name__ == "__main__":
    reset_repository()
