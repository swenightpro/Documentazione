import os
import re
import json
from datetime import datetime
from collections import defaultdict

FIELD_SEPARATOR = re.compile(r'[ _]+')
VERSION_TOKEN = re.compile(r'^v(\d+(?:\.\d+){0,2})$', re.IGNORECASE)
SIGNED_TOKEN = re.compile(r'^(firmato|signed)$', re.IGNORECASE)
DATE_TOKEN = re.compile(r'^\d{4}-\d{2}-\d{2}$')

class Item:
    def __init__(self, val):
        self.val = val
        
    def __gt__(self, other):
        if self.val["type"] == 'folder':
            if other.val["type"] == 'folder':
                weights = {"documentazione esterna": 2, "documentazione interna": 1}
                s_weight = weights.get(self.val["name"].lower(), 0)
                o_weight = weights.get(other.val["name"].lower(), 0)
                
                if s_weight != o_weight:
                    return s_weight > o_weight
                return self.val["name"].lower() > other.val["name"].lower()
            return False
        if other.val["type"] == 'folder': return True
        if self.val["date"]:
            if other.val["date"]:
                return datetime.strptime(self.val["date"], "%Y-%m-%d") > datetime.strptime(other.val["date"], "%Y-%m-%d")
            return True
        if other.val["date"]: return False
        return self.val["name"].lower() > other.val["name"].lower()
    
    def __repr__(self):
        return self.val["name"]

def normalize_text(s):
    return s.encode('ascii', 'ignore').decode()

def sorting(children):
    ch = [Item(i) for i in children]
    return list(map(lambda i: i.val, sorted(ch, reverse=True)))

def parse_version(version):
    if not version:
        return (0, 0, 0)
    m = re.search(r'^(?:v)?(\d+)(?:\.(\d+))?(?:\.(\d+))?$', version, re.IGNORECASE)
    if not m:
        return (0, 0, 0)
    major = int(m.group(1))
    minor = int(m.group(2)) if m.group(2) else 0
    patch = int(m.group(3)) if m.group(3) else 0
    return (major, minor, patch)

def parse_date(date_str):
    if not date_str:
        return (0, 0, 0)
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return (dt.year, dt.month, dt.day)
    except ValueError:
        return (0, 0, 0)

def stable_sort_key(entry):
    # Priorita: versione piu alta, poi data piu recente, poi firmato.
    return (
        parse_version(entry.get('version')),
        parse_date(entry.get('date')),
        1 if entry.get('signed') else 0,
        entry.get('path', '').lower(),
    )

def normalize_date_token(token):
    if not token or not DATE_TOKEN.match(token):
        return None
    try:
        dt = datetime.strptime(token, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None

def split_name_tokens(name):
    return [t for t in FIELD_SEPARATOR.split(name.strip()) if t]

def iter_pdf_walk(directory):
    for root, dirs, files in os.walk(directory, topdown=True):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        pdf_files = [f for f in files if f.lower().endswith('.pdf') and not f.startswith('.')]
        yield root, os.path.relpath(root, directory), dirs, pdf_files

def doc_relative_path(relative_path, filename):
    if relative_path == '.':
        return filename
    return f"{relative_path.replace(os.sep, '/')}/{filename}"

def doc_web_path(directory, relative_path, filename):
    docs_root = os.path.basename(os.path.normpath(directory))
    return f"./{docs_root}/{doc_relative_path(relative_path, filename)}"

def estrai_info(filename):
    name_no_ext = os.path.splitext(filename)[0].strip()
    tokens = split_name_tokens(name_no_ext)

    signed = False
    version = None
    date = None

    # Parsing da destra: [nome] [data] [versione] [firma]
    if tokens and SIGNED_TOKEN.match(tokens[-1]):
        signed = True
        tokens = tokens[:-1]

    if tokens:
        version_match = VERSION_TOKEN.match(tokens[-1])
        if version_match:
            version = f"v{version_match.group(1)}"
            tokens = tokens[:-1]

    if tokens:
        maybe_date = normalize_date_token(tokens[-1])
        if maybe_date:
            date = maybe_date
            tokens = tokens[:-1]

    clean_base = " ".join(tokens).strip() or name_no_ext
    clean_name = normalize_text(clean_base.title())

    parts = [clean_name]
    if version: parts.append(version)
    if date: parts.append(date)
    if signed: parts.append("firmato")
    search_name = " ".join(parts).lower()

    return clean_name, version, date, signed, search_name

def make_tree_entry(directory, relative_path, filename):
    clean_name, version, date, signed, search_name = estrai_info(filename)
    return {
        'type': 'file',
        'name': clean_name,
        'version': version,
        'date': date,
        'signed': signed,
        'path': doc_web_path(directory, relative_path, filename),
        'search_name': search_name,
    }

def build_file_tree(directory):
    tree_root = {}

    for root, relative_path, dirs, files in iter_pdf_walk(directory):
        
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
            entry = make_tree_entry(directory, relative_path, file)
            base_key = (
                re.sub(r'[\s_]+', '', entry['name']).lower(),
                entry['date'] or '',
                entry['version'] or ''
            )

            if base_key not in base_files:
                base_files[base_key] = {'normal': None, 'signed': None}
            if entry['signed']:
                base_files[base_key]['signed'] = entry
            else:
                base_files[base_key]['normal'] = entry

        for variants in base_files.values():
            entry = variants['signed'] or variants['normal']
            if not entry:
                continue
            current['children'].append(entry)
            
        current['children'] = sorting(current['children'])

    return {k: sorting(v['children']) for k, v in tree_root.items()}


def build_stable_links(directory):
    groups = defaultdict(list)

    for _root, rel_dir, _dirs, files in iter_pdf_walk(directory):

        for file in files:
            clean_name, version, date, signed, _search_name = estrai_info(file)
            if not version:
                continue

            file_rel = doc_relative_path(rel_dir, file)
            groups[(rel_dir, clean_name, date)].append({
                'name': clean_name,
                'version': version,
                'date': date,
                'signed': signed,
                'path': file_rel,
            })

    stable_links = {}
    for (rel_dir, clean_name, date), entries in groups.items():
        if not entries:
            continue

        best = max(entries, key=stable_sort_key)

        stable_name = clean_name
        if date:
            stable_name = f"{stable_name} {date}"
        stable_filename = re.sub(r'\s+', '_', stable_name) + '.pdf'
        prefix = '' if rel_dir == '.' else rel_dir.replace(os.sep, '/') + '/'
        stable_path = prefix + stable_filename

        if stable_path != best['path']:
            stable_links[stable_path] = best['path']

    return stable_links


if __name__ == "__main__":
    directory_docs = '../docs'
    output = './docs_tree.json'
    output_stable = './stable_links.json'

    tree_ = build_file_tree(directory_docs)
    tree = {root: tree_[root] for root in ["PB", "RTB", "Candidatura"] if root in tree_}
    
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(tree, f, indent=2, ensure_ascii=False)

    stable = build_stable_links(directory_docs)
    with open(output_stable, 'w', encoding='utf-8') as f:
        json.dump(stable, f, indent=2, ensure_ascii=False)


