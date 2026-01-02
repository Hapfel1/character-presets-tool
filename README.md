# Elden Ring Character Preset Manager

A tool for managing character appearance presets in Elden Ring save files. Extract, view, export, and copy character customization data between saves.

## Download
[Get the latest release here](../../releases/latest)

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

## How to Use
1. Click "Browse" or "Auto-Find" to select your save file
2. Click "Load Presets" to read the character presets
3. Select a preset from the list
4. Choose an action:
   - **View Details**: See complete preset information
   - **Export All to JSON**: Save all presets to a file
   - **Copy to Another Save**: Transfer the preset to a different save

## Development & Building
See [`DEVELOPMENT.md`](DEVELOPMENT.md).

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
