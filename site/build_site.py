import os
import re
import json

def estrai_versione(filename):
    match = re.search(r'v(\d+\.\d+(?:\.\d+)?)(?=[\s_\-]*(firmato|signed)?$)', filename, re.IGNORECASE)
    if match:
        return f"v{match.group(1)}"
    return None


def build_file_tree(directory):
    tree_root_dict = {}

    for root, dirs, files in os.walk(directory, topdown=True):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        files = [f for f in files if not f.startswith('.') and f.lower().endswith('.pdf')]

        relative_path = os.path.relpath(root, directory)
        if relative_path == '.':
            for d in dirs:
                if d not in tree_root_dict:
                    tree_root_dict[d] = {'type': 'folder', 'name': d, 'children': []}
            continue
        else:
            root_folder_name = relative_path.split(os.sep)[0]
            if root_folder_name not in tree_root_dict:
                tree_root_dict[root_folder_name] = {'type': 'folder', 'name': root_folder_name, 'children': []}

            parts = relative_path.split(os.sep)
            current_folder_dict = tree_root_dict[parts[0]]

            for part in parts[1:]:
                found_folder = next(
                    (i for i in current_folder_dict['children'] if i['type'] == 'folder' and i['name'] == part),
                    None
                )
                if not found_folder:
                    found_folder = {'type': 'folder', 'name': part, 'children': []}
                    current_folder_dict['children'].append(found_folder)
                current_folder_dict = found_folder

        base_files = {}

        for file in files:
            name_no_ext = os.path.splitext(file)[0]

            base_name = re.sub(r'[\s_\-]*(firmato|signed)$', '', name_no_ext, flags=re.IGNORECASE)

            if base_name not in base_files:
                base_files[base_name] = {'normal': None, 'signed': None}

            if re.search(r'[\s_\-](firmato|signed)$', name_no_ext, re.IGNORECASE):
                base_files[base_name]['signed'] = file
            else:
                base_files[base_name]['normal'] = file

        children_list_to_add_files = current_folder_dict.setdefault('children', [])

        for base_name, variants in base_files.items():
            chosen_file = variants['signed'] or variants['normal']
            if not chosen_file:
                continue

            pdf_path = os.path.join(root, chosen_file)
            clean_name = base_name.replace('_', ' ').replace('-', ' ')
            web_path = f'./{pdf_path.replace(os.sep, "/").lstrip("../")}'

            file_data = {
                'type': 'file',
                'name': clean_name.strip(),
                'path': web_path,
                'version': estrai_versione(base_name),
                'signed': bool(variants['signed'])
            }
            children_list_to_add_files.append(file_data)

    final_tree = {}
    for key, value in tree_root_dict.items():
        if value['type'] == 'folder':
            final_tree[key] = value['children']

    return final_tree


if __name__ == "__main__":
    directory_docs = '../docs'
    output_json_file = './docs_tree.json'

    print(f"Avvio scansione della cartella: {directory_docs}")
    file_tree = build_file_tree(directory_docs)

    try:
        with open(output_json_file, 'w', encoding='utf-8') as f:
            json.dump(file_tree, f, indent=2, ensure_ascii=False)
        print(f"\nAlbero dei file salvato con successo in: {output_json_file}")
    except Exception as e:
        print(f"\nErrore durante la scrittura del file JSON: {e}")
