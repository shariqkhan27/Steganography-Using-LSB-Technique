"""
Standard Tkinter GUI Interface
Professional user interface using built-in tkinter (no additional dependencies)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import os
from encoder import SteganographyEncoder
from decoder import SteganographyDecoder
from utils import SteganographyUtils

class SteganographyApp:
    """Main GUI Application with Standard Tkinter"""
    
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("🔐 Advanced Steganography System v2.0")
        self.window.geometry("1200x800")
        self.window.configure(bg='#2b2b2b')
        
        # Configure style
        self.setup_styles()
        
        # Initialize components
        self.encoder = SteganographyEncoder()
        self.decoder = SteganographyDecoder()
        self.utils = SteganographyUtils()
        
        # State variables
        self.carrier_image = None
        self.stego_image = None
        
        self.setup_ui()
    
    def setup_styles(self):
        """Configure ttk styles for dark theme"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure colors
        bg_color = '#2b2b2b'
        fg_color = '#ffffff'
        accent_color = '#0078d4'
        
        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TLabel', background=bg_color, foreground=fg_color, font=('Helvetica', 12))
        self.style.configure('TButton', 
                           background=accent_color, 
                           foreground=fg_color,
                           font=('Helvetica', 11),
                           padding=10)
        self.style.map('TButton',
                      background=[('active', '#005a9e')])
        
        self.style.configure('Title.TLabel', 
                           font=('Helvetica', 24, 'bold'),
                           foreground='#00ff00')
        
        self.style.configure('Subtitle.TLabel', 
                           font=('Helvetica', 14, 'bold'),
                           foreground=accent_color)
        
        self.style.configure('TNotebook', background=bg_color)
        self.style.configure('TNotebook.Tab', 
                           background='#3c3c3c',
                           foreground=fg_color,
                           padding=[20, 10],
                           font=('Helvetica', 11, 'bold'))
        self.style.map('TNotebook.Tab',
                      background=[('selected', accent_color)],
                      foreground=[('selected', fg_color)])
    
    def setup_ui(self):
        """Setup modern UI components"""
        
        # Main container
        self.main_frame = ttk.Frame(self.window)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title with decorative elements
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(fill="x", pady=10)
        
        title = ttk.Label(
            title_frame,
            text="🔐 Advanced Steganography System",
            style='Title.TLabel'
        )
        title.pack()
        
        subtitle = ttk.Label(
            title_frame,
            text="Secure Message Hiding in Images • AES-256-GCM Encryption",
            style='Subtitle.TLabel'
        )
        subtitle.pack()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add tabs
        encode_frame = ttk.Frame(self.notebook)
        decode_frame = ttk.Frame(self.notebook)
        analysis_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(encode_frame, text="  🔒 Encode  ")
        self.notebook.add(decode_frame, text="  🔓 Decode  ")
        self.notebook.add(analysis_frame, text="  🔬 Analysis  ")
        
        self.setup_encode_tab(encode_frame)
        self.setup_decode_tab(decode_frame)
        self.setup_analysis_tab(analysis_frame)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            self.main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=('Helvetica', 10)
        )
        status_bar.pack(fill="x", pady=(5, 0))
    
    def setup_encode_tab(self, parent):
        """Setup encoding interface"""
        
        # Paned window for left/right split
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left frame for inputs
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # Canvas with scrollbar for left frame
        left_canvas = tk.Canvas(left_frame, bg='#2b2b2b', highlightthickness=0)
        left_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=left_canvas.yview)
        left_scrollable = ttk.Frame(left_canvas)
        
        left_scrollable.bind(
            "<Configure>",
            lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all"))
        )
        
        left_canvas.create_window((0, 0), window=left_scrollable, anchor="nw")
        left_canvas.configure(yscrollcommand=left_scrollbar.set)
        
        # Title
        ttk.Label(left_scrollable, text="📁 Input Configuration", 
                 style='Subtitle.TLabel').pack(pady=10)
        
        # Image selection frame
        img_frame = ttk.LabelFrame(left_scrollable, text="Carrier Image", padding=10)
        img_frame.pack(fill="x", padx=10, pady=5)
        
        self.carrier_path_var = tk.StringVar()
        carrier_entry = ttk.Entry(img_frame, textvariable=self.carrier_path_var, 
                                  font=('Courier', 10), width=40)
        carrier_entry.pack(fill="x", pady=5)
        
        browse_btn = tk.Button(
            img_frame, 
            text="📂 Browse Image",
            command=self.browse_carrier_image,
            bg='#0078d4',
            fg='white',
            font=('Helvetica', 10, 'bold'),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        browse_btn.pack(pady=5)
        
        # Image preview
        self.image_preview = ttk.Label(img_frame, text="No image selected", 
                                       background='#3c3c3c', 
                                       foreground='#888888',
                                       font=('Helvetica', 10))
        self.image_preview.pack(pady=10)
        
        # Message frame
        msg_frame = ttk.LabelFrame(left_scrollable, text="Secret Message", padding=10)
        msg_frame.pack(fill="both", padx=10, pady=5)
        
        self.message_text = tk.Text(msg_frame, height=6, width=40, 
                                    font=('Courier', 10),
                                    bg='#3c3c3c', 
                                    fg='white',
                                    insertbackground='white',
                                    relief=tk.FLAT,
                                    padx=5,
                                    pady=5)
        self.message_text.pack(fill="both", pady=5)
        
        # Character count
        self.char_count_var = tk.StringVar(value="Characters: 0")
        ttk.Label(msg_frame, textvariable=self.char_count_var, 
                 font=('Helvetica', 9)).pack()
        
        self.message_text.bind('<KeyRelease>', self.update_char_count)
        
        # Password frame
        pwd_frame = ttk.LabelFrame(left_scrollable, text="🔑 Encryption Password", padding=10)
        pwd_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(pwd_frame, text="Password:").pack(anchor="w")
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(
            pwd_frame, 
            textvariable=self.password_var,
            show="•", 
            font=('Courier', 11)
        )
        password_entry.pack(fill="x", pady=2)
        
        ttk.Label(pwd_frame, text="Confirm Password:").pack(anchor="w", pady=(10,0))
        self.confirm_password_var = tk.StringVar()
        confirm_entry = ttk.Entry(
            pwd_frame, 
            textvariable=self.confirm_password_var,
            show="•", 
            font=('Courier', 11)
        )
        confirm_entry.pack(fill="x", pady=2)
        
        # Password strength indicator
        self.pwd_strength_var = tk.StringVar(value="")
        ttk.Label(pwd_frame, textvariable=self.pwd_strength_var, 
                 font=('Helvetica', 9), foreground='#ff4444').pack()
        
        password_entry.bind('<KeyRelease>', self.check_password_strength)
        
        # Encode button
        encode_btn = tk.Button(
            left_scrollable, 
            text="🔒 ENCODE MESSAGE",
            command=self.encode_message,
            bg='#28a745',
            fg='white',
            font=('Helvetica', 12, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        encode_btn.pack(pady=20)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            left_scrollable, 
            variable=self.progress_var,
            mode='determinate'
        )
        self.progress_bar.pack(fill="x", padx=20, pady=5)
        
        left_canvas.pack(side="left", fill="both", expand=True)
        left_scrollbar.pack(side="right", fill="y")
        
        # Right frame for output
        right_frame = ttk.LabelFrame(paned, text="📤 Output", padding=10)
        paned.add(right_frame, weight=1)
        
        # Output preview
        ttk.Label(right_frame, text="Stego Image Preview:", 
                 font=('Helvetica', 11, 'bold')).pack(pady=5)
        
        self.output_preview_frame = ttk.Frame(right_frame)
        self.output_preview_frame.pack(pady=10)
        
        self.output_preview = ttk.Label(self.output_preview_frame, 
                                        text="No output yet",
                                        background='#3c3c3c',
                                        foreground='#888888')
        self.output_preview.pack()
        
        # Statistics
        ttk.Label(right_frame, text="📊 Encoding Statistics:", 
                 font=('Helvetica', 11, 'bold')).pack(pady=10)
        
        self.stats_text = scrolledtext.ScrolledText(
            right_frame, 
            height=12, 
            width=40,
            bg='#3c3c3c',
            fg='#00ff00',
            font=('Courier', 10),
            relief=tk.FLAT
        )
        self.stats_text.pack(fill="both", expand=True, pady=5)
        
        # Action buttons
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill="x", pady=10)
        
        save_btn = tk.Button(
            btn_frame,
            text="💾 Save Stego Image",
            command=self.save_stego_image,
            bg='#17a2b8',
            fg='white',
            font=('Helvetica', 10, 'bold'),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        save_btn.pack(side="left", padx=5)
        
        clear_btn = tk.Button(
            btn_frame,
            text="🗑️ Clear All",
            command=self.clear_encode_tab,
            bg='#6c757d',
            fg='white',
            font=('Helvetica', 10, 'bold'),
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        clear_btn.pack(side="right", padx=5)
    
    def setup_decode_tab(self, parent):
        """Setup decoding interface"""
        
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left frame
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # Stego image selection
        img_frame = ttk.LabelFrame(left_frame, text="Stego Image", padding=10)
        img_frame.pack(fill="both", padx=10, pady=10)
        
        self.stego_path_var = tk.StringVar()
        stego_entry = ttk.Entry(img_frame, textvariable=self.stego_path_var, 
                               font=('Courier', 10))
        stego_entry.pack(fill="x", pady=5)
        
        browse_btn = tk.Button(
            img_frame, 
            text="📂 Browse Stego Image",
            command=self.browse_stego_image,
            bg='#0078d4',
            fg='white',
            font=('Helvetica', 10, 'bold'),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        browse_btn.pack(pady=5)
        
        # Stego preview
        self.stego_preview_frame = ttk.Frame(img_frame)
        self.stego_preview_frame.pack(pady=10)
        
        self.stego_preview = ttk.Label(self.stego_preview_frame, 
                                       text="No image selected",
                                       background='#3c3c3c',
                                       foreground='#888888')
        self.stego_preview.pack()
        
        # Password
        pwd_frame = ttk.LabelFrame(left_frame, text="🔑 Decryption Password", padding=10)
        pwd_frame.pack(fill="x", padx=10, pady=10)
        
        self.decode_password_var = tk.StringVar()
        decode_password_entry = ttk.Entry(
            pwd_frame, 
            textvariable=self.decode_password_var,
            show="•", 
            font=('Courier', 11)
        )
        decode_password_entry.pack(fill="x", pady=5)
        
        # Show password checkbox
        self.show_pwd_var = tk.BooleanVar()
        show_pwd_cb = ttk.Checkbutton(
            pwd_frame,
            text="Show password",
            variable=self.show_pwd_var,
            command=lambda: decode_password_entry.configure(
                show="" if self.show_pwd_var.get() else "•"
            )
        )
        show_pwd_cb.pack(pady=5)
        
        # Decode button
        decode_btn = tk.Button(
            left_frame, 
            text="🔓 DECODE MESSAGE",
            command=self.decode_message,
            bg='#dc3545',
            fg='white',
            font=('Helvetica', 12, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        decode_btn.pack(pady=20)
        
        # Right frame for output
        right_frame = ttk.LabelFrame(paned, text="📥 Extracted Message", padding=10)
        paned.add(right_frame, weight=1)
        
        # Message display
        ttk.Label(right_frame, text="Decrypted Message:", 
                 font=('Helvetica', 11, 'bold')).pack(anchor="w", pady=5)
        
        message_display_frame = ttk.Frame(right_frame)
        message_display_frame.pack(fill="both", expand=True, pady=5)
        
        self.extracted_message = scrolledtext.ScrolledText(
            message_display_frame, 
            height=10,
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Courier', 11, 'bold'),
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.extracted_message.pack(fill="both", expand=True)
        
        # Metadata display
        ttk.Label(right_frame, text="📋 Metadata:", 
                 font=('Helvetica', 11, 'bold')).pack(anchor="w", pady=(10,5))
        
        self.metadata_text = scrolledtext.ScrolledText(
            right_frame, 
            height=8,
            bg='#3c3c3c',
            fg='#adb5bd',
            font=('Courier', 9),
            relief=tk.FLAT
        )
        self.metadata_text.pack(fill="both", pady=5)
        
        # Copy button
        copy_btn = tk.Button(
            right_frame,
            text="📋 Copy Message",
            command=self.copy_extracted_message,
            bg='#6c757d',
            fg='white',
            font=('Helvetica', 10),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        copy_btn.pack(pady=5)
    
    def setup_analysis_tab(self, parent):
        """Setup analysis tab"""
        
        # Analysis tools frame
        tools_frame = ttk.LabelFrame(parent, text="🔬 Analysis Tools", padding=20)
        tools_frame.pack(fill="x", padx=20, pady=20)
        
        # Tool buttons
        btn_frame = ttk.Frame(tools_frame)
        btn_frame.pack()
        
        tools = [
            ("📊 Check Image Capacity", self.check_capacity, '#0078d4'),
            ("🔍 Detect Hidden Data", self.detect_hidden_data, '#6f42c1'),
            ("📸 Compare Images", self.compare_images, '#fd7e14'),
            ("📈 Statistical Analysis", self.statistical_analysis, '#20c997')
        ]
        
        for text, command, color in tools:
            btn = tk.Button(
                btn_frame,
                text=text,
                command=command,
                bg=color,
                fg='white',
                font=('Helvetica', 11, 'bold'),
                relief=tk.FLAT,
                padx=20,
                pady=10,
                width=25,
                cursor='hand2'
            )
            btn.pack(side="left", padx=5)
        
        # Results area
        results_frame = ttk.LabelFrame(parent, text="📋 Analysis Results", padding=10)
        results_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.analysis_text = scrolledtext.ScrolledText(
            results_frame, 
            height=20,
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Courier', 10),
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.analysis_text.pack(fill="both", expand=True)
        
        # Clear button
        clear_btn = tk.Button(
            results_frame,
            text="🗑️ Clear Results",
            command=lambda: self.analysis_text.delete(1.0, tk.END),
            bg='#6c757d',
            fg='white',
            font=('Helvetica', 10),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        clear_btn.pack(pady=5)
    
    # UI Helper Methods
    def update_char_count(self, event=None):
        """Update character count for message"""
        count = len(self.message_text.get("1.0", "end-1c"))
        self.char_count_var.set(f"Characters: {count}")
    
    def check_password_strength(self, event=None):
        """Check and display password strength"""
        password = self.password_var.get()
        
        if len(password) == 0:
            strength = ""
            color = '#ff4444'
        elif len(password) < 4:
            strength = "Weak"
            color = '#ff4444'
        elif len(password) < 8:
            strength = "Medium"
            color = '#ffaa00'
        else:
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_special = any(not c.isalnum() for c in password)
            
            if has_upper and has_lower and has_digit and has_special:
                strength = "Strong"
                color = '#00ff00'
            elif (has_upper or has_lower) and has_digit:
                strength = "Good"
                color = '#88ff00'
            else:
                strength = "Fair"
                color = '#ffaa00'
        
        self.pwd_strength_var.set(f"Strength: {strength}")
        # Update label color (using configure)
        for child in self.window.winfo_children():
            if isinstance(child, ttk.Label):
                if child.cget('textvariable') == str(self.pwd_strength_var):
                    child.configure(foreground=color)
    
    def clear_encode_tab(self):
        """Clear all fields in encode tab"""
        self.carrier_path_var.set("")
        self.message_text.delete("1.0", tk.END)
        self.password_var.set("")
        self.confirm_password_var.set("")
        self.image_preview.configure(image="", text="No image selected")
        self.output_preview.configure(image="", text="No output yet")
        self.stats_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.carrier_image = None
        self.stego_image = None
        self.status_var.set("Cleared all fields")
    
    def copy_extracted_message(self):
        """Copy extracted message to clipboard"""
        message = self.extracted_message.get(1.0, tk.END).strip()
        if message:
            self.window.clipboard_clear()
            self.window.clipboard_append(message)
            self.status_var.set("Message copied to clipboard!")
    
    # Image handling methods
    def browse_carrier_image(self):
        """Browse and load carrier image"""
        filepath = filedialog.askopenfilename(
            title="Select Carrier Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff"),
                ("All files", "*.*")
            ]
        )
        if filepath:
            self.carrier_path_var.set(filepath)
            self.display_image(filepath, self.image_preview, size=(150, 150))
            self.carrier_image = filepath
            self.status_var.set(f"Loaded carrier image: {os.path.basename(filepath)}")
    
    def browse_stego_image(self):
        """Browse and load stego image"""
        filepath = filedialog.askopenfilename(
            title="Select Stego Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff"),
                ("All files", "*.*")
            ]
        )
        if filepath:
            self.stego_path_var.set(filepath)
            self.display_image(filepath, self.stego_preview, size=(150, 150))
            self.stego_image = filepath
            self.status_var.set(f"Loaded stego image: {os.path.basename(filepath)}")
    
    def display_image(self, path, label_widget, size=(200, 200)):
        """Display image preview"""
        try:
            img = Image.open(path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label_widget.configure(image=photo, text="")
            label_widget.image = photo
        except Exception as e:
            label_widget.configure(text=f"Error loading image")
            self.status_var.set(f"Error: {str(e)}")
    
    # Core functionality methods
    def encode_message(self):
        """Handle message encoding"""
        if not self.carrier_image:
            messagebox.showerror("Error", "Please select a carrier image")
            return
        
        message = self.message_text.get("1.0", "end-1c")
        if not message:
            messagebox.showerror("Error", "Please enter a message to hide")
            return
        
        password = self.password_var.get()
        if not password or len(password) < 4:
            messagebox.showerror("Error", "Password must be at least 4 characters")
            return
        
        if password != self.confirm_password_var.get():
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        try:
            # Ask where to save BEFORE encoding starts
            output_path = filedialog.asksaveasfilename(
                title="Save Encoded Image As",
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                initialfile="stego_output.png"
            )
            if not output_path:
                self.status_var.set("Encoding cancelled.")
                return  # User hit Cancel

            self.progress_var.set(30)
            self.status_var.set("Encoding message...")
            self.window.update()

            # Encode directly to the chosen path
            stats = self.encoder.encode(
                self.carrier_image,
                message,
                password,
                output_path
            )

            self.progress_var.set(100)

            # Update UI - encoder may have appended .png
            self.stego_image = stats['output_path']
            self.display_image(self.stego_image, self.output_preview)

            # Show statistics
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, "\u2554" + "\u2550"*32 + "\u2557\n")
            self.stats_text.insert(tk.END, "\u2551   \u2705 ENCODING SUCCESSFUL!     \u2551\n")
            self.stats_text.insert(tk.END, "\u255a" + "\u2550"*32 + "\u255d\n\n")
            self.stats_text.insert(tk.END, f"\U0001f4dd Message Length: {stats['message_length']} characters\n")
            self.stats_text.insert(tk.END, f"\U0001f4e6 Payload Size: {stats['payload_size']} bytes\n")
            self.stats_text.insert(tk.END, f"\U0001f4be Capacity Used: {stats['capacity_used']}\n")
            self.stats_text.insert(tk.END, f"\U0001f522 Bits Embedded: {stats['bits_embedded']}\n")
            self.stats_text.insert(tk.END, f"\U0001f4c1 Saved to: {stats['output_path']}\n")

            self.status_var.set(f"\u2705 Saved to: {stats['output_path']}")
            messagebox.showinfo(
                "Success",
                f"Message encoded and saved!\n\n\U0001f4c1 {stats['output_path']}"
            )
            
        except Exception as e:
            messagebox.showerror("Encoding Error", str(e))
            self.progress_var.set(0)
            self.status_var.set(f"Error: {str(e)}")
    
    def decode_message(self):
        """Handle message decoding with self-destruct awareness"""
        if not self.stego_image:
            messagebox.showerror("Error", "Please select a stego image")
            return

        password = self.decode_password_var.get()
        if not password:
            messagebox.showerror("Error", "Please enter the decryption password")
            return

        try:
            self.status_var.set("Decoding message...")
            self.window.update()

            # Clear previous results
            self.extracted_message.delete(1.0, tk.END)
            self.metadata_text.delete(1.0, tk.END)

            # Decode
            result = self.decoder.decode(self.stego_image, password)

            if result['success']:
                # ── Success ──────────────────────────────────────────────
                self.extracted_message.configure(fg='#00ff00')
                self.extracted_message.insert(1.0, result['message'])

                if result.get('metadata') and len(result['metadata']) > 0:
                    import json
                    self.metadata_text.insert(1.0, json.dumps(result['metadata'], indent=2))
                else:
                    self.metadata_text.insert(1.0, "No metadata found in this image")

                self.status_var.set("✅ Message decoded successfully!")
                messagebox.showinfo(
                    "Success",
                    f"Message extracted successfully!\n\nLength: {len(result['message'])} characters"
                )

            else:
                error_msg = result.get('error', 'Unknown error')

                if result.get('destroyed'):
                    # ── Self-destruct just fired ──────────────────────────
                    self._show_destruct_ui(error_msg)
                elif '🔥 SELF-DESTRUCT' in error_msg or 'permanently destroyed' in error_msg:
                    # ── Already poisoned (previous attempt) ──────────────
                    self._show_destruct_ui(error_msg)
                else:
                    # ── Generic error ─────────────────────────────────────
                    self.extracted_message.configure(fg='#ff4444')
                    self.extracted_message.insert(1.0, f"❌ ERROR:\n\n{error_msg}")
                    self.metadata_text.insert(1.0, "Decoding failed — see error message")
                    self.status_var.set("❌ Decoding failed")
                    messagebox.showerror("Decoding Error", error_msg)

        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"An unexpected error occurred:\n\n{str(e)}")
            self.status_var.set("Error during decoding")

    def _show_destruct_ui(self, error_msg: str):
        """Flash the UI red and show the self-destruct warning."""
        # Turn message area red with warning text
        self.extracted_message.configure(fg='#ff2222', bg='#1a0000')
        self.extracted_message.delete(1.0, tk.END)
        self.extracted_message.insert(
            1.0,
            "💀 MESSAGE PERMANENTLY DESTROYED 💀\n\n"
            "The hidden data has been overwritten with\n"
            "random noise and cannot be recovered.\n\n"
            "This image is now a clean carrier."
        )
        self.metadata_text.delete(1.0, tk.END)
        self.metadata_text.insert(1.0, "⚠️  Self-destruct was triggered by a wrong password.\n"
                                        "All payload data has been erased from this image.")
        self.status_var.set("💀 SELF-DESTRUCT TRIGGERED — data permanently erased")

        # Flash window title briefly
        original_title = self.window.title()
        self.window.title("🔥 SELF-DESTRUCT TRIGGERED — DATA DESTROYED")
        self.window.configure(bg='#3a0000')
        self.window.after(3000, lambda: self.window.title(original_title))
        self.window.after(3000, lambda: self.window.configure(bg='#2b2b2b'))

        messagebox.showerror(
            "🔥 SELF-DESTRUCT ACTIVATED",
            "WRONG PASSWORD DETECTED\n\n"
            "The hidden message has been permanently erased.\n"
            "The image LSBs have been overwritten with random noise.\n\n"
            "No further recovery is possible."
        )
    
    def save_stego_image(self):
        """Save stego image to chosen location"""
        if not self.stego_image:
            messagebox.showerror("Error", "No stego image to save")
            return
        
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if save_path:
            try:
                import shutil
                shutil.copy2(self.stego_image, save_path)
                self.status_var.set(f"Image saved to: {save_path}")
                messagebox.showinfo("Success", f"Image saved to: {save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def check_capacity(self):
        """Check image capacity"""
        filepath = filedialog.askopenfilename(
            title="Select Image for Analysis",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        
        if filepath:
            try:
                capacity = self.utils.calculate_capacity(filepath)
                
                self.analysis_text.delete(1.0, tk.END)
                self.analysis_text.insert(tk.END, "╔══════════════════════════════════╗\n")
                self.analysis_text.insert(tk.END, "║  IMAGE CAPACITY ANALYSIS        ║\n")
                self.analysis_text.insert(tk.END, "╚══════════════════════════════════╝\n\n")
                self.analysis_text.insert(tk.END, f"📏 Dimensions: {capacity['image_size']}\n")
                self.analysis_text.insert(tk.END, f"🔢 Total Pixels: {capacity['pixels']:,}\n")
                self.analysis_text.insert(tk.END, f"🎨 Color Channels: {capacity['channels']}\n")
                self.analysis_text.insert(tk.END, f"📊 Total Bits: {capacity['total_bits']:,}\n")
                self.analysis_text.insert(tk.END, f"💾 Total Bytes: {capacity['total_bytes']:,}\n")
                self.analysis_text.insert(tk.END, f"📋 Metadata Overhead: {capacity['metadata_overhead']} bytes\n")
                self.analysis_text.insert(tk.END, f"\n📝 MAXIMUM CAPACITY:\n")
                self.analysis_text.insert(tk.END, f"   Usable Bytes: {capacity['usable_bytes']:,}\n")
                self.analysis_text.insert(tk.END, f"   Max Characters: {capacity['max_characters']:,}\n")
                
                self.status_var.set(f"Capacity analysis complete for {os.path.basename(filepath)}")
                
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def detect_hidden_data(self):
        """Detect if image contains hidden data (and whether it has been destroyed)"""
        filepath = filedialog.askopenfilename(
            title="Select Image for Detection",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )

        if filepath:
            try:
                self.status_var.set("Scanning for hidden data...")
                self.window.update()

                detection = self.decoder.detect_hidden_data(filepath)

                self.analysis_text.delete(1.0, tk.END)
                self.analysis_text.insert(tk.END, "╔══════════════════════════════════╗\n")
                self.analysis_text.insert(tk.END, "║  STEGANALYSIS DETECTION         ║\n")
                self.analysis_text.insert(tk.END, "╚══════════════════════════════════╝\n\n")
                self.analysis_text.insert(tk.END, f"File: {os.path.basename(filepath)}\n\n")

                if detection['poisoned']:
                    self.analysis_text.insert(tk.END, "💀 SELF-DESTRUCT WAS TRIGGERED\n\n")
                    self.analysis_text.insert(tk.END, detection['message'] + "\n")
                    self.analysis_text.insert(tk.END, "\nThe image once contained hidden data,\n")
                    self.analysis_text.insert(tk.END, "but a wrong password destroyed it.\n")
                    self.status_var.set("💀 Destroyed steganographic data found")
                elif detection['found']:
                    self.analysis_text.insert(tk.END, "⚠️  ACTIVE HIDDEN DATA DETECTED!\n\n")
                    self.analysis_text.insert(tk.END, detection['message'] + "\n")
                    self.analysis_text.insert(tk.END, "\nIntegrity flag: ALIVE ✅\n")
                    self.analysis_text.insert(tk.END, "Magic number 'STEG' confirmed in LSB data.\n")
                    self.status_var.set("⚠️ Active hidden data detected!")
                else:
                    self.analysis_text.insert(tk.END, "✅ NO HIDDEN DATA DETECTED\n\n")
                    self.analysis_text.insert(tk.END, detection['message'] + "\n")
                    self.analysis_text.insert(tk.END, "\nThe image appears to be a clean carrier.\n")
                    self.status_var.set("No hidden data found")

            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def compare_images(self):
        """Compare original and stego images"""
        filepath1 = filedialog.askopenfilename(
            title="Select Original Image",
            filetypes=[("Image files", "*.*")]
        )
        
        if not filepath1:
            return
        
        filepath2 = filedialog.askopenfilename(
            title="Select Stego Image",
            filetypes=[("Image files", "*.*")]
        )
        
        if filepath2:
            try:
                self.status_var.set("Comparing images...")
                self.window.update()
                
                diff = self.utils.image_difference(filepath1, filepath2)
                
                self.analysis_text.delete(1.0, tk.END)
                self.analysis_text.insert(tk.END, "╔══════════════════════════════════╗\n")
                self.analysis_text.insert(tk.END, "║  IMAGE COMPARISON ANALYSIS      ║\n")
                self.analysis_text.insert(tk.END, "╚══════════════════════════════════╝\n\n")
                self.analysis_text.insert(tk.END, f"📊 Max Pixel Difference: {diff['max_pixel_diff']}\n")
                self.analysis_text.insert(tk.END, f"📈 Mean Difference: {diff['mean_pixel_diff']:.6f}\n")
                self.analysis_text.insert(tk.END, f"📉 Std Deviation: {diff['std_pixel_diff']:.6f}\n")
                self.analysis_text.insert(tk.END, f"🎯 Pixels Changed: {diff['pixels_changed']:,}\n")
                self.analysis_text.insert(tk.END, f"📊 Change Percentage: {diff['percent_changed']:.4f}%\n\n")
                
                if diff['max_pixel_diff'] <= 1:
                    self.analysis_text.insert(tk.END, "✅ Images are VISUALLY IDENTICAL\n")
                    self.analysis_text.insert(tk.END, "   Changes are imperceptible to human eye.\n")
                elif diff['max_pixel_diff'] <= 5:
                    self.analysis_text.insert(tk.END, "⚠️  MINOR differences detected\n")
                    self.analysis_text.insert(tk.END, "   Slight variations may be noticeable.\n")
                else:
                    self.analysis_text.insert(tk.END, "❌ SIGNIFICANT differences detected\n")
                    self.analysis_text.insert(tk.END, "   Images are noticeably different.\n")
                
                self.status_var.set("Image comparison complete")
                    
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def statistical_analysis(self):
        """Perform statistical analysis on image"""
        filepath = filedialog.askopenfilename(
            title="Select Image for Statistical Analysis",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
        )
        
        if filepath:
            try:
                from PIL import Image
                import numpy as np
                
                img = Image.open(filepath)
                if img.mode not in ['RGB', 'RGBA']:
                    img = img.convert('RGB')
                
                img_array = np.array(img)
                
                self.analysis_text.delete(1.0, tk.END)
                self.analysis_text.insert(tk.END, "╔══════════════════════════════════╗\n")
                self.analysis_text.insert(tk.END, "║  STATISTICAL ANALYSIS            ║\n")
                self.analysis_text.insert(tk.END, "╚══════════════════════════════════╝\n\n")
                
                # Basic statistics
                self.analysis_text.insert(tk.END, "📊 BASIC STATISTICS:\n")
                self.analysis_text.insert(tk.END, f"   Mean pixel value: {np.mean(img_array):.2f}\n")
                self.analysis_text.insert(tk.END, f"   Median pixel value: {np.median(img_array):.2f}\n")
                self.analysis_text.insert(tk.END, f"   Std deviation: {np.std(img_array):.2f}\n")
                self.analysis_text.insert(tk.END, f"   Min pixel value: {np.min(img_array)}\n")
                self.analysis_text.insert(tk.END, f"   Max pixel value: {np.max(img_array)}\n\n")
                
                # LSB analysis
                lsb_array = img_array & 1
                lsb_mean = np.mean(lsb_array)
                lsb_std = np.std(lsb_array)
                
                self.analysis_text.insert(tk.END, "🔍 LSB ANALYSIS:\n")
                self.analysis_text.insert(tk.END, f"   LSB Mean: {lsb_mean:.4f}\n")
                self.analysis_text.insert(tk.END, f"   LSB Std Dev: {lsb_std:.4f}\n")
                
                # Check for anomalies
                if abs(lsb_mean - 0.5) > 0.1:
                    self.analysis_text.insert(tk.END, "   ⚠️  LSB distribution is ABNORMAL\n")
                    self.analysis_text.insert(tk.END, "   This may indicate hidden data!\n")
                else:
                    self.analysis_text.insert(tk.END, "   ✅ LSB distribution appears NORMAL\n")
                
                self.status_var.set(f"Statistical analysis complete for {os.path.basename(filepath)}")
                
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def run(self):
        """Run the application"""
        self.window.mainloop()

if __name__ == "__main__":
    app = SteganographyApp()
    app.run()