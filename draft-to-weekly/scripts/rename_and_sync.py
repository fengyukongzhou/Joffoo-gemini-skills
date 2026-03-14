import os
import re
import sys
import argparse
from pathlib import Path

def sync_links(vault_root, old_link, new_link):
    """
    Search all markdown files in the vault and replace old_link with new_link.
    """
    print(f"  Syncing links: {old_link} -> {new_link}")
    for root, dirs, files in os.walk(vault_root):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        if "_attachments" in dirs:
            dirs.remove("_attachments")
            
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if old_link in content:
                        print(f"    Updating: {file_path}")
                        new_content = content.replace(old_link, new_link)
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                except Exception as e:
                    print(f"    Error reading {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Rename images and sync links in Obsidian vault.")
    parser.add_argument("markdown_path", help="Path to the weekly markdown file")
    parser.add_argument("issue_num", help="Issue number (e.g., 017)")
    args = parser.parse_args()

    md_path = Path(args.markdown_path)
    if not md_path.exists():
        print(f"Error: File not found {md_path}")
        sys.exit(1)

    # Assume vault root is the parent of _attachments or the current working directory
    # For this project, we are in the root.
    vault_root = Path.cwd()
    attachments_dir = vault_root / "_attachments"

    if not attachments_dir.exists():
        print(f"Error: _attachments directory not found at {attachments_dir}")
        sys.exit(1)

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all ![[image.ext]] links
    matches = re.findall(r'!\[\[(.*?)\]\]', content)
    if not matches:
        print("No Obsidian-style image links found.")
        return

    # Process matches
    index = 0
    # Use a dictionary to avoid double renaming if same image used twice
    renamed_map = {}

    for old_name in matches:
        if old_name in renamed_map:
            continue
            
        ext = os.path.splitext(old_name)[1]
        new_name = f"zw{args.issue_num}-{index}{ext}"
        
        old_file_path = attachments_dir / old_name
        new_file_path = attachments_dir / new_name

        if old_file_path.exists():
            print(f"Renaming {old_name} -> {new_name}")
            try:
                os.rename(old_file_path, new_file_path)
                
                old_link = f"![[{old_name}]]"
                new_link = f"![]({new_name})"
                
                # Sync in the whole vault
                sync_links(vault_root, old_link, new_link)
                
                renamed_map[old_name] = new_name
                index += 1
            except Exception as e:
                print(f"Error renaming {old_name}: {e}")
        else:
            print(f"Warning: File not found {old_file_path}")

    print("Done.")

if __name__ == "__main__":
    main()
