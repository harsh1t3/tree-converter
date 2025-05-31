import os
import re
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


class TreeParser:
    def parse_tree_from_string(self, tree_string: str) -> List[Dict]:
        lines = [line for line in tree_string.splitlines() if line.strip()]
        structure = []
        stack = [{'level': -1, 'path': '', 'children': structure}]

        root_name = 'my-project'
        if lines and not re.match(r'^[\s\u2502\u251c\u2514\u2500]+', lines[0]):
            root_name = lines[0].strip().rstrip('/')
            lines = lines[1:]

        root = {
            'name': root_name,
            'path': root_name,
            'is_file': False,
            'level': 0,
            'children': [],
            'comment': ''
        }
        structure.append(root)
        stack.append({'level': 0, 'path': root_name, 'children': root['children']})

        for line in lines:
            result = self._process_line(line)
            if result is None:
                continue
            level, name, is_file, comment = result
            level += 1  # for root level

            while len(stack) > 1 and stack[-1]['level'] >= level:
                stack.pop()

            parent = stack[-1]
            path = os.path.join(parent['path'], name).replace('\\', '/')

            node = {
                'name': name,
                'path': path,
                'is_file': is_file,
                'level': level,
                'children': [],
                'comment': comment
            }
            parent['children'].append(node)

            if not is_file:
                stack.append({'level': level, 'path': path, 'children': node['children']})

        return structure

    def _process_line(self, line: str) -> Optional[Tuple[int, str, bool, str]]:
        if not line.strip():
            return None

        indent_match = re.match(r'^([\u2502\u251c\u2514\u2500\s]+)', line)
        indent = indent_match.group(1) if indent_match else ''
        level = indent.count('│') + indent.count('    ') + indent.count('├') + indent.count('└')

        if '#' in line:
            line_content, comment = line.split('#', 1)
        else:
            line_content, comment = line, ''

        name = re.sub(r'^[\u2502\u251c\u2514\u2500\s]+', '', line_content).strip().rstrip('/')
        if not name:
            return None

        is_file = '.' in name and not name.endswith('/')
        return level, name, is_file, comment.strip()


class FolderCreator:
    def __init__(self, base_path: str = '.', dry_run: bool = False):
        self.base_path = Path(base_path).resolve()
        self.dry_run = dry_run

    def create_structure(self, structure: List[Dict], current_path: Optional[Path] = None):
        current_path = current_path or self.base_path
        for item in structure:
            full_path = current_path / item['name']
            try:
                if item['is_file']:
                    self._create_file(full_path, item)
                else:
                    if not self.dry_run:
                        full_path.mkdir(parents=True, exist_ok=True)
                    self.create_structure(item['children'], full_path)
            except Exception as e:
                logging.error(f"Failed to create {'file' if item['is_file'] else 'directory'} '{full_path}': {e}")

    def _create_file(self, full_path: Path, item: Dict):
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            comment = f"# {item['comment']}\n" if item['comment'] else ''
            content = f"{comment}# {item['name']}\nAuto-generated file\n"

            if not self.dry_run:
                if not full_path.exists():
                    full_path.write_text(content)
            else:
                logging.info(f"[DRY RUN] Would create file: {full_path}")
                logging.info(f"[DRY RUN] Content:\n{content}")
        except Exception as e:
            logging.error(f"Could not write file '{full_path}': {e}")


def print_structure(structure: List[Dict], indent: str = ''):
    for i, item in enumerate(structure):
        is_last = (i == len(structure) - 1)
        prefix = '└── ' if is_last else '├── '
        icon = '📄' if item['is_file'] else '📁'
        print(f"{indent}{prefix}{icon} {item['name']}" + (f"  # {item['comment']}" if item['comment'] else ''))
        if item['children']:
            new_indent = indent + ('    ' if is_last else '│   ')
            print_structure(item['children'], new_indent)


def main():
    parser = argparse.ArgumentParser(description="ASCII Tree to Folder Structure Converter")
    parser.add_argument('input_file', nargs='?', help='Input tree file')
    parser.add_argument('output_dir', nargs='?', default='.', help='Output directory')
    parser.add_argument('--sample', action='store_true', help='Use a sample tree')
    parser.add_argument('--dry-run', action='store_true', help='Preview structure without creating it')
    parser.add_argument('--root-name', type=str, help='Override root project folder name')
    args = parser.parse_args()

    if args.sample:
        tree_string = """my-project
├── README.md # Project overview
├── src
│   ├── main.py # Entry point
│   └── utils.py # Helper functions
└── tests
    └── test_main.py # Unit tests"""
    elif args.input_file:
        try:
            tree_string = Path(args.input_file).read_text(encoding='utf-8')
        except Exception as e:
            logging.error(f"Failed to read input file: {e}")
            return
    else:
        print("Paste your tree (end with blank line):")
        lines = []
        while True:
            try:
                line = input()
                if not line.strip():
                    break
                lines.append(line)
            except EOFError:
                break
        tree_string = '\n'.join(lines)

    tree_parser = TreeParser()
    tree = tree_parser.parse_tree_from_string(tree_string)

    if args.root_name:
        tree[0]['name'] = args.root_name
        tree[0]['path'] = args.root_name

    if args.dry_run:
        print("📋 DRY RUN: Structure to be created")
        print_structure(tree)
    else:
        FolderCreator(args.output_dir, dry_run=False).create_structure(tree)
        print(f"\n✅ Structure created in: {Path(args.output_dir).resolve()}")


if __name__ == '__main__':
    main()
