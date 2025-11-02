# ASCII Tree to Folder Structure Converter

A Python utility that converts ASCII tree representations into actual folder and file structures on your filesystem. Features a native folder selection dialog for easy directory creation.

## Features

- Convert ASCII tree diagrams to real directory structures
- Native folder selection popup (cross-platform)
- Support for inline comments in tree format (preserved in generated files)
- Dry-run mode to preview structure before creation
- Cross-platform compatibility (Windows, macOS, Linux)
- Handles nested directories and files automatically
- Smart file detection (files have extensions, folders don't)
- Auto-opens created folder in file explorer

## Installation

Clone this repository:

```bash
git clone https://github.com/harsh1t3/tree-converter.git
cd tree-converter
```

No additional dependencies required - uses only Python standard library (tkinter is optional but recommended for GUI folder selection).

## Usage

### Command Line Options

```bash
python app.py [input_file] [options]
```

**Arguments:**
- `input_file`: Optional path to a file containing the ASCII tree

**Options:**
- `--sample`: Use built-in sample tree for testing
- `--dry-run`: Preview structure without creating files/folders

### Examples

**1. Use sample tree with dry-run:**
```bash
python app.py --sample --dry-run
```

**2. Create structure from file:**
```bash
python app.py tree.txt
```

**3. Interactive mode (paste tree and press Enter on empty line):**
```bash
python app.py
```

After providing the tree structure, a native folder selection dialog will open where you can choose the destination directory.

### Input Format

Your ASCII tree should follow this format:

```
my-project
├── README.md # Project overview
├── src/
│   ├── main.py # Entry point
│   └── utils.py # Helper functions
└── tests/
    └── test_main.py # Unit tests
```

**Notes:**
- Comments after `#` are preserved and added to generated files
- Files are detected by presence of file extensions (e.g., `.py`, `.md`)
- Folders can end with `/` or be detected by lack of extension
- First line without tree characters is treated as root folder name

## Quick Start Scripts

### Windows
Run `refined-tree-converter.bat` for a quick demo with the sample tree.

### Linux/macOS
Run `refined-tree-converter.sh` for a quick demo with the sample tree.

## How It Works

1. **Input**: Paste tree, use sample, or provide file path
2. **Parse**: Analyzes ASCII tree structure and extracts hierarchy with comments
3. **Select**: Native popup appears to choose destination folder
4. **Create**: Generates actual folders and files with comment headers
5. **Open**: Automatically opens the created folder in your file explorer

## Example Output

Input:
```
my-app
├── README.md # Overview
├── app.py # Main logic
└── utils/
    └── helpers.py # Utility functions
```

Creates:
```
my-app/
├── README.md (contains: "# Overview" as header)
├── app.py (contains: "# Main logic" as header)
└── utils/
    └── helpers.py (contains: "# Utility functions" as header)
```

Each generated file includes:
- The inline comment from the tree (if present)
- Filename as header
- "Auto-generated file" text

## Dry-Run Mode

Use `--dry-run` to preview what would be created without actually creating files:

```bash
python app.py --sample --dry-run
```

This shows:
- The parsed structure with emoji indicators (📁 folders, 📄 files)
- Where files would be created
- What content would be written to each file

## GUI Folder Selection

The tool uses tkinter (if available) to show a native folder chooser dialog. If tkinter is not available:
- Fallback prompts you to type the destination path in the terminal
- All functionality remains the same

## Contributing

Feel free to submit issues and pull requests at [https://github.com/harsh1t3/tree-converter](https://github.com/harsh1t3/tree-converter)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

Created by [harsh1t3](https://github.com/harsh1t3)