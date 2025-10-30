import os
import re
import json
from datetime import datetime

def normalize_text(s):
    return s.encode('ascii', 'ignore').decode()

def estrai_info(filename):
    name_no_ext = os.path.splitext(filename)[0]
    normalized = name_no_ext.strip()
    normalized = re.sub(r'_+', ' ', normalized)
    normalized = re.sub(r'\s+', ' ', normalized)

    signed = bool(re.search(r'(firmato|signed)', normalized, re.IGNORECASE))
    normalized = re.sub(r'(?i)(?:[\s_\-\.]*)(firmato|signed)(?:[\s_\-\.]*)$', ' ', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()

    version_match = re.search(r'v\s?(\d+(?:\.\d+){0,2})', normalized, re.IGNORECASE)
    version = f"v{version_match.group(1)}" if version_match else None
    if version:
        normalized = re.sub(r'v\s?\d+(?:\.\d+){0,2}', ' ', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'\s+', ' ', normalized).strip()

    date_match = re.search(r'\b(\d{2})[-_/](\d{2})[-_/](\d{2,4})\b', normalized)
    if date_match:
        raw_date = date_match.group(0)
        normalized = normalized.replace(raw_date, ' ')
        day, month, year = date_match.groups()
        if len(year) == 2:
            year = ("20" + year) if int(year) < 50 else ("19" + year)
        try:
            date = f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
        except ValueError:
            date = None
        normalized = re.sub(r'\s+', ' ', normalized).strip()
    else:
        date = None

    clean_name = normalize_text(normalized.strip().title())

    parts = [clean_name]
    if version: parts.append(version)
    if date: parts.append(date)
    if signed: parts.append("firmato")
    search_name = " ".join(parts).lower()

    return clean_name, version, date, signed, search_name

def build_file_tree(directory):
    tree_root = {}

    for root, dirs, files in os.walk(directory, topdown=True):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        files = [f for f in files if f.lower().endswith('.pdf') and not f.startswith('.')]

        relative_path = os.path.relpath(root, directory)
        if relative_path == '.':
            for d in dirs:
                if d not in tree_root:
                    tree_root[d] = {'type': 'folder', 'name': d, 'children': []}
            continue

        parts = relative_path.split(os.sep)
        current = tree_root.setdefault(parts[0], {'type': 'folder', 'name': parts[0], 'children': []})

        for part in parts[1:]:
            found = next((x for x in current['children'] if x['type'] == 'folder' and x['name'] == part), None)
            if not found:
                found = {'type': 'folder', 'name': part, 'children': []}
                current['children'].append(found)
            current = found

        base_files = {}
        for file in files:
            base_key = os.path.splitext(file)[0]
            base_key = re.sub(r'(?i)(?:[\s_\-\.]*)(firmato|signed)$', '', base_key)
            base_key = re.sub(r'[\s_]+', '', base_key).lower()

            clean_name, version, date, signed, search_name = estrai_info(file)

            if base_key not in base_files:
                base_files[base_key] = {'normal': None, 'signed': None}
            if signed:
                base_files[base_key]['signed'] = (file, clean_name, version, date, signed, search_name)
            else:
                base_files[base_key]['normal'] = (file, clean_name, version, date, signed, search_name)

        for base_name, variants in base_files.items():
            entry = variants['signed'] or variants['normal']
            if not entry:
                continue
            file, clean_name, version, date, signed, search_name = entry
            web_path = f'./{os.path.join(root, file).replace(os.sep, "/").lstrip("../")}'
            current['children'].append({
                'type': 'file',
                'name': clean_name,
                'version': version,
                'date': date,
                'signed': signed,
                'path': web_path,
                'search_name': search_name
            })

    return {k: v['children'] for k, v in tree_root.items()}

if __name__ == "__main__":
    directory_docs = '../docs'
    output = './docs_tree.json'

    tree = build_file_tree(directory_docs)
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(tree, f, indent=2, ensure_ascii=False)
