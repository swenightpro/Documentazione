import json
import os
import shutil


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    stable_links_path = os.path.join(base_dir, 'stable_links.json')
    docs_dir = os.path.join(base_dir, 'docs')

    with open(stable_links_path, encoding='utf-8') as f:
        links = json.load(f)

    for stable, actual in links.items():
        src = os.path.join(docs_dir, actual)
        dst = os.path.join(docs_dir, stable)
        parent = os.path.dirname(dst)
        if parent:
            os.makedirs(parent, exist_ok=True)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"  {stable} -> {actual}")
        else:
            print(f"  MISSING: {src}")


if __name__ == '__main__':
    main()
