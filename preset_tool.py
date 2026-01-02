#!/usr/bin/env python3
"""
Elden Ring Character Preset Tool

Command-line tool for managing character appearance presets across save files.

Usage:
    preset_tool.py list <save_file>
    preset_tool.py export <save_file> <output_json>
    preset_tool.py copy <source_save> <source_slot> <dest_save> <dest_slot>
    preset_tool.py info <save_file> <slot>
"""

import sys
import json
from pathlib import Path

# Import from elden_ring_save_parser_lib
sys.path.insert(0, str(Path(__file__).parent / "elden_ring_save_parser_lib"))

from elden_ring_save_parser_lib.save import Save
from character_presets import CSMenuSystemSaveLoad, FacePreset


def list_presets(save_path: str) -> None:
    """List all presets in a save file"""
    print(f"Loading save file: {save_path}")
    
    try:
        save = Save.from_file(save_path)
        presets = save.get_character_presets()
        
        if not presets:
            print("Error: Could not load character presets")
            return
        
        active = presets.get_active_presets()
        
        print(f"\nCharacter Presets ({len(active)}/15 slots used):")
        print("=" * 60)
        
        if not active:
            print("No presets found in this save file")
            return
        
        for slot, preset in active:
            body_type = "Type A" if preset.get_body_type() == 0 else "Type B"
            print(f"\nSlot {slot + 1}:")
            print(f"  Body Type: {body_type}")
            print(f"  Face Model: {preset.face_model}")
            print(f"  Hair Model: {preset.hair_model}")
            print(f"  Apparent Age: {preset.apparent_age}")
            
            # Show some color info
            print(f"  Skin Color: RGB({preset.skin_color_r}, {preset.skin_color_g}, {preset.skin_color_b})")
            print(f"  Hair Color: RGB({preset.hair_color_r}, {preset.hair_color_g}, {preset.hair_color_b})")
            
    except FileNotFoundError:
        print(f"Error: Save file not found: {save_path}")
    except Exception as e:
        print(f"Error loading save file: {e}")
        import traceback
        traceback.print_exc()


def export_presets(save_path: str, output_path: str) -> None:
    """Export presets to JSON"""
    print(f"Loading save file: {save_path}")
    
    try:
        save = Save.from_file(save_path)
        count = save.export_presets(output_path)
        
        if count > 0:
            print(f"\nSuccessfully exported {count} preset(s) to: {output_path}")
        else:
            print("\nNo active presets found to export")
            
    except FileNotFoundError:
        print(f"Error: Save file not found: {save_path}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def copy_preset(source_save_path: str, source_slot: int, dest_save_path: str, dest_slot: int) -> None:
    """Copy preset between save files"""
    print(f"Loading source save: {source_save_path}")
    print(f"Loading destination save: {dest_save_path}")
    
    try:
        source_save = Save.from_file(source_save_path)
        dest_save = Save.from_file(dest_save_path)
        
        # Adjust slot numbers (user provides 1-15, we use 0-14)
        source_idx = source_slot - 1
        dest_idx = dest_slot - 1
        
        if source_idx < 0 or source_idx >= 15:
            print(f"Error: Source slot must be 1-15, got {source_slot}")
            return
        
        if dest_idx < 0 or dest_idx >= 15:
            print(f"Error: Destination slot must be 1-15, got {dest_slot}")
            return
        
        print(f"\nCopying preset from slot {source_slot} to slot {dest_slot}...")
        
        success = dest_save.copy_preset_to_save(source_save, source_idx, dest_idx)
        
        if success:
            # Save the modified file
            backup_path = dest_save_path + ".backup"
            print(f"Creating backup: {backup_path}")
            
            import shutil
            shutil.copy2(dest_save_path, backup_path)
            
            dest_save.save(dest_save_path)
            print(f"\nPreset copied successfully!")
            print(f"Destination save updated: {dest_save_path}")
        else:
            print("\nError: Failed to copy preset")
            print("Possible reasons:")
            print("- Source preset slot is empty")
            print("- Invalid slot numbers")
            
    except FileNotFoundError as e:
        print(f"Error: Save file not found: {e}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def show_preset_info(save_path: str, slot: int) -> None:
    """Show detailed info for a specific preset"""
    print(f"Loading save file: {save_path}")
    
    try:
        save = Save.from_file(save_path)
        presets = save.get_character_presets()
        
        if not presets:
            print("Error: Could not load character presets")
            return
        
        # Adjust slot number (user provides 1-15, we use 0-14)
        slot_idx = slot - 1
        
        if slot_idx < 0 or slot_idx >= 15:
            print(f"Error: Slot must be 1-15, got {slot}")
            return
        
        preset = presets.presets[slot_idx]
        
        if preset.is_empty():
            print(f"\nSlot {slot} is empty")
            return
        
        print(f"\nPreset Details - Slot {slot}")
        print("=" * 60)
        
        body_type = "Type A (Male)" if preset.get_body_type() == 0 else "Type B (Female)"
        print(f"\nBody Type: {body_type}")
        
        print(f"\nModels:")
        print(f"  Face Model: {preset.face_model}")
        print(f"  Hair Model: {preset.hair_model}")
        print(f"  Eyebrow Model: {preset.eyebrow_model}")
        print(f"  Beard Model: {preset.beard_model}")
        print(f"  Eye Patch Model: {preset.eyepatch_model}")
        
        print(f"\nFacial Structure:")
        print(f"  Apparent Age: {preset.apparent_age}")
        print(f"  Facial Aesthetic: {preset.facial_aesthetic}")
        print(f"  Form Emphasis: {preset.form_emphasis}")
        print(f"  Eye Size: {preset.eye_size}")
        print(f"  Eye Position: {preset.eye_position}")
        print(f"  Nose Size: {preset.nose_size}")
        print(f"  Mouth Size: {preset.mouth_width}")
        
        print(f"\nBody Proportions:")
        print(f"  Head Size: {preset.head_size}")
        print(f"  Chest Size: {preset.chest_size}")
        print(f"  Abdomen Size: {preset.abdomen_size}")
        print(f"  Arms Size: {preset.arms_size}")
        print(f"  Legs Size: {preset.legs_size}")
        
        print(f"\nColors:")
        print(f"  Skin: RGB({preset.skin_color_r}, {preset.skin_color_g}, {preset.skin_color_b})")
        print(f"  Hair: RGB({preset.hair_color_r}, {preset.hair_color_g}, {preset.hair_color_b})")
        print(f"  Left Eye: RGB({preset.left_iris_color_r}, {preset.left_iris_color_g}, {preset.left_iris_color_b})")
        print(f"  Right Eye: RGB({preset.right_iris_color_r}, {preset.right_iris_color_g}, {preset.right_iris_color_b})")
        
        print(f"\nCosmetics:")
        print(f"  Stubble: {preset.stubble}")
        print(f"  Dark Circles: {preset.dark_circles}")
        print(f"  Eye Liner: {preset.eye_liner}")
        print(f"  Lip Stick: {preset.lip_stick}")
        
    except FileNotFoundError:
        print(f"Error: Save file not found: {save_path}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def print_usage():
    """Print usage information"""
    print("Elden Ring Character Preset Tool")
    print("=" * 60)
    print("\nUsage:")
    print("  preset_tool.py list <save_file>")
    print("      List all character presets in a save file")
    print()
    print("  preset_tool.py export <save_file> <output_json>")
    print("      Export all presets to JSON file")
    print()
    print("  preset_tool.py copy <source_save> <source_slot> <dest_save> <dest_slot>")
    print("      Copy preset from one save file to another")
    print("      Slots are numbered 1-15")
    print()
    print("  preset_tool.py info <save_file> <slot>")
    print("      Show detailed information for a specific preset slot")
    print("      Slot is numbered 1-15")
    print()
    print("Examples:")
    print("  preset_tool.py list ER0000.sl2")
    print("  preset_tool.py export ER0000.sl2 my_presets.json")
    print("  preset_tool.py copy ER0000.sl2 1 ER0001.sl2 2")
    print("  preset_tool.py info ER0000.sl2 1")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        if len(sys.argv) != 3:
            print("Usage: preset_tool.py list <save_file>")
            return
        list_presets(sys.argv[2])
        
    elif command == "export":
        if len(sys.argv) != 4:
            print("Usage: preset_tool.py export <save_file> <output_json>")
            return
        export_presets(sys.argv[2], sys.argv[3])
        
    elif command == "copy":
        if len(sys.argv) != 6:
            print("Usage: preset_tool.py copy <source_save> <source_slot> <dest_save> <dest_slot>")
            return
        try:
            source_slot = int(sys.argv[3])
            dest_slot = int(sys.argv[5])
            copy_preset(sys.argv[2], source_slot, sys.argv[4], dest_slot)
        except ValueError:
            print("Error: Slot numbers must be integers (1-15)")
            
    elif command == "info":
        if len(sys.argv) != 4:
            print("Usage: preset_tool.py info <save_file> <slot>")
            return
        try:
            slot = int(sys.argv[3])
            show_preset_info(sys.argv[2], slot)
        except ValueError:
            print("Error: Slot number must be an integer (1-15)")
            
    else:
        print(f"Unknown command: {command}")
        print()
        print_usage()


if __name__ == "__main__":
    main()
