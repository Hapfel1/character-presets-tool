# Elden Ring Character Preset Manager

A tool for managing character appearance presets in Elden Ring save files. Extract, view, export, and copy character customization data between saves.

## Features

- **View Character Presets**: Browse all 15 preset slots in your save file
- **Detailed Information**: See complete facial customization data (120+ parameters)
- **Export to JSON**: Save presets for backup or sharing
- **Copy Between Saves**: Transfer presets from one save file to another
- **Auto-Detection**: Automatically locate save files in default directories

## What Are Character Presets?

Elden Ring stores up to 15 character appearance presets in the `USER_DATA_10` section of save files. Each preset contains:
- Face model and hair selection
- 68 facial structure parameters
- 50+ color and cosmetic values
- Body proportions
- Body type selection

## Installation

### Requirements

- Python 3.8 or higher
- tkinter (usually included with Python)

### Setup

Clone the repository:
```bash
git clone https://github.com/Hapfel1/elden-ring-preset-manager.git
cd elden-ring-preset-manager
```
## Usage

### GUI Application

Launch the graphical interface:

```bash
python preset_gui.py
```

**Steps:**
1. Click "Browse" or "Auto-Find" to select your save file
2. Click "Load Presets" to read the character presets
3. Select a preset from the list
4. Choose an action:
   - **View Details**: See complete preset information
   - **Export All to JSON**: Save all presets to a file
   - **Copy to Another Save**: Transfer the preset to a different save

### Command-Line Tool

The CLI provides the same functionality without a GUI:

#### List all presets in a save file:
```bash
python preset_tool.py list ER0000.sl2
```

**Output:**
```
Character Presets (3/15 slots used):
============================================================

Slot 1:
  Body Type: Type A
  Face Model: 12
  Hair Model: 5
  Apparent Age: 128
  Skin Color: RGB(205, 180, 165)
  Hair Color: RGB(45, 35, 30)
...
```

#### Export presets to JSON:
```bash
python preset_tool.py export ER0000.sl2 my_presets.json
```

#### Copy preset between saves:
```bash
python preset_tool.py copy ER0000.sl2 1 ER0001.sl2 2
```
*Copies preset from slot 1 of ER0000.sl2 to slot 2 of ER0001.sl2*

#### Show detailed preset information:
```bash
python preset_tool.py info ER0000.sl2 1
```

### Command Reference

```
preset_tool.py list <save_file>
    List all character presets in a save file

preset_tool.py export <save_file> <output_json>
    Export all presets to JSON file

preset_tool.py copy <source_save> <source_slot> <dest_save> <dest_slot>
    Copy preset from one save file to another
    Slots are numbered 1-15

preset_tool.py info <save_file> <slot>
    Show detailed information for a specific preset
    Slot is numbered 1-15
```

## Technical Details

### Save File Structure

Character presets are stored in the `CSMenuSystemSaveLoad` structure within `USER_DATA_10`:

- **Location**: After Version, SteamID, and Settings sections
- **Total Size**: 0x1800 bytes (6144 bytes)
- **Structure**:
  - Header: 8 bytes (metadata)
  - 15 Preset Slots: 15 × 0x130 bytes (304 bytes each)
  - Padding: Remaining bytes

### Preset Structure (0x130 bytes)

Each preset contains:

| Section | Size | Description |
|---------|------|-------------|
| Header | 0x18 bytes | Magic ("FACE"), markers, body type |
| Face Models | 32 bytes | Face, hair, eyebrow, beard, eyepatch (with padding) |
| Facial Structure | 68 bytes | All facial proportions and features |
| Unknown Block | 64 bytes | Reserved/unknown data |
| Body Proportions | 5 bytes | Head, chest, abdomen, arms, legs |
| Skin & Cosmetics | 88 bytes | Colors, makeup, tattoos, etc. |
| Padding | 10 bytes | End padding |

### Body Type Detection

Body type is stored at offset 0x9 within each preset:
- `0` = Type A (Male build)
- `1` = Type B (Female build)

## Safety Features

- **Automatic Backups**: Creates `filename.backup` before any modifications
- **Validation**: Checks slot numbers (1-15) and file integrity
- **Empty Detection**: Identifies and skips empty preset slots
- **Read-Only Options**: Export and view don't modify save files


## Development

### Building from Source

The tool uses only Python standard library, so no build process is needed.

## Contributing

Contributions are welcome

## Related Projects

- [Elden Ring Save File Fixer](https://github.com/Hapfel1/elden-ring-save-fixer) - Fixes infinite loading screens and corruption
- [elden-ring-save-parser-lib](https://github.com/Hapfel1/elden-ring-save-parser-lib) 

## Acknowledgments

- Structure based on [ER-Save-Lib](https://github.com/soulsmods/ER-Save-Lib) Rust implementation
- 010 Editor template by [Umgak](https://github.com/Umgak) for initial structure analysis

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool modifies save files. While it creates automatic backups, **always keep your own backups** of important saves. Use at your own risk.

The developer is not responsible for corrupted saves, lost data, or any issues arising from the use of this tool.
