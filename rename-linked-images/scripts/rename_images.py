import os
import re
import datetime
import argparse
from pathlib import Path

def extract_image_links(content):
    # Obsidian WikiLinks: ![[image.png|alt]]
    obsidian_regex = r'!\[\[([^\]|#]+)(?:\|[^\]]*)?\]\]'
    # Markdown Links: ![alt](image.png)
    markdown_regex = r'!\[[^\]]*\]\(([^)\s]+?)\)'
    
    links = []
    seen = set()
    
    for match in re.finditer(obsidian_regex, content):
        name = match.group(1).strip()
        if name not in seen:
            links.append(name)
            seen.add(name)
            
    for match in re.finditer(markdown_regex, content):
        name = match.group(1).strip()
        # Decode URL encoding if present
        import urllib.parse
        try:
            name = urllib.parse.unquote(name)
        except:
            pass
        if name not in seen:
            links.append(name)
            seen.add(name)
            
    return links

def format_date(date_obj, date_format):
    if not date_format:
        return ""
    
    month = f"{date_obj.month:02d}"
    day = f"{date_obj.day:02d}"
    year_short = str(date_obj.year)[2:]
    
    if date_format == 'YYMMDD':
        return f"{year_short}{month}{day}"
    elif date_format == 'DDMM':
        return f"{day}{month}"
    else: # MMDD default
        return f"{month}{day}"

def find_file_in_vault(filename, start_dir):
    """
    Simulate Obsidian's link resolution.
    """
    # 1. Try relative to start_dir
    potential_path = Path(start_dir) / filename
    if potential_path.exists():
        return potential_path
    
    # 2. Try common names in the SAME directory and UP one level
    search_dirs = [Path(start_dir), Path(start_dir).parent]
    for base_dir in search_dirs:
        for folder in ['_attachments', 'assets', 'attachments', 'Attachments']:
            p = base_dir / folder / filename
            if p.exists():
                return p
            
    return None

def main():
    parser = argparse.ArgumentParser(description='Rename linked images in a Markdown file.')
    parser.add_argument('md_file', help='Path to the Markdown file')
    parser.add_argument('--prefix', default='img', help='Prefix for new filenames')
    parser.add_argument('--date-format', choices=['MMDD', 'DDMM', 'YYMMDD'], default='MMDD', help='Date format')
    parser.add_argument('--start-index', type=int, default=1, help='Starting index for numbering')
    parser.add_argument('--pad-length', type=int, default=3, help='Padding length for index (e.g., 3 -> 001)')
    parser.add_argument('--dry-run', action='store_true', help='Print changes without applying them')
    
    args = parser.parse_args()
    
    md_path = Path(args.md_file).resolve()
    if not md_path.exists():
        print(f"Error: {md_path} does not exist.")
        return

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    image_links = extract_image_links(content)
    if not image_links:
        print("No image links found.")
        return

    # Use file creation time for the date string
    stat = md_path.stat()
    ctime = datetime.datetime.fromtimestamp(stat.st_ctime)
    date_str = format_date(ctime, args.date_format)
    
    mapping = {}
    index = args.start_index
    
    for old_name in image_links:
        # Find the actual file
        file_path = find_file_in_vault(old_name, md_path.parent)
        if not file_path:
            print(f"Warning: Could not find file for link '{old_name}'")
            continue
            
        ext = file_path.suffix
        new_name = f"{args.prefix}{date_str}-{str(index).zfill(args.pad_length)}{ext}"
        new_path = file_path.parent / new_name
        
        mapping[old_name] = (new_name, file_path, new_path)
        index += 1

    if not mapping:
        print("No files to rename.")
        return

    print(f"Found {len(mapping)} images to rename.")
    
    # 1. Rename files
    renamed_count = 0
    for old_link, (new_name, old_file, new_file) in mapping.items():
        if old_file.name == new_name:
            print(f"Skipping {old_link} (already named correctly)")
            continue
            
        if args.dry_run:
            print(f"[DRY RUN] Rename: {old_file} -> {new_file}")
            renamed_count += 1
        else:
            try:
                if new_file.exists():
                    print(f"Warning: Destination {new_file} already exists. Skipping.")
                    continue
                old_file.rename(new_file)
                print(f"Renamed: {old_file.name} -> {new_name}")
                renamed_count += 1
            except Exception as e:
                print(f"Error renaming {old_file}: {e}")

    # 2. Update Markdown content
    if renamed_count > 0:
        import urllib.parse
        new_content = content
        for old_link, (new_name, _, _) in mapping.items():
            # WikiLink replacement
            escaped_old_wiki = re.escape(old_link)
            wiki_pattern = rf'!\[\[({escaped_old_wiki})(?:\|([^\]]*))?\]\]'
            def wiki_sub(m):
                alt = m.group(2)
                return f'![[{new_name}|{alt}]]' if alt else f'![[{new_name}]]'
            new_content = re.sub(wiki_pattern, wiki_sub, new_content)
            
            # Markdown replacement (needs to handle both literal and encoded)
            encoded_old = urllib.parse.quote(old_link)
            # Match either the literal name or the encoded name
            links_to_match = [re.escape(old_link)]
            if encoded_old != old_link:
                links_to_match.append(re.escape(encoded_old))
            
            md_pattern = rf'!\[([^\]]*)\]\(({"|".join(links_to_match)})\)'
            def md_sub(m):
                alt = m.group(1)
                encoded_new = urllib.parse.quote(new_name)
                return f'![{alt}]({encoded_new})'
            new_content = re.sub(md_pattern, md_sub, new_content)

        if not args.dry_run:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated Markdown file: {md_path}")
        else:
            print(f"[DRY RUN] Would update Markdown file: {md_path}")


if __name__ == '__main__':
    main()
