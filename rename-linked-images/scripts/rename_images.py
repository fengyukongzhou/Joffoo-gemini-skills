import os
import re
import datetime
import argparse
from pathlib import Path
import urllib.parse

def extract_image_links(content):
    """Extract image links from markdown content."""
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
        try:
            name = urllib.parse.unquote(name)
        except:
            pass
        if name not in seen:
            links.append(name)
            seen.add(name)
            
    return links

def format_date(date_obj, date_format):
    """Format date according to specified format."""
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

def find_file_in_vault(filename, start_dir, vault_root=None):
    """
    Simulate Obsidian's link resolution.
    Search in start_dir, then common attachment folders, then vault_root.
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
    
    # 3. If vault_root is provided, search entire vault
    if vault_root:
        for root, dirs, files in os.walk(vault_root):
            if filename in files:
                return Path(root) / filename
            
    return None

def find_all_md_files(vault_root):
    """Find all markdown files in the vault."""
    md_files = []
    for root, dirs, files in os.walk(vault_root):
        # Skip .obsidian and other hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith('.md'):
                md_files.append(Path(root) / file)
    return md_files

def update_links_in_file(md_file, old_name, new_name):
    """
    Update all image links in a markdown file from old_name to new_name.
    Returns True if any changes were made.
    """
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {md_file}: {e}")
        return False
    
    original_content = content
    
    # WikiLink replacement: ![[old_name|alt]] -> ![[new_name|alt]]
    escaped_old = re.escape(old_name)
    wiki_pattern = rf'!\[\[({escaped_old})(?:\|([^\]]*))?\]\]'
    def wiki_sub(m):
        alt = m.group(2)
        return f'![[{new_name}|{alt}]]' if alt else f'![[{new_name}]]'
    content = re.sub(wiki_pattern, wiki_sub, content)
    
    # Markdown replacement: ![alt](old_name) -> ![alt](new_name)
    # Handle both literal and URL-encoded versions
    encoded_old = urllib.parse.quote(old_name)
    links_to_match = [re.escape(old_name)]
    if encoded_old != old_name:
        links_to_match.append(re.escape(encoded_old))
    
    md_pattern = rf'!\[([^\]]*)\]\(({"|".join(links_to_match)})\)'
    def md_sub(m):
        alt = m.group(1)
        encoded_new = urllib.parse.quote(new_name)
        return f'![{alt}]({encoded_new})'
    content = re.sub(md_pattern, md_sub, content)
    
    if content != original_content:
        try:
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing {md_file}: {e}")
            return False
    
    return False

def main():
    parser = argparse.ArgumentParser(description='Rename linked images in a Markdown file and update all references across the vault.')
    parser.add_argument('md_file', help='Path to the Markdown file')
    parser.add_argument('--prefix', default='img', help='Prefix for new filenames')
    parser.add_argument('--date-format', choices=['MMDD', 'DDMM', 'YYMMDD'], default='MMDD', help='Date format')
    parser.add_argument('--no-date', action='store_true', help='Disable date in filename')
    parser.add_argument('--start-index', type=int, default=1, help='Starting index for numbering')
    parser.add_argument('--pad-length', type=int, default=3, help='Padding length for index (e.g., 3 -> 001)')
    parser.add_argument('--dry-run', action='store_true', help='Print changes without applying them')
    parser.add_argument('--vault-root', help='Root directory of the Obsidian vault (for searching all references)')
    
    args = parser.parse_args()
    
    md_path = Path(args.md_file).resolve()
    if not md_path.exists():
        print(f"Error: {md_path} does not exist.")
        return

    # Determine vault root
    vault_root = args.vault_root
    if not vault_root:
        # Try to find .obsidian folder to determine vault root
        current = md_path.parent
        while current != current.parent:
            if (current / '.obsidian').exists():
                vault_root = current
                print(f"Detected vault root: {vault_root}")
                break
            current = current.parent
        
        if not vault_root:
            vault_root = md_path.parent
            print(f"No .obsidian folder found. Using markdown file directory as vault root: {vault_root}")

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    image_links = extract_image_links(content)
    if not image_links:
        print("No image links found.")
        return

    # Use file creation time for the date string (unless --no-date is specified)
    if args.no_date:
        date_str = ""
    else:
        stat = md_path.stat()
        ctime = datetime.datetime.fromtimestamp(stat.st_ctime)
        date_str = format_date(ctime, args.date_format)
    
    # Collect all files that will be renamed and their target directory
    files_to_rename = []
    target_dirs = set()
    
    for old_name in image_links:
        file_path = find_file_in_vault(old_name, md_path.parent, vault_root)
        if file_path:
            files_to_rename.append((old_name, file_path))
            target_dirs.add(file_path.parent)
    
    if not files_to_rename:
        print("No files to rename.")
        return
    
    # First pass: identify which files already have the correct naming pattern
    # and extract their indices
    used_indices = set()  # Indices already used by files in correct format
    files_needing_rename = []  # Files that need to be renamed
    
    for old_name, file_path in files_to_rename:
        ext = file_path.suffix
        current_name = file_path.name
        
        # Check if current filename matches the target pattern: prefix-XXX.ext
        pattern = rf"^{re.escape(args.prefix)}(\d{{{args.pad_length}}}){re.escape(ext)}$"
        match = re.match(pattern, current_name)
        if match:
            # File already has the correct format, record its index
            idx = int(match.group(1))
            used_indices.add(idx)
        else:
            # File needs to be renamed
            files_needing_rename.append((old_name, file_path))
    
    # Second pass: assign new names to files that need renaming
    mapping = {}
    index = args.start_index
    
    for old_name, file_path in files_needing_rename:
        ext = file_path.suffix
        
        # Find the next available index that's not used by existing correctly-named files
        while index in used_indices:
            index += 1
        
        new_name = f"{args.prefix}{date_str}-{str(index).zfill(args.pad_length)}{ext}"
        new_path = file_path.parent / new_name
        
        mapping[old_name] = (new_name, file_path, new_path)
        used_indices.add(index)
        index += 1

    if not mapping:
        print("No files to rename.")
        return

    print(f"Found {len(mapping)} images to rename.")
    
    # 1. Rename files
    renamed_count = 0
    renamed_mappings = {}  # Track successful renames: old_name -> new_name
    
    for old_link, (new_name, old_file, new_file) in mapping.items():
        if old_file.name == new_name:
            print(f"Skipping {old_link} (already named correctly)")
            continue
            
        if args.dry_run:
            print(f"[DRY RUN] Rename: {old_file} -> {new_file}")
            renamed_mappings[old_link] = new_name
            renamed_count += 1
        else:
            try:
                if new_file.exists():
                    print(f"Warning: Destination {new_file} already exists. Skipping.")
                    continue
                old_file.rename(new_file)
                print(f"Renamed: {old_file.name} -> {new_name}")
                renamed_mappings[old_link] = new_name
                renamed_count += 1
            except Exception as e:
                print(f"Error renaming {old_file}: {e}")

    # 2. Update ALL markdown files in the vault that reference these images
    if renamed_count > 0:
        print(f"\nUpdating references across the vault...")
        
        all_md_files = find_all_md_files(vault_root)
        print(f"Found {len(all_md_files)} markdown files in vault.")
        
        updated_files = []
        
        for md_file in all_md_files:
            file_updated = False
            for old_name, new_name in renamed_mappings.items():
                if args.dry_run:
                    # In dry-run mode, just check if file would be updated without actually modifying it
                    try:
                        with open(md_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        # Check if old_name appears in content
                        escaped_old = re.escape(old_name)
                        wiki_pattern = rf'!\[\[({escaped_old})(?:\|([^\]]*))?\]\]'
                        md_pattern = rf'!\[([^\]]*)\]\(({re.escape(old_name)}|{re.escape(urllib.parse.quote(old_name))})\)'
                        if re.search(wiki_pattern, content) or re.search(md_pattern, content):
                            file_updated = True
                    except Exception as e:
                        pass
                else:
                    if update_links_in_file(md_file, old_name, new_name):
                        file_updated = True
            if file_updated:
                updated_files.append(md_file)
                if args.dry_run:
                    print(f"[DRY RUN] Would update: {md_file}")
                else:
                    print(f"Updated: {md_file}")
        
        if args.dry_run:
            print(f"\n[DRY RUN] Would update {len(updated_files)} files.")
        else:
            print(f"\nSuccessfully updated {len(updated_files)} files.")
            
        # Also update the original file (in case it wasn't in the vault search)
        if not args.dry_run and md_path not in updated_files:
            for old_name, new_name in renamed_mappings.items():
                update_links_in_file(md_path, old_name, new_name)
            print(f"Updated original file: {md_path}")

if __name__ == '__main__':
    main()
