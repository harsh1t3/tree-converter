"""
tree_converter.py

- Paste or provide an ASCII tree (or use --sample or an input file)
- After you finish pasting, a native folder-selection popup appears
  so the user chooses where to create the structure.
- Supports --dry-run to preview without creating files/folders.
- Preserves comments (lines with #) and writes them into generated files.
"""

import os
import re
import argparse
import subprocess
import platform
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Try to import tkinter for the folder chooser. If unavailable,
# we'll fall back to asking the user to type a path.
try:
    import tkinter as tk
    from tkinter import filedialog
    TK_AVAILABLE = True
except Exception:
    TK_AVAILABLE = False


class TreeParser:
    """Parses an ASCII tree string into a nested structure (list/dicts)."""
    def parse_tree_from_string(self, tree_string: str) -> List[Dict]:
        lines = [line for line in tree_string.splitlines() if line.strip() != '']
        structure: List[Dict] = []
        # stack holds dicts: {'level': int, 'path': str, 'children': list}
        stack = [{'level': -1, 'path': '', 'children': structure}]

        root_name = 'my-project'
        if lines and not re.match(r'^[\s│├└─]+', lines[0]):
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
            level += 1  # account for root level

            # pop until we find the parent level
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

        # detect indent tokens (box-drawing or spaces)
        indent_match = re.match(r'^([│├└─\s]+)', line)
        indent = indent_match.group(1) if indent_match else ''
        # Heuristic for level: count occurrences of common indent characters
        level = indent.count('│') + indent.count('    ') + indent.count('├') + indent.count('└')

        # split out inline comment
        if '#' in line:
            line_content, comment = line.split('#', 1)
        else:
            line_content, comment = line, ''

        name = re.sub(r'^[│├└─\s]+', '', line_content).strip().rstrip('/')
        if not name:
            return None

        is_file = '.' in name and not name.endswith('/')
        return level, name, is_file, comment.strip()


class FolderCreator:
    """Creates folders and files from the parsed structure."""
    def __init__(self, base_path: str = '.', dry_run: bool = False):
        self.base_path = Path(base_path).resolve()
        self.dry_run = dry_run

    def create_structure(self, structure: List[Dict], current_path: Optional[Path] = None):
        current_path = current_path or self.base_path
        for item in structure:
            full_path = current_path / item['name']
            if item['is_file']:
                self._create_file(full_path, item)
            else:
                if not self.dry_run:
                    full_path.mkdir(parents=True, exist_ok=True)
                # recurse into children
                self.create_structure(item['children'], full_path)

    def _create_file(self, full_path: Path, item: Dict):
        # Ensure parent exists
        if not self.dry_run:
            full_path.parent.mkdir(parents=True, exist_ok=True)

        # Build content: include comment as first line if present
        comment = f"# {item['comment']}\n" if item.get('comment') else ''
        content = f"{comment}# {item['name']}\nAuto-generated file\n"

        if self.dry_run:
            print(f"[DRY RUN] Would create file: {full_path}")
            print(f"[DRY RUN] Content:\n{content}")
        else:
            # Only write if file doesn't exist to avoid clobbering
            if not full_path.exists():
                full_path.write_text(content)
            else:
                # if file exists, do not overwrite; optionally you can change this behavior
                pass


def print_structure(structure: List[Dict], indent: str = ''):
    for i, item in enumerate(structure):
        is_last = (i == len(structure) - 1)
        prefix = '└── ' if is_last else '├── '
        icon = '📄' if item['is_file'] else '📁'
        print(f"{indent}{prefix}{icon} {item['name']}" + (f"  # {item['comment']}" if item['comment'] else ''))
        if item['children']:
            new_indent = indent + ('    ' if is_last else '│   ')
            print_structure(item['children'], new_indent)


def open_folder(path: Path):
    """Open folder in file explorer depending on OS."""
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", str(path)])
        else:  # assume linux
            subprocess.run(["xdg-open", str(path)])
    except Exception as e:
        print(f"⚠️ Could not open folder automatically: {e}")


def choose_output_folder_popup(title: str = "Select folder where project should be created") -> Optional[Path]:
    """
    Show a native folder choose dialog and return the selected Path.
    Returns None if cancelled or if tkinter is not available.
    """
    if not TK_AVAILABLE:
        return None

    # Enable DPI awareness for Windows to fix blurry rendering
    if platform.system() == "Windows":
        try:
            from ctypes import windll
            # Try to set DPI awareness (Windows 8.1+)
            try:
                windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
            except Exception:
                try:
                    windll.user32.SetProcessDPIAware()  # Fallback for older Windows
                except Exception:
                    pass
        except Exception:
            pass

    # Build a small, hidden root and bring the dialog to front
    root = tk.Tk()
    root.withdraw()
    
    # Additional DPI scaling for tkinter itself
    try:
        root.tk.call('tk', 'scaling', 2.0)  # Adjust scaling if needed
    except Exception:
        pass
    
    # Try to ensure the dialog is on top
    try:
        root.attributes('-topmost', True)
    except Exception:
        pass

    selected = filedialog.askdirectory(title=title)
    root.destroy()
    if not selected:
        return None
    return Path(selected)


def choose_output_folder_fallback() -> Optional[Path]:
    """Fallback: prompt user to type a folder path in terminal."""
    try:
        typed = input("Type full path of destination folder (or leave blank to cancel): ").strip()
    except EOFError:
        return None
    if not typed:
        return None
    return Path(typed).expanduser().resolve()


def main():
    parser = argparse.ArgumentParser(description="ASCII Tree to Folder Structure Converter")
    parser.add_argument('input_file', nargs='?', help='Input tree file (optional)')
    parser.add_argument('--sample', action='store_true', help='Use a sample tree')
    parser.add_argument('--dry-run', action='store_true', help='Preview structure without creating it')
    args = parser.parse_args()

    # Step 1: get tree string (sample / file / paste)
    if args.sample:
        tree_string = """my-project
├── README.md # Project overview
├── src
│   ├── main.py # Entry point
│   └── utils.py # Helper functions
└── tests
    └── test_main.py # Unit tests"""
    elif args.input_file:
        tree_string = Path(args.input_file).read_text(encoding='utf-8')
    else:
        print("📋 Paste your folder tree structure below. Press ENTER on an empty line to finish:")
        lines: List[str] = []
        while True:
            try:
                line = input()
            except EOFError:
                break
            # stop when the user presses enter on an empty line after entering at least one line
            if line.strip() == "" and len(lines) > 0:
                break
            lines.append(line)
        tree_string = "\n".join(lines)

    # Parse the tree into internal structure
    parser = TreeParser()
    try:
        structure = parser.parse_tree_from_string(tree_string)
    except Exception as e:
        print(f"❌ Error parsing tree: {e}")
        return

    # If dry-run requested, show structure and ask where (optional)
    if args.dry_run:
        print("\n📋 DRY RUN: Structure to be created (preview):")
        print_structure(structure)
        # still ask where to save for clarity but do not create files
        print("\n📁 Please choose where you'd create this (DRY RUN) — dialog will open now.")
    else:
        print("\n📁 Please choose where you want to create this folder structure — dialog will open now.")

    # Step 2: open popup AFTER paste/parse
    selected_path = choose_output_folder_popup()
    if selected_path is None:
        # popup not available or user cancelled; fall back to typing path
        if TK_AVAILABLE:
            # user cancelled dialog
            print("❌ No folder selected. Operation cancelled.")
            return
        else:
            print("⚠️ tkinter not available — please type the destination folder path.")
            selected_path = choose_output_folder_fallback()
            if not selected_path:
                print("❌ No folder provided. Exiting.")
                return

    # Build the final output directory: selected_path / root_name
    root_name = structure[0]['name'] if structure else 'my-project'
    final_output_dir = selected_path / root_name

    # If dry-run: show final path and don't create
    if args.dry_run:
        print("\n📁 DRY RUN Target Path:")
        print(final_output_dir)
        print("\nPreview of tree:")
        print_structure(structure)
        return

    # Step 3: create the structure
    try:
        creator = FolderCreator(selected_path, dry_run=False)
        creator.create_structure(structure)
    except Exception as e:
        print(f"❌ Error creating files/folders: {e}")
        return

    # Step 4: confirmation + open folder
    print(f"\n✅ Structure created in: {final_output_dir.resolve()}")
    # Attempt to open; if it fails, still show path
    try:
        open_folder(final_output_dir)
    except Exception:
        pass


if __name__ == '__main__':
    main()
