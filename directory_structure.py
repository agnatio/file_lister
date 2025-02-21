import os
import fnmatch
import sys
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
from tkinter.font import Font

sys.stdout.reconfigure(encoding="utf-8")


def load_gitignore(gitignore_path):
    """Load .gitignore patterns and return them as a list."""
    ignore_patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as gitignore_file:
            for line in gitignore_file:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignore_patterns.append(line)
    return ignore_patterns


def should_ignore(path, ignore_patterns, is_dir=False):
    """Check if a given path matches any ignore pattern."""
    for pattern in ignore_patterns:
        if is_dir:
            if fnmatch.fnmatch(os.path.basename(path) + "/", pattern) or fnmatch.fnmatch(path + "/", pattern):
                return True
        else:
            if fnmatch.fnmatch(os.path.basename(path), pattern) or fnmatch.fnmatch(path, pattern):
                return True
    return False


def list_files(startpath, remove_objects=None, max_levels=None, gitignore=True, output_file=None):
    """Recursively list files and directories in a tree format."""
    remove_objects = remove_objects or []
    ignore_patterns = load_gitignore(os.path.join(
        startpath, ".gitignore")) if gitignore else []
    output_lines = ["./"]

    def write_output(text):
        output_lines.append(text)

    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, "").count(os.sep)
        if max_levels is not None and level > max_levels:
            del dirs[:]  # Prevent deeper traversal
            continue
        dirs[:] = [d for d in dirs if d not in remove_objects and not should_ignore(
            os.path.join(root, d), ignore_patterns, is_dir=True)]
        indent = "│   " * (level - 1) + "├── " if level > 0 else ""
        subindent = "│   " * level + "├── "
        if root != startpath:
            write_output(f"{indent}{os.path.basename(root)}/")
        if not files and not dirs:
            write_output(f"{subindent}(empty)")
        for i, f in enumerate(files):
            if not should_ignore(os.path.join(root, f), ignore_patterns, is_dir=False):
                file_indent = "└── " if i == len(files) - 1 else "├── "
                write_output(f"{subindent}{file_indent}{f}")
    result_text = "\n".join(output_lines)
    if output_file:
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(result_text)
    return result_text


class FileListerApp:
    """Tkinter GUI for file listing script with enhanced styling."""

    def __init__(self, root):
        self.root = root
        self.root.title("File Lister Pro")
        self.root.geometry("900x700")

        # Set a modern color scheme
        self.bg_color = "#f5f5f7"
        self.accent_color = "#0071e3"
        self.secondary_bg = "#ffffff"
        self.text_color = "#333333"
        self.light_accent = "#e6f2ff"

        self.root.configure(bg=self.bg_color)

        # Create custom fonts
        self.header_font = Font(family="Segoe UI", size=11, weight="bold")
        self.normal_font = Font(family="Segoe UI", size=10)
        self.mono_font = Font(family="Consolas", size=10)

        # Configure ttk styles
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use clam as base theme

        # Configure various widget styles
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure(
            "Card.TFrame", background=self.secondary_bg, relief="flat")

        self.style.configure("TLabel",
                             background=self.bg_color,
                             foreground=self.text_color,
                             font=self.normal_font)

        self.style.configure("Header.TLabel",
                             background=self.bg_color,
                             foreground=self.text_color,
                             font=self.header_font)

        self.style.configure("TEntry",
                             fieldbackground=self.secondary_bg,
                             borderwidth=1)

        self.style.map("TEntry",
                       fieldbackground=[("focus", self.light_accent)])

        self.style.configure("TButton",
                             background=self.accent_color,
                             foreground="white",
                             padding=(10, 5),
                             font=self.normal_font)

        self.style.map("TButton",
                       background=[("active", self.accent_color),
                                   ("pressed", "#005bb8")])

        self.style.configure("Secondary.TButton",
                             background="#e0e0e0",
                             foreground=self.text_color)

        self.style.map("Secondary.TButton",
                       background=[("active", "#d0d0d0"),
                                   ("pressed", "#c0c0c0")])

        self.style.configure("TCheckbutton",
                             background=self.bg_color,
                             font=self.normal_font)

        self.style.configure("TSpinbox",
                             arrowsize=13,
                             padding=5)

        # Create menu bar
        self.create_menu_bar()

        # Main container
        main_frame = ttk.Frame(root, style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        title_label = ttk.Label(main_frame,
                                text="File Lister Pro",
                                style="Header.TLabel",
                                font=Font(family="Segoe UI", size=16, weight="bold"))
        title_label.pack(anchor="w", pady=(0, 20))

        # Input container (card-like appearance)
        input_frame = ttk.Frame(main_frame, style="Card.TFrame")
        input_frame.pack(fill=tk.X, padx=2, pady=2)

        # Add a thin border effect
        border_frame = ttk.Frame(input_frame, padding=15)
        border_frame.pack(fill=tk.X, padx=1, pady=1)

        # Grid for form layout
        # Make the entry column expandable
        border_frame.columnconfigure(1, weight=1)

        # Directory selection
        ttk.Label(border_frame,
                  text="Directory:",
                  style="Header.TLabel").grid(row=0, column=0, sticky="w", padx=5, pady=10)

        dir_frame = ttk.Frame(border_frame)
        dir_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
        dir_frame.columnconfigure(0, weight=1)

        self.dir_entry = ttk.Entry(dir_frame, font=self.normal_font)
        self.dir_entry.grid(row=0, column=0, sticky="ew")

        browse_btn = ttk.Button(dir_frame,
                                text="Browse",
                                command=self.browse_directory,
                                style="Secondary.TButton")
        browse_btn.grid(row=0, column=1, padx=(10, 0))

        # Max levels input
        ttk.Label(border_frame,
                  text="Max Depth:",
                  style="Header.TLabel").grid(row=1, column=0, sticky="w", padx=5, pady=10)

        depth_frame = ttk.Frame(border_frame)
        depth_frame.grid(row=1, column=1, sticky="w", padx=5, pady=10)

        self.max_level_var = tk.StringVar(value="")
        self.max_level_spinbox = ttk.Spinbox(
            depth_frame,
            from_=1,
            to=20,
            textvariable=self.max_level_var,
            width=5,
            font=self.normal_font
        )
        self.max_level_spinbox.grid(row=0, column=0)

        ttk.Label(depth_frame,
                  text="(Leave empty for unlimited depth)",
                  foreground="#777777").grid(row=0, column=1, padx=(10, 0))

        # Gitignore checkbox
        ttk.Label(border_frame,
                  text="Options:",
                  style="Header.TLabel").grid(row=2, column=0, sticky="w", padx=5, pady=10)

        options_frame = ttk.Frame(border_frame)
        options_frame.grid(row=2, column=1, sticky="w", padx=5, pady=10)

        self.gitignore_var = tk.BooleanVar(value=True)
        self.gitignore_check = ttk.Checkbutton(
            options_frame,
            text="Respect .gitignore files",
            variable=self.gitignore_var)
        self.gitignore_check.grid(row=0, column=0, padx=(0, 15))

        # Output file selection
        ttk.Label(border_frame,
                  text="Save To File:",
                  style="Header.TLabel").grid(row=3, column=0, sticky="w", padx=5, pady=10)

        output_frame = ttk.Frame(border_frame)
        output_frame.grid(row=3, column=1, sticky="ew", padx=5, pady=10)
        output_frame.columnconfigure(0, weight=1)

        self.output_file_entry = ttk.Entry(output_frame, font=self.normal_font)
        self.output_file_entry.grid(row=0, column=0, sticky="ew")

        browse_output_btn = ttk.Button(output_frame,
                                       text="Browse",
                                       command=self.browse_output_file,
                                       style="Secondary.TButton")
        browse_output_btn.grid(row=0, column=1, padx=(10, 0))

        # Action buttons
        buttons_frame = ttk.Frame(border_frame)
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=(20, 10))

        ttk.Button(buttons_frame,
                   text="Generate Tree",
                   command=self.run_script).grid(row=0, column=0, padx=5)

        ttk.Button(buttons_frame,
                   text="Copy to Clipboard",
                   command=self.copy_to_clipboard,
                   style="Secondary.TButton").grid(row=0, column=1, padx=5)

        ttk.Button(buttons_frame,
                   text="Clear",
                   command=self.clear_output,
                   style="Secondary.TButton").grid(row=0, column=2, padx=5)

        # Results label
        results_label = ttk.Label(main_frame,
                                  text="Directory Structure:",
                                  style="Header.TLabel")
        results_label.pack(anchor="w", pady=(20, 10))

        # Output display - wrapped in a frame for border effect
        output_container = ttk.Frame(main_frame, style="Card.TFrame")
        output_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Customized scrolled text with better styling
        self.output_text = scrolledtext.ScrolledText(
            output_container,
            wrap=tk.NONE,  # No word wrapping for tree display
            font=self.mono_font,
            background=self.secondary_bg,
            foreground=self.text_color,
            borderwidth=1,
            padx=10,
            pady=10
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(main_frame,
                                    textvariable=self.status_var,
                                    foreground="#777777",
                                    font=Font(family="Segoe UI", size=9))
        self.status_bar.pack(fill=tk.X, pady=(10, 0), anchor="w")
        self.status_var.set("Ready")

    def browse_directory(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, folder)

    def browse_output_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            self.output_file_entry.delete(0, tk.END)
            self.output_file_entry.insert(0, file_path)

    def copy_to_clipboard(self):
        text = self.output_text.get(1.0, tk.END)
        if text.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.status_var.set("Copied to clipboard")
        else:
            self.status_var.set("Nothing to copy")

    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
        self.status_var.set("Output cleared")

    def run_script(self):
        startpath = self.dir_entry.get()
        max_levels_str = self.max_level_var.get()
        gitignore = self.gitignore_var.get()
        output_file = self.output_file_entry.get() or None

        if not startpath:
            messagebox.showerror("Error", "Please select a directory.")
            return

        try:
            self.status_var.set("Processing directory structure...")
            self.root.update_idletasks()  # Update the UI to show the status change

            # Process max_levels
            max_levels = None
            if max_levels_str.strip():
                try:
                    max_levels = int(max_levels_str)
                except ValueError:
                    self.status_var.set(
                        "Invalid depth value - using unlimited depth")

            # Call the list_files function with appropriate parameters
            result = list_files(
                startpath,
                remove_objects=["venv", ".git", "__pycache__", "node_modules"],
                max_levels=max_levels,
                gitignore=gitignore,
                output_file=output_file
            )

            # Update the text area with the result
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, result)

            # Apply some basic syntax highlighting
            self.highlight_text()

            # Update status
            file_count = result.count('\n') - 1  # Rough estimate
            if output_file:
                self.status_var.set(
                    f"Generated tree with approximately {file_count} entries. Saved to file.")
            else:
                self.status_var.set(
                    f"Generated tree with approximately {file_count} entries.")

        except Exception as e:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Error: {str(e)}")
            self.status_var.set("An error occurred")

    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Directory...",
                              command=self.browse_directory)
        file_menu.add_command(label="Save Output As...",
                              command=self.browse_output_file)
        file_menu.add_separator()
        file_menu.add_command(label="Generate Tree", command=self.run_script)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Copy to Clipboard",
                              command=self.copy_to_clipboard)
        edit_menu.add_command(label="Clear Output", command=self.clear_output)

        # # View menu
        # view_menu = tk.Menu(menubar, tearoff=0)
        # menubar.add_cascade(label="View", menu=view_menu)

        # # Font size submenu
        # font_size_menu = tk.Menu(view_menu, tearoff=0)
        # view_menu.add_cascade(label="Font Size", menu=font_size_menu)

        # self.font_size_var = tk.IntVar(value=10)
        # for size in [8, 9, 10, 11, 12, 14]:
        #     font_size_menu.add_radiobutton(
        #         label=f"{size} pt",
        #         value=size,
        #         variable=self.font_size_var,
        #         command=self.change_font_size
        #     )

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    # def change_font_size(self):
    #     """Change the font size of the output text."""
    #     size = self.font_size_var.get()
    #     self.mono_font.configure(size=size)
    #     # Reapply highlighting to update the font
    #     self.highlight_text()

    def show_about(self):
        """Display the About dialog."""
        about_window = tk.Toplevel(self.root)
        about_window.title("About File Lister Pro")
        about_window.geometry("400x300")
        about_window.resizable(False, False)
        about_window.transient(self.root)  # Set as transient to main window
        about_window.grab_set()  # Make modal

        # Try to use same icon as main window
        try:
            icon_path = os.path.join(os.path.dirname(
                os.path.abspath(__file__)), "fox.ico")
            if os.path.exists(icon_path):
                about_window.iconbitmap(icon_path)
        except Exception:
            pass

        # Content frame
        frame = ttk.Frame(about_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # App title
        ttk.Label(
            frame,
            text="File Lister Pro",
            font=Font(family="Segoe UI", size=16, weight="bold")
        ).pack(pady=(0, 10))

        # Version info
        ttk.Label(
            frame,
            text="Version 1.0.0",
            font=Font(family="Segoe UI", size=10)
        ).pack()

        # Description
        description = "A professional utility for visualizing directory structures with support for .gitignore files and custom depth settings."
        ttk.Label(
            frame,
            text=description,
            font=Font(family="Segoe UI", size=10),
            wraplength=350,
            justify=tk.CENTER
        ).pack(pady=(15, 10))

        # License information
        license_frame = ttk.Frame(frame)
        license_frame.pack(fill=tk.X)

        license_text = "Released under MIT License: you can do whatever you want with this software;\nthe author is not responsible for any use or consequences."
        ttk.Label(
            license_frame,
            text=license_text,
            font=Font(family="Segoe UI", size=8),
            justify=tk.CENTER,
            foreground="#777777"
        ).pack(pady=(0, 10))

        # License button that shows the full MIT license text
        license_button = ttk.Button(
            license_frame,
            text="View Full License",
            style="Secondary.TButton",
            command=self.show_license,
            width=15
        )
        license_button.pack()

        # Copyright
        ttk.Label(
            frame,
            text="© 2025 Alexey Matveev",
            font=Font(family="Segoe UI", size=9)
        ).pack()

        # Website link
        website_frame = ttk.Frame(frame)
        website_frame.pack(pady=(15, 0))

        ttk.Label(
            website_frame,
            text="If you are Oracle Fusion implementer:",
            font=Font(family="Segoe UI", size=9)
        ).pack(side=tk.LEFT)

        website_link = ttk.Label(
            website_frame,
            text="www.sqlharmony.com",
            font=Font(family="Segoe UI", size=9, underline=True),
            foreground=self.accent_color,
            cursor="hand2"
        )
        website_link.pack(side=tk.LEFT, padx=(5, 0))
        website_link.bind("<Button-1>", lambda e: self.open_website())

        # Close button
        ttk.Button(
            frame,
            text="OK",
            command=about_window.destroy,
            style="TButton",
            width=10
        ).pack(pady=(20, 0))

        # Center the window
        about_window.update_idletasks()
        width = about_window.winfo_width()
        height = about_window.winfo_height()
        x = (about_window.winfo_screenwidth() // 2) - (width // 2)
        y = (about_window.winfo_screenheight() // 2) - (height // 2)
        about_window.geometry(f'{width}x{height}+{x}+{y}')

    def open_website(self):
        """Open the website in default browser."""
        import webbrowser
        webbrowser.open("http://www.filelister.example.com")

    def show_license(self):
        """Display the full MIT License."""
        license_window = tk.Toplevel(self.root)
        license_window.title("MIT License")
        license_window.geometry("600x500")
        license_window.transient(self.root)  # Set as transient to main window
        license_window.grab_set()  # Make modal

        # Try to use same icon as main window
        try:
            icon_path = os.path.join(os.path.dirname(
                os.path.abspath(__file__)), "fox.ico")
            if os.path.exists(icon_path):
                license_window.iconbitmap(icon_path)
        except Exception:
            pass

        # Content frame
        frame = ttk.Frame(license_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # License title
        ttk.Label(
            frame,
            text="MIT License",
            font=Font(family="Segoe UI", size=14, weight="bold")
        ).pack(pady=(0, 15))

        # License text
        license_text = """Copyright (c) 2025 File Lister Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

        # Scrolled text for license
        license_scroll = scrolledtext.ScrolledText(
            frame,
            wrap=tk.WORD,
            width=60,
            height=15,
            font=Font(family="Consolas", size=9),
            background="#f9f9f9",
            padx=10,
            pady=10
        )
        license_scroll.pack(fill=tk.BOTH, expand=True)
        license_scroll.insert(tk.END, license_text)
        license_scroll.config(state=tk.DISABLED)  # Make read-only

        # Close button
        ttk.Button(
            frame,
            text="Close",
            command=license_window.destroy,
            style="TButton",
            width=10
        ).pack(pady=(15, 0))

        # Center the window
        license_window.update_idletasks()
        width = license_window.winfo_width()
        height = license_window.winfo_height()
        x = (license_window.winfo_screenwidth() // 2) - (width // 2)
        y = (license_window.winfo_screenheight() // 2) - (height // 2)
        license_window.geometry(f'{width}x{height}+{x}+{y}')

    def highlight_text(self):
        """Apply simple syntax highlighting to the tree output."""
        # Get all text
        text = self.output_text.get("1.0", tk.END)
        lines = text.split('\n')

        # Clear existing tags
        for tag in self.output_text.tag_names():
            self.output_text.tag_delete(tag)

        # Create tags for different elements
        self.output_text.tag_configure("directory", foreground="#0066cc", font=Font(
            family="Consolas", size=10, weight="bold"))
        self.output_text.tag_configure("file", foreground="#333333")
        self.output_text.tag_configure("empty", foreground="#999999", font=Font(
            family="Consolas", size=10, slant="italic"))
        self.output_text.tag_configure("structure", foreground="#777777")

        # Apply highlighting line by line
        for i, line in enumerate(lines):
            line_start = f"{i+1}.0"
            line_end = f"{i+1}.end"

            # Find the parts to highlight
            if '/' in line:  # Directory
                # Highlight the directory name
                slash_pos = line.rfind('/')
                if slash_pos > 0:
                    dir_start_pos = line.rfind('─', 0, slash_pos) + 1
                    if dir_start_pos > 0:
                        self.output_text.tag_add(
                            "structure", f"{i+1}.0", f"{i+1}.{dir_start_pos}")
                        self.output_text.tag_add(
                            "directory", f"{i+1}.{dir_start_pos}", line_end)
            elif '(empty)' in line:  # Empty directory
                self.output_text.tag_add("structure", f"{i+1}.0", line_end)
                self.output_text.tag_add("empty", f"{i+1}.0", line_end)
            elif '─' in line:  # Files
                # Highlight the file name
                dash_pos = line.rfind('─')
                if dash_pos > 0:
                    self.output_text.tag_add(
                        "structure", f"{i+1}.0", f"{i+1}.{dash_pos + 1}")
                    self.output_text.tag_add(
                        "file", f"{i+1}.{dash_pos + 1}", line_end)
            else:  # Root directory or other
                self.output_text.tag_add("directory", line_start, line_end)


if __name__ == "__main__":
    root = tk.Tk()

    # Set application icon - using fox.ico from root folder
    try:
        icon_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "fox.ico")
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
        else:
            print(f"Icon file not found at: {icon_path}")
    except Exception as e:
        print(f"Error setting icon: {e}")

    app = FileListerApp(root)
    root.mainloop()
