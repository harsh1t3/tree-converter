# ASCII Tree to Folder Structure Converter

A Python utility that converts ASCII tree representations into actual folder and file structures on your filesystem.

## Features

- Convert ASCII tree diagrams to real directory structures
- Support for comments in tree format
- Dry-run mode to preview structure before creation
- Cross-platform compatibility (Windows, macOS, Linux)
- Handles nested directories and files automatically

## Installation

Clone this repository:

```bash
git clone https://github.com/harsh1t3/tree-converter.git
cd tree-converter
```

No additional dependencies required - uses only Python standard library.

## Usage

### Command Line Options

```bash
python refined-tree-converter.py [input_file] [output_dir] [options]
```

**Options:**
- `--sample`: Use built-in sample tree for testing
- `--dry-run`: Preview structure without creating files/folders
- `--root-name`: Override the root project folder name

### Examples

**1. Use sample tree with dry-run:**
```bash
python refined-tree-converter.py --sample --dry-run
```

**2. Create structure from file:**
```bash
python refined-tree-converter.py tree.txt ./output
```

**3. Interactive mode:**
```bash
python refined-tree-converter.py
# Then paste your tree structure and press Enter twice
```

### Input Format

Your ASCII tree should follow this format:

```
my-project
├── README.md # Project overview
├── src
│   ├── main.py # Entry point
│   └── utils.py # Helper functions
└── tests
    └── test_main.py # Unit tests
```

## Quick Start Scripts

### Windows
Run `refined-tree-converter.bat` for a quick demo with the sample tree.

### Linux/macOS
Run `refined-tree-converter.sh` for a quick demo with the sample tree.

## How It Works

1. **Parse**: Analyzes ASCII tree structure and extracts hierarchy
2. **Process**: Converts tree into internal data structure
3. **Create**: Generates actual folders and files with optional comments
4. **Verify**: Shows created structure or dry-run preview

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
├── README.md (with comment header)
├── app.py (with comment header)
└── utils/
    └── helpers.py (with comment header)
```

## Contributing

Feel free to submit issues and pull requests at [https://github.com/harsh1t3](https://github.com/harsh1t3)

## License

MIT License - see LICENSE file for details.