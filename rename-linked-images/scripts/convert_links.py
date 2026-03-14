import re
import argparse
import urllib.parse
from pathlib import Path

def wiki_to_markdown(content):
    """
    Convert ![[filename.png|alt]] to ![alt](filename.png)
    """
    # Regex for Obsidian WikiLinks: ![[filename.ext|alt]]
    pattern = r'!\[\[([^\]|#]+)(?:\|([^\]]*))?\]\]'
    
    def replace(match):
        filename = match.group(1).strip()
        alt = match.group(2) or ""
        # Encode spaces for standard markdown links
        encoded_filename = urllib.parse.quote(filename) if ' ' in filename else filename
        return f'![{alt.strip()}]({encoded_filename})'
    
    return re.sub(pattern, replace, content)

def markdown_to_wiki(content):
    """
    Convert ![alt](filename.png) to ![[filename.png|alt]]
    """
    # Regex for standard Markdown links: ![alt](filename.ext)
    pattern = r'!\[([^\]]*)\]\(([^)\s]+?)\)'
    
    def replace(match):
        alt = match.group(1).strip()
        filename = match.group(2).strip()
        # Decode filename if it's encoded
        try:
            filename = urllib.parse.unquote(filename)
        except:
            pass
            
        if alt:
            return f'![[{filename}|{alt}]]'
        else:
            return f'![[{filename}]]'
            
    return re.sub(pattern, replace, content)

def main():
    parser = argparse.ArgumentParser(description='Convert between WikiLinks and Markdown image links.')
    parser.add_argument('md_file', help='Path to the Markdown file')
    parser.add_argument('--to', choices=['markdown', 'wiki'], required=True, help='Target format')
    parser.add_argument('--dry-run', action='store_true', help='Print changes without applying them')
    
    args = parser.parse_args()
    
    md_path = Path(args.md_file).resolve()
    if not md_path.exists():
        print(f"Error: {md_path} does not exist.")
        return

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if args.to == 'markdown':
        new_content = wiki_to_markdown(content)
        action_name = "Wiki to Markdown"
    else:
        new_content = markdown_to_wiki(content)
        action_name = "Markdown to Wiki"

    if content == new_content:
        print(f"No changes needed for {action_name}.")
        return

    if args.dry_run:
        print(f"[DRY RUN] Would convert {md_path} to {args.to}")
        # Print a small preview of changes
        print("--- Preview ---")
        diff_lines = []
        for old, new in zip(content.splitlines(), new_content.splitlines()):
            if old != new:
                print(f"OLD: {old}")
                print(f"NEW: {new}")
        print("---------------")
    else:
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Successfully converted {md_path} to {args.to}")

if __name__ == '__main__':
    main()
