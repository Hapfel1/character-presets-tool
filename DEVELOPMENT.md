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

## Build
```bash
pyinstaller "Elden_Ring_Preset_Manager.spec"
```