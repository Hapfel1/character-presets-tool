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
    """Show detailed info for a specific preset - COMPLETE VERSION"""
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
        
        print(f"\n{'=' * 60}")
        print(f"PRESET SLOT {slot}")
        print(f"{'=' * 60}")
        
        body_type = "Type A (Male)" if preset.get_body_type() == 0 else "Type B (Female)"
        print(f"Body Type: {body_type}")
        
        # MODELS
        print(f"\nMODELS:")
        print(f"  Face Model:    {preset.face_model}")
        print(f"  Hair Model:    {preset.hair_model}")
        print(f"  Eyebrow Model: {preset.eyebrow_model}")
        print(f"  Beard Model:   {preset.beard_model}")
        print(f"  Eye Patch:     {preset.eyepatch_model}")
        
        # FACIAL STRUCTURE - Complete list
        print(f"\nFACIAL STRUCTURE:")
        print(f"  Apparent Age:      {preset.apparent_age}")
        print(f"  Facial Aesthetic:  {preset.facial_aesthetic}")
        print(f"  Form Emphasis:     {preset.form_emphasis}")
        
        print(f"\n  Brow Ridge:")
        print(f"    Height: {preset.brow_ridge_height}")
        print(f"    Inner:  {preset.inner_brow_ridge}")
        print(f"    Outer:  {preset.outer_brow_ridge}")
        
        print(f"\n  Cheekbones:")
        print(f"    Height:     {preset.cheekbone_height}")
        print(f"    Depth:      {preset.cheekbone_depth}")
        print(f"    Width:      {preset.cheekbone_width}")
        print(f"    Protrusion: {preset.cheekbone_protrusion}")
        print(f"  Cheeks: {preset.cheeks}")
        
        print(f"\n  Chin:")
        print(f"    Tip Position: {preset.chin_tip_position}")
        print(f"    Length:       {preset.chin_length}")
        print(f"    Protrusion:   {preset.chin_protrusion}")
        print(f"    Depth:        {preset.chin_depth}")
        print(f"    Size:         {preset.chin_size}")
        print(f"    Height:       {preset.chin_height}")
        print(f"    Width:        {preset.chin_width}")
        
        print(f"\n  Eyes:")
        print(f"    Position: {preset.eye_position}")
        print(f"    Size:     {preset.eye_size}")
        print(f"    Slant:    {preset.eye_slant}")
        print(f"    Spacing:  {preset.eye_spacing}")
        
        print(f"\n  Nose:")
        print(f"    Size:            {preset.nose_size}")
        print(f"    Forehead Ratio:  {preset.nose_forehead_ratio}")
        print(f"    Ridge Depth:     {preset.nose_ridge_depth}")
        print(f"    Ridge Length:    {preset.nose_ridge_length}")
        print(f"    Position:        {preset.nose_position}")
        print(f"    Tip Height:      {preset.nose_tip_height}")
        print(f"    Nostril Slant:   {preset.nostril_slant}")
        print(f"    Nostril Size:    {preset.nostril_size}")
        print(f"    Nostril Width:   {preset.nostril_width}")
        print(f"    Protrusion:      {preset.nose_protrusion}")
        print(f"    Bridge Height:   {preset.nose_bridge_height}")
        print(f"    Bridge Prot. 1:  {preset.bridge_protrusion1}")
        print(f"    Bridge Prot. 2:  {preset.bridge_protrusion2}")
        print(f"    Bridge Width:    {preset.nose_bridge_width}")
        print(f"    Height:          {preset.nose_height}")
        print(f"    Slant:           {preset.nose_slant}")
        
        print(f"\n  Face Shape:")
        print(f"    Protrusion:          {preset.face_protrusion}")
        print(f"    Vertical Ratio:      {preset.vertical_face_ratio}")
        print(f"    Feature Slant:       {preset.facial_feature_slant}")
        print(f"    Horizontal Ratio:    {preset.horizontal_face_ratio}")
        
        print(f"\n  Forehead:")
        print(f"    Depth:      {preset.forehead_depth}")
        print(f"    Protrusion: {preset.forehead_protrusion}")
        
        print(f"\n  Jaw:")
        print(f"    Protrusion: {preset.jaw_protrusion}")
        print(f"    Width:      {preset.jaw_width}")
        print(f"    Lower:      {preset.lower_jaw}")
        print(f"    Contour:    {preset.jaw_contour}")
        
        print(f"\n  Lips:")
        print(f"    Shape:      {preset.lip_shape}")
        print(f"    Size:       {preset.lip_size}")
        print(f"    Fullness:   {preset.lip_fullness}")
        print(f"    Protrusion: {preset.lip_protrusion}")
        print(f"    Thickness:  {preset.lip_thickness}")
        
        print(f"\n  Mouth:")
        print(f"    Expression:     {preset.mouth_expression}")
        print(f"    Protrusion:     {preset.mouth_protrusion}")
        print(f"    Slant:          {preset.mouth_slant}")
        print(f"    Occlusion:      {preset.occlusion}")
        print(f"    Position:       {preset.mouth_position}")
        print(f"    Width:          {preset.mouth_width}")
        print(f"    Chin Distance:  {preset.mouth_chin_distance}")
        
        # BODY PROPORTIONS
        print(f"\nBODY PROPORTIONS:")
        print(f"  Head:    {preset.head_size}")
        print(f"  Chest:   {preset.chest_size}")
        print(f"  Abdomen: {preset.abdomen_size}")
        print(f"  Arms:    {preset.arms_size}")
        print(f"  Legs:    {preset.legs_size}")
        
        # COLORS
        print(f"\nCOLORS:")
        print(f"  Skin:       RGB({preset.skin_color_r:>3}, {preset.skin_color_g:>3}, {preset.skin_color_b:>3})")
        print(f"    Luster: {preset.skin_luster}")
        print(f"    Pores:  {preset.pores}")
        
        print(f"\n  Hair:       RGB({preset.hair_color_r:>3}, {preset.hair_color_g:>3}, {preset.hair_color_b:>3})")
        print(f"    Luster:        {preset.luster}")
        print(f"    Root Darkness: {preset.hair_root_darkness}")
        print(f"    White Hairs:   {preset.white_hairs}")
        
        print(f"\n  Beard:      RGB({preset.beard_color_r:>3}, {preset.beard_color_g:>3}, {preset.beard_color_b:>3})")
        print(f"    Luster:        {preset.beard_luster}")
        print(f"    Root Darkness: {preset.beard_root_darkness}")
        print(f"    White Hairs:   {preset.beard_white_hairs}")
        
        print(f"\n  Eyebrows:   RGB({preset.brow_color_r:>3}, {preset.brow_color_g:>3}, {preset.brow_color_b:>3})")
        print(f"    Luster:        {preset.brow_luster}")
        print(f"    Root Darkness: {preset.brow_root_darkness}")
        print(f"    White Hairs:   {preset.brow_white_hairs}")
        
        print(f"\n  Eyelashes:  RGB({preset.eye_lash_color_r:>3}, {preset.eye_lash_color_g:>3}, {preset.eye_lash_color_b:>3})")
        print(f"  Eye Patch:  RGB({preset.eye_patch_color_r:>3}, {preset.eye_patch_color_g:>3}, {preset.eye_patch_color_b:>3})")
        
        print(f"\n  Left Eye:   RGB({preset.left_iris_color_r:>3}, {preset.left_iris_color_g:>3}, {preset.left_iris_color_b:>3})")
        print(f"    Iris Size:  {preset.left_iris_size}")
        print(f"    Clouding:   {preset.left_eye_clouding}")
        print(f"    Cloud RGB:  ({preset.left_eye_clouding_color_r}, {preset.left_eye_clouding_color_g}, {preset.left_eye_clouding_color_b})")
        print(f"    White RGB:  ({preset.left_eye_white_color_r}, {preset.left_eye_white_color_g}, {preset.left_eye_white_color_b})")
        print(f"    Position:   {preset.left_eye_position}")
        
        print(f"\n  Right Eye:  RGB({preset.right_iris_color_r:>3}, {preset.right_iris_color_g:>3}, {preset.right_iris_color_b:>3})")
        print(f"    Iris Size:  {preset.right_iris_size}")
        print(f"    Clouding:   {preset.right_eye_clouding}")
        print(f"    Cloud RGB:  ({preset.right_eye_clouding_color_r}, {preset.right_eye_clouding_color_g}, {preset.right_eye_clouding_color_b})")
        print(f"    White RGB:  ({preset.right_eye_white_color_r}, {preset.right_eye_white_color_g}, {preset.right_eye_white_color_b})")
        print(f"    Position:   {preset.right_eye_position}")
        
        # COSMETICS
        print(f"\nCOSMETICS:")
        print(f"  Stubble:       {preset.stubble}")
        
        print(f"\n  Dark Circles:  {preset.dark_circles}")
        if preset.dark_circles > 0:
            print(f"    Color: RGB({preset.dark_circle_color_r}, {preset.dark_circle_color_g}, {preset.dark_circle_color_b})")
        
        print(f"\n  Cheek Color:   {preset.cheeks_color_intensity}")
        if preset.cheeks_color_intensity > 0:
            print(f"    Color: RGB({preset.cheek_color_r}, {preset.cheek_color_g}, {preset.cheek_color_b})")
        
        print(f"\n  Eye Liner:     {preset.eye_liner}")
        if preset.eye_liner > 0:
            print(f"    Color: RGB({preset.eye_liner_color_r}, {preset.eye_liner_color_g}, {preset.eye_liner_color_b})")
        
        print(f"\n  Eye Shadow (Lower): {preset.eye_shadow_lower}")
        if preset.eye_shadow_lower > 0:
            print(f"    Color: RGB({preset.eye_shadow_lower_color_r}, {preset.eye_shadow_lower_color_g}, {preset.eye_shadow_lower_color_b})")
        
        print(f"\n  Eye Shadow (Upper): {preset.eye_shadow_upper}")
        if preset.eye_shadow_upper > 0:
            print(f"    Color: RGB({preset.eye_shadow_upper_color_r}, {preset.eye_shadow_upper_color_g}, {preset.eye_shadow_upper_color_b})")
        
        print(f"\n  Lip Stick:     {preset.lip_stick}")
        if preset.lip_stick > 0:
            print(f"    Color: RGB({preset.lip_stick_color_r}, {preset.lip_stick_color_g}, {preset.lip_stick_color_b})")
        
        # TATTOO/MARK
        print(f"\nTATTOO/MARK:")
        print(f"  Horizontal Position: {preset.tattoo_mark_position_horizontal}")
        print(f"  Vertical Position:   {preset.tattoo_mark_position_vertical}")
        print(f"  Angle:               {preset.tattoo_mark_angle}")
        print(f"  Expansion:           {preset.tattoo_mark_expansion}")
        print(f"  Color:               RGB({preset.tattoo_mark_color_r}, {preset.tattoo_mark_color_g}, {preset.tattoo_mark_color_b})")
        print(f"  Flip:                {preset.tattoo_mark_flip}")
        
        # BODY HAIR
        print(f"\nBODY HAIR:")
        print(f"  Intensity: {preset.body_hair}")
        if preset.body_hair > 0:
            print(f"  Color:     RGB({preset.body_hair_color_r}, {preset.body_hair_color_g}, {preset.body_hair_color_b})")
        
        print(f"\n{'=' * 60}\n")
        
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
