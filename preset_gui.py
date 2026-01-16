#!/usr/bin/env python3
"""
Elden Ring Character Preset Manager - GUI

Graphical interface for managing character appearance presets across save files.
"""

import os
import shutil
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from elden_ring_save_parser_lib.save import Save
from character_presets import CSMenuSystemSaveLoad, FacePreset


class PresetManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Elden Ring Character Preset Manager")
        self.root.geometry("800x650")
        self.root.resizable(False, False)
        
        # Style configuration matching save file fixer
        style = ttk.Style()
        style.theme_use("clam")
        
        self.pink_colors = {"pink": "#F5A9B8", "text": "#1f1f1f"}
        style.configure("Accent.TButton", padding=6)
        style.map(
            "Accent.TButton",
            background=[("active", self.pink_colors["pink"])],
            foreground=[("active", self.pink_colors["text"])],
        )
        
        self.default_save_path = Path(os.environ.get("APPDATA", "")) / "EldenRing"
        self.current_save = None
        self.current_save_path = None
        self.presets = None
        self.selected_slot = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components"""
        # Title
        title_frame = ttk.Frame(self.root, padding="15")
        title_frame.pack(fill=tk.X)
        
        ttk.Label(
            title_frame,
            text="Elden Ring Character Preset Manager",
            font=("Segoe UI", 18, "bold"),
        ).pack()
        
        ttk.Label(
            title_frame,
            text="View, export, and copy character appearance presets between save files.",
            font=("Segoe UI", 10),
        ).pack()
        
        # File Selection
        file_frame = ttk.LabelFrame(
            self.root, text="Step 1: Select Save File", padding="15"
        )
        file_frame.pack(fill=tk.X, padx=15, pady=10)
        
        self.file_path_var = tk.StringVar()
        
        path_frame = ttk.Frame(file_frame)
        path_frame.pack(fill=tk.X)
        
        ttk.Entry(path_frame, textvariable=self.file_path_var, width=50).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5)
        )
        
        ttk.Button(
            path_frame,
            text="Browse",
            command=self.browse_file,
            width=10,
            style="Accent.TButton",
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            path_frame,
            text="Auto-Find",
            command=self.auto_detect,
            width=10,
            style="Accent.TButton",
        ).pack(side=tk.LEFT, padx=2)
        
        buttons_frame = ttk.Frame(file_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            buttons_frame,
            text="Load Presets",
            command=self.load_presets,
            width=20,
            style="Accent.TButton",
        ).pack(side=tk.LEFT)
        
        # Preset Selection
        preset_frame = ttk.LabelFrame(
            self.root, text="Step 2: Character Presets", padding="10"
        )
        preset_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)
        
        # Preset list
        list_frame = ttk.Frame(preset_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.preset_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 10),
            height=12,
            selectmode=tk.SINGLE,
        )
        self.preset_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.preset_listbox.yview)
        
        self.preset_listbox.bind("<ButtonRelease-1>", self.on_preset_select)
        self.preset_listbox.bind("<Double-Button-1>", self.show_preset_details)
        
        # Action buttons
        action_frame = ttk.LabelFrame(
            self.root, text="Step 3: Actions", padding="10"
        )
        action_frame.pack(fill=tk.X, padx=15, pady=8)
        
        ttk.Button(
            action_frame,
            text="View Details",
            command=self.show_preset_details,
            width=20,
            style="Accent.TButton",
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            action_frame,
            text="Export All to JSON",
            command=self.export_presets,
            width=20,
            style="Accent.TButton",
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            action_frame,
            text="Import from JSON",
            command=self.import_preset,
            width=20,
            style="Accent.TButton",
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            action_frame,
            text="Copy to Another Save",
            command=self.copy_preset,
            width=20,
            style="Accent.TButton",
        ).pack(side=tk.LEFT, padx=5)
        
        # Status bar
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar(value="Ready - Select a save file to begin")
        ttk.Label(
            status_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2),
        ).pack(fill=tk.X)
        
    def browse_file(self):
        """Open file browser"""
        filename = filedialog.askopenfilename(
            title="Select Elden Ring Save File",
            initialdir=self.default_save_path,
            filetypes=[("Elden Ring Saves", "*.sl2 *.co2"), ("All files", "*.*")],
        )
        if filename:
            self.file_path_var.set(filename)
            self.status_var.set(f"Selected: {os.path.basename(filename)}")
            
    def auto_detect(self):
        """Auto-detect save file"""
        if not self.default_save_path.exists():
            messagebox.showerror(
                "Not Found",
                f"Elden Ring save folder not found:\n{self.default_save_path}",
            )
            return
        
        saves = list(self.default_save_path.rglob("ER*.sl2")) + list(
            self.default_save_path.rglob("ER*.co2")
        )
        
        if not saves:
            messagebox.showwarning("Not Found", "No Elden Ring save files found.")
            return
        
        if len(saves) == 1:
            self.file_path_var.set(str(saves[0]))
            self.status_var.set("Save file auto-detected")
        else:
            self.show_save_selector(saves)
            
    def show_save_selector(self, saves):
        """Show dialog to select from multiple saves"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Save File")
        dialog.geometry("500x300")
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"500x300+{x}+{y}")
        
        ttk.Label(
            dialog,
            text=f"Found {len(saves)} save files:",
            font=("Segoe UI", 10, "bold"),
            padding=10,
        ).pack()
        
        listbox_frame = ttk.Frame(dialog, padding=10)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(
            listbox_frame, yscrollcommand=scrollbar.set, font=("Consolas", 9)
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        for save in saves:
            listbox.insert(tk.END, str(save))
        
        def select_save():
            selection = listbox.curselection()
            if selection:
                self.file_path_var.set(str(saves[selection[0]]))
                self.status_var.set(f"Selected: {saves[selection[0]].name}")
                dialog.destroy()
        
        ttk.Button(
            dialog, text="Select", command=select_save, style="Accent.TButton"
        ).pack(pady=10)
        listbox.bind("<Double-Button-1>", lambda e: select_save())
        
    def load_presets(self):
        """Load the selected save file"""
        filepath = self.file_path_var.get()
        
        if not filepath or not os.path.exists(filepath):
            messagebox.showerror("Error", "Please select a valid save file first!")
            return
        
        try:
            self.status_var.set(f"Loading {os.path.basename(filepath)}...")
            self.root.update()
            
            self.current_save = Save.from_file(filepath)
            self.current_save_path = filepath
            self.presets = self.current_save.get_character_presets()
            
            if not self.presets:
                messagebox.showerror("Error", "Could not load character presets from this save file.")
                self.status_var.set("Error loading presets")
                return
            
            self.populate_preset_list()
            self.status_var.set(f"Loaded: {os.path.basename(filepath)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load save file:\n{str(e)}")
            self.status_var.set("Error")
            import traceback
            traceback.print_exc()
            
    def populate_preset_list(self):
        """Populate the preset list"""
        self.preset_listbox.delete(0, tk.END)
        
        if not self.presets:
            return
        
        active_presets = self.presets.get_active_presets()
        
        if not active_presets:
            self.preset_listbox.insert(tk.END, "No presets found in this save file")
            return
        
        for slot, preset in active_presets:
            body_type = "Type A" if preset.get_body_type() == 0 else "Type B"
            skin = f"RGB({preset.skin_color_r},{preset.skin_color_g},{preset.skin_color_b})"
            hair = f"RGB({preset.hair_color_r},{preset.hair_color_g},{preset.hair_color_b})"
            
            line = f"Slot {slot + 1:2d} | {body_type:6s} | Face:{preset.face_model:2d} Hair:{preset.hair_model:2d} | Skin:{skin:15s} Hair:{hair}"
            self.preset_listbox.insert(tk.END, line)
            
    def on_preset_select(self, event):
        """Handle preset selection"""
        selection = self.preset_listbox.curselection()
        if not selection:
            return
        
        # Get the actual slot number from active presets
        active_presets = self.presets.get_active_presets()
        if selection[0] < len(active_presets):
            self.selected_slot = active_presets[selection[0]][0]
            
    def show_preset_details(self, event=None):
        """Show detailed preset information in a popup"""
        if self.selected_slot is None:
            messagebox.showwarning("No Selection", "Please select a preset first!")
            return
        
        preset = self.presets.presets[self.selected_slot]
        
        if preset.is_empty():
            return
        
        # Create detail window
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Preset Details - Slot {self.selected_slot + 1}")
        detail_window.geometry("700x700")
        detail_window.grab_set()
        
        # Center window
        detail_window.update_idletasks()
        x = (detail_window.winfo_screenwidth() // 2) - (detail_window.winfo_width() // 2)
        y = (detail_window.winfo_screenheight() // 2) - (detail_window.winfo_height() // 2)
        detail_window.geometry(f"700x700+{x}+{y}")
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(detail_window, padding=10)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 9),
            width=80,
            height=35,
        )
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        
        # Build complete details text
        details = []
        details.append(f"{'='*60}\n")
        details.append(f"PRESET SLOT {self.selected_slot + 1}\n")
        details.append(f"{'='*60}\n\n")
        
        body_type = "Type A (Male)" if preset.get_body_type() == 0 else "Type B (Female)"
        details.append(f"Body Type: {body_type}\n\n")
        
        # MODELS
        details.append("MODELS:\n")
        details.append(f"  Face Model:    {preset.face_model}\n")
        details.append(f"  Hair Model:    {preset.hair_model}\n")
        details.append(f"  Eyebrow Model: {preset.eyebrow_model}\n")
        details.append(f"  Beard Model:   {preset.beard_model}\n")
        details.append(f"  Eye Patch:     {preset.eyepatch_model}\n\n")
        
        # FACIAL STRUCTURE - Complete
        details.append("FACIAL STRUCTURE:\n")
        details.append(f"  Apparent Age:      {preset.apparent_age}\n")
        details.append(f"  Facial Aesthetic:  {preset.facial_aesthetic}\n")
        details.append(f"  Form Emphasis:     {preset.form_emphasis}\n\n")
        
        details.append("  Brow Ridge:\n")
        details.append(f"    Height: {preset.brow_ridge_height}\n")
        details.append(f"    Inner:  {preset.inner_brow_ridge}\n")
        details.append(f"    Outer:  {preset.outer_brow_ridge}\n\n")
        
        details.append("  Cheekbones:\n")
        details.append(f"    Height:     {preset.cheekbone_height}\n")
        details.append(f"    Depth:      {preset.cheekbone_depth}\n")
        details.append(f"    Width:      {preset.cheekbone_width}\n")
        details.append(f"    Protrusion: {preset.cheekbone_protrusion}\n")
        details.append(f"  Cheeks: {preset.cheeks}\n\n")
        
        details.append("  Chin:\n")
        details.append(f"    Tip Position: {preset.chin_tip_position}\n")
        details.append(f"    Length:       {preset.chin_length}\n")
        details.append(f"    Protrusion:   {preset.chin_protrusion}\n")
        details.append(f"    Depth:        {preset.chin_depth}\n")
        details.append(f"    Size:         {preset.chin_size}\n")
        details.append(f"    Height:       {preset.chin_height}\n")
        details.append(f"    Width:        {preset.chin_width}\n\n")
        
        details.append("  Eyes:\n")
        details.append(f"    Position: {preset.eye_position}\n")
        details.append(f"    Size:     {preset.eye_size}\n")
        details.append(f"    Slant:    {preset.eye_slant}\n")
        details.append(f"    Spacing:  {preset.eye_spacing}\n\n")
        
        details.append("  Nose:\n")
        details.append(f"    Size:            {preset.nose_size}\n")
        details.append(f"    Forehead Ratio:  {preset.nose_forehead_ratio}\n")
        details.append(f"    Ridge Depth:     {preset.nose_ridge_depth}\n")
        details.append(f"    Ridge Length:    {preset.nose_ridge_length}\n")
        details.append(f"    Position:        {preset.nose_position}\n")
        details.append(f"    Tip Height:      {preset.nose_tip_height}\n")
        details.append(f"    Nostril Slant:   {preset.nostril_slant}\n")
        details.append(f"    Nostril Size:    {preset.nostril_size}\n")
        details.append(f"    Nostril Width:   {preset.nostril_width}\n")
        details.append(f"    Protrusion:      {preset.nose_protrusion}\n")
        details.append(f"    Bridge Height:   {preset.nose_bridge_height}\n")
        details.append(f"    Bridge Prot. 1:  {preset.bridge_protrusion1}\n")
        details.append(f"    Bridge Prot. 2:  {preset.bridge_protrusion2}\n")
        details.append(f"    Bridge Width:    {preset.nose_bridge_width}\n")
        details.append(f"    Height:          {preset.nose_height}\n")
        details.append(f"    Slant:           {preset.nose_slant}\n\n")
        
        details.append("  Face Shape:\n")
        details.append(f"    Protrusion:          {preset.face_protrusion}\n")
        details.append(f"    Vertical Ratio:      {preset.vertical_face_ratio}\n")
        details.append(f"    Feature Slant:       {preset.facial_feature_slant}\n")
        details.append(f"    Horizontal Ratio:    {preset.horizontal_face_ratio}\n\n")
        
        details.append("  Forehead:\n")
        details.append(f"    Depth:      {preset.forehead_depth}\n")
        details.append(f"    Protrusion: {preset.forehead_protrusion}\n\n")
        
        details.append("  Jaw:\n")
        details.append(f"    Protrusion: {preset.jaw_protrusion}\n")
        details.append(f"    Width:      {preset.jaw_width}\n")
        details.append(f"    Lower:      {preset.lower_jaw}\n")
        details.append(f"    Contour:    {preset.jaw_contour}\n\n")
        
        details.append("  Lips:\n")
        details.append(f"    Shape:      {preset.lip_shape}\n")
        details.append(f"    Size:       {preset.lip_size}\n")
        details.append(f"    Fullness:   {preset.lip_fullness}\n")
        details.append(f"    Protrusion: {preset.lip_protrusion}\n")
        details.append(f"    Thickness:  {preset.lip_thickness}\n\n")
        
        details.append("  Mouth:\n")
        details.append(f"    Expression:     {preset.mouth_expression}\n")
        details.append(f"    Protrusion:     {preset.mouth_protrusion}\n")
        details.append(f"    Slant:          {preset.mouth_slant}\n")
        details.append(f"    Occlusion:      {preset.occlusion}\n")
        details.append(f"    Position:       {preset.mouth_position}\n")
        details.append(f"    Width:          {preset.mouth_width}\n")
        details.append(f"    Chin Distance:  {preset.mouth_chin_distance}\n\n")
        
        # BODY PROPORTIONS
        details.append("BODY PROPORTIONS:\n")
        details.append(f"  Head:    {preset.head_size}\n")
        details.append(f"  Chest:   {preset.chest_size}\n")
        details.append(f"  Abdomen: {preset.abdomen_size}\n")
        details.append(f"  Arms:    {preset.arms_size}\n")
        details.append(f"  Legs:    {preset.legs_size}\n\n")
        
        # COLORS - Complete with details
        details.append("COLORS:\n")
        details.append(f"  Skin:       RGB({preset.skin_color_r:3d}, {preset.skin_color_g:3d}, {preset.skin_color_b:3d})\n")
        details.append(f"    Luster: {preset.skin_luster}\n")
        details.append(f"    Pores:  {preset.pores}\n\n")
        
        details.append(f"  Hair:       RGB({preset.hair_color_r:3d}, {preset.hair_color_g:3d}, {preset.hair_color_b:3d})\n")
        details.append(f"    Luster:        {preset.luster}\n")
        details.append(f"    Root Darkness: {preset.hair_root_darkness}\n")
        details.append(f"    White Hairs:   {preset.white_hairs}\n\n")
        
        details.append(f"  Beard:      RGB({preset.beard_color_r:3d}, {preset.beard_color_g:3d}, {preset.beard_color_b:3d})\n")
        details.append(f"    Luster:        {preset.beard_luster}\n")
        details.append(f"    Root Darkness: {preset.beard_root_darkness}\n")
        details.append(f"    White Hairs:   {preset.beard_white_hairs}\n\n")
        
        details.append(f"  Eyebrows:   RGB({preset.brow_color_r:3d}, {preset.brow_color_g:3d}, {preset.brow_color_b:3d})\n")
        details.append(f"    Luster:        {preset.brow_luster}\n")
        details.append(f"    Root Darkness: {preset.brow_root_darkness}\n")
        details.append(f"    White Hairs:   {preset.brow_white_hairs}\n\n")
        
        details.append(f"  Eyelashes:  RGB({preset.eye_lash_color_r:3d}, {preset.eye_lash_color_g:3d}, {preset.eye_lash_color_b:3d})\n")
        details.append(f"  Eye Patch:  RGB({preset.eye_patch_color_r:3d}, {preset.eye_patch_color_g:3d}, {preset.eye_patch_color_b:3d})\n\n")
        
        details.append(f"  Left Eye:   RGB({preset.left_iris_color_r:3d}, {preset.left_iris_color_g:3d}, {preset.left_iris_color_b:3d})\n")
        details.append(f"    Iris Size:  {preset.left_iris_size}\n")
        details.append(f"    Clouding:   {preset.left_eye_clouding}\n")
        details.append(f"    Cloud RGB:  ({preset.left_eye_clouding_color_r}, {preset.left_eye_clouding_color_g}, {preset.left_eye_clouding_color_b})\n")
        details.append(f"    White RGB:  ({preset.left_eye_white_color_r}, {preset.left_eye_white_color_g}, {preset.left_eye_white_color_b})\n")
        details.append(f"    Position:   {preset.left_eye_position}\n\n")
        
        details.append(f"  Right Eye:  RGB({preset.right_iris_color_r:3d}, {preset.right_iris_color_g:3d}, {preset.right_iris_color_b:3d})\n")
        details.append(f"    Iris Size:  {preset.right_iris_size}\n")
        details.append(f"    Clouding:   {preset.right_eye_clouding}\n")
        details.append(f"    Cloud RGB:  ({preset.right_eye_clouding_color_r}, {preset.right_eye_clouding_color_g}, {preset.right_eye_clouding_color_b})\n")
        details.append(f"    White RGB:  ({preset.right_eye_white_color_r}, {preset.right_eye_white_color_g}, {preset.right_eye_white_color_b})\n")
        details.append(f"    Position:   {preset.right_eye_position}\n\n")
        
        # COSMETICS - Complete
        details.append("COSMETICS:\n")
        details.append(f"  Stubble:       {preset.stubble}\n\n")
        
        details.append(f"  Dark Circles:  {preset.dark_circles}\n")
        if preset.dark_circles > 0:
            details.append(f"    Color: RGB({preset.dark_circle_color_r}, {preset.dark_circle_color_g}, {preset.dark_circle_color_b})\n")
        details.append("\n")
        
        details.append(f"  Cheek Color:   {preset.cheeks_color_intensity}\n")
        if preset.cheeks_color_intensity > 0:
            details.append(f"    Color: RGB({preset.cheek_color_r}, {preset.cheek_color_g}, {preset.cheek_color_b})\n")
        details.append("\n")
        
        details.append(f"  Eye Liner:     {preset.eye_liner}\n")
        if preset.eye_liner > 0:
            details.append(f"    Color: RGB({preset.eye_liner_color_r}, {preset.eye_liner_color_g}, {preset.eye_liner_color_b})\n")
        details.append("\n")
        
        details.append(f"  Eye Shadow (Lower): {preset.eye_shadow_lower}\n")
        if preset.eye_shadow_lower > 0:
            details.append(f"    Color: RGB({preset.eye_shadow_lower_color_r}, {preset.eye_shadow_lower_color_g}, {preset.eye_shadow_lower_color_b})\n")
        details.append("\n")
        
        details.append(f"  Eye Shadow (Upper): {preset.eye_shadow_upper}\n")
        if preset.eye_shadow_upper > 0:
            details.append(f"    Color: RGB({preset.eye_shadow_upper_color_r}, {preset.eye_shadow_upper_color_g}, {preset.eye_shadow_upper_color_b})\n")
        details.append("\n")
        
        details.append(f"  Lip Stick:     {preset.lip_stick}\n")
        if preset.lip_stick > 0:
            details.append(f"    Color: RGB({preset.lip_stick_color_r}, {preset.lip_stick_color_g}, {preset.lip_stick_color_b})\n")
        details.append("\n")
        
        # TATTOO/MARK
        details.append("TATTOO/MARK:\n")
        details.append(f"  Horizontal Position: {preset.tattoo_mark_position_horizontal}\n")
        details.append(f"  Vertical Position:   {preset.tattoo_mark_position_vertical}\n")
        details.append(f"  Angle:               {preset.tattoo_mark_angle}\n")
        details.append(f"  Expansion:           {preset.tattoo_mark_expansion}\n")
        details.append(f"  Color:               RGB({preset.tattoo_mark_color_r}, {preset.tattoo_mark_color_g}, {preset.tattoo_mark_color_b})\n")
        details.append(f"  Flip:                {preset.tattoo_mark_flip}\n\n")
        
        # BODY HAIR
        details.append("BODY HAIR:\n")
        details.append(f"  Intensity: {preset.body_hair}\n")
        if preset.body_hair > 0:
            details.append(f"  Color:     RGB({preset.body_hair_color_r}, {preset.body_hair_color_g}, {preset.body_hair_color_b})\n")
        
        details.append(f"\n{'='*60}\n")
        
        text_widget.insert(1.0, "".join(details))
        text_widget.config(state=tk.DISABLED)
        
        ttk.Button(
            detail_window,
            text="Close",
            command=detail_window.destroy,
            style="Accent.TButton",
        ).pack(pady=10)
        
    def export_presets(self):
        """Export presets to JSON"""
        if not self.current_save:
            messagebox.showerror("Error", "No save file loaded")
            return
        
        filepath = filedialog.asksaveasfilename(
            title="Export Presets",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
        )
        
        if not filepath:
            return
        
        try:
            count = self.current_save.export_presets(filepath)
            messagebox.showinfo(
                "Export Successful",
                f"Exported {count} preset(s) to:\n{os.path.basename(filepath)}"
            )
            self.status_var.set(f"Exported {count} presets")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export presets:\n{str(e)}")
            import traceback
            traceback.print_exc()

    def import_preset(self):
        """Import preset from JSON file"""
        if not self.current_save:
            messagebox.showerror("Error", "No save file loaded")
            return
        
        # Select JSON file
        json_path = filedialog.askopenfilename(
            title="Select Preset JSON File",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
        )
        
        if not json_path:
            return
        
        # Show import dialog
        self.show_import_dialog(json_path)
        
    def show_import_dialog(self, json_path):
        """Show dialog for importing preset from JSON"""
        import json
        
        # Load JSON to show available presets
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            if 'presets' not in data or len(data['presets']) == 0:
                messagebox.showerror("Error", "No presets found in JSON file")
                return
            
            presets = data['presets']
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load JSON file:\n{str(e)}")
            return
        
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Import Preset from JSON")
        dialog.geometry("600x300")
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"600x300+{x}+{y}")
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            frame,
            text=f"Import from: {os.path.basename(json_path)}",
            font=("Segoe UI", 11, "bold"),
        ).grid(row=0, column=0, columnspan=3, pady=(0, 15))
        
        # Preset selection
        ttk.Label(frame, text="Select Preset from JSON:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        preset_var = tk.StringVar()
        preset_options = []
        for i, preset_entry in enumerate(presets):
            slot = preset_entry.get('slot', i)
            preset_data = preset_entry.get('data', {})
            body_type = "Type A" if preset_data.get('body_type', 0) == 0 else "Type B"
            preset_options.append(f"Preset {i+1} (Original Slot {slot+1}, {body_type})")
        
        preset_combo = ttk.Combobox(frame, textvariable=preset_var, values=preset_options, state="readonly", width=40)
        preset_combo.grid(row=1, column=1, columnspan=2, padx=5)
        preset_combo.current(0)
        
        ttk.Label(frame, text="Destination Slot (1-15):").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        dest_slot_var = tk.StringVar(value="1")
        dest_slot_entry = ttk.Entry(frame, textvariable=dest_slot_var, width=10)
        dest_slot_entry.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        def do_import():
            try:
                # Get selected preset index
                preset_index = preset_combo.current() + 1  # 1-based for user
                
                dest_slot = int(dest_slot_var.get())
                if dest_slot < 1 or dest_slot > 15:
                    messagebox.showerror("Error", "Slot must be between 1 and 15")
                    return
                
                # Import preset
                success = self.current_save.import_preset_from_json(
                    json_path, preset_index - 1, dest_slot - 1
                )
                
                if success:
                    # Create backup
                    import shutil
                    backup_path = self.current_save_path + ".backup"
                    shutil.copy2(self.current_save_path, backup_path)
                    
                    # Save modified file
                    self.current_save.save(self.current_save_path)
                    
                    # Reload presets to show changes
                    self.current_save = Save.from_file(self.current_save_path)
                    self.presets = self.current_save.get_character_presets()
                    self.populate_preset_list()
                    
                    messagebox.showinfo(
                        "Import Successful",
                        f"Preset imported successfully to slot {dest_slot}!\n\n"
                        f"Backup created: {os.path.basename(backup_path)}"
                    )
                    dialog.destroy()
                else:
                    messagebox.showerror(
                        "Import Failed",
                        "Failed to import preset.\n\n"
                        "Check that the JSON file is valid and the slot is available."
                    )
                    
            except ValueError:
                messagebox.showerror("Error", "Invalid slot number - must be an integer (1-15)")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import preset:\n{str(e)}")
                import traceback
                traceback.print_exc()
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(15, 0))
        
        ttk.Button(
            button_frame, text="Import Preset", command=do_import, width=15, style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, text="Cancel", command=dialog.destroy, width=15
        ).pack(side=tk.LEFT, padx=5)
            
    def copy_preset(self):
        """Copy selected preset to another save file"""
        if self.selected_slot is None:
            messagebox.showerror("No Selection", "Please select a preset to copy!")
            return
        
        # Show copy dialog
        self.show_copy_dialog()
        
    def show_copy_dialog(self):
        """Show dialog for copying preset"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Copy Preset to Another Save")
        dialog.geometry("600x220")
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"600x220+{x}+{y}")
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            frame,
            text=f"Copy preset from Slot {self.selected_slot + 1}",
            font=("Segoe UI", 11, "bold"),
        ).grid(row=0, column=0, columnspan=3, pady=(0, 15))
        
        ttk.Label(frame, text="Destination Save File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        dest_path_var = tk.StringVar()
        dest_entry = ttk.Entry(frame, textvariable=dest_path_var, width=45)
        dest_entry.grid(row=1, column=1, padx=5)
        
        def browse_dest():
            filename = filedialog.askopenfilename(
                title="Select Destination Save File",
                initialdir=self.default_save_path,
                filetypes=[("Elden Ring Saves", "*.sl2 *.co2"), ("All Files", "*.*")],
            )
            if filename:
                dest_path_var.set(filename)
        
        ttk.Button(
            frame, text="Browse", command=browse_dest, style="Accent.TButton"
        ).grid(row=1, column=2, padx=5)
        
        ttk.Label(frame, text="Destination Slot (1-15):").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        dest_slot_var = tk.StringVar(value="1")
        dest_slot_entry = ttk.Entry(frame, textvariable=dest_slot_var, width=10)
        dest_slot_entry.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        def do_copy():
            dest_path = dest_path_var.get()
            if not dest_path or not os.path.exists(dest_path):
                messagebox.showerror("Error", "Please select a valid destination save file")
                return
            
            try:
                dest_slot = int(dest_slot_var.get())
                if dest_slot < 1 or dest_slot > 15:
                    messagebox.showerror("Error", "Slot must be between 1 and 15")
                    return
                
                # Load destination save
                dest_save = Save.from_file(dest_path)
                
                # Copy preset
                success = dest_save.copy_preset_to_save(
                    self.current_save, self.selected_slot, dest_slot - 1
                )
                
                if success:
                    # Create backup
                    backup_path = dest_path + ".backup"
                    shutil.copy2(dest_path, backup_path)
                    
                    # Save modified file
                    dest_save.save(dest_path)
                    
                    messagebox.showinfo(
                        "Copy Successful",
                        f"Preset copied successfully!\n\n"
                        f"From: Slot {self.selected_slot + 1}\n"
                        f"To: {os.path.basename(dest_path)} - Slot {dest_slot}\n\n"
                        f"Backup created: {os.path.basename(backup_path)}"
                    )
                    dialog.destroy()
                else:
                    messagebox.showerror(
                        "Copy Failed",
                        "Failed to copy preset.\n\n"
                        "Possible reasons:\n"
                        "- Source preset slot is empty\n"
                        "- Invalid slot numbers"
                    )
                    
            except ValueError:
                messagebox.showerror("Error", "Invalid slot number - must be an integer (1-15)")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy preset:\n{str(e)}")
                import traceback
                traceback.print_exc()
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(15, 0))
        
        ttk.Button(
            button_frame, text="Copy Preset", command=do_copy, width=15, style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, text="Cancel", command=dialog.destroy, width=15
        ).pack(side=tk.LEFT, padx=5)


def main():
    root = tk.Tk()
    app = PresetManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()