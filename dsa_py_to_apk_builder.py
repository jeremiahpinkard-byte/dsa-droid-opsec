import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class PyToApkBuilderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tidewater DSA Python-to-APK Packager")
        self.root.geometry("520x540")
        self.root.configure(bg="#1A1A1A")
        self.root.resizable(False, False)

        self.dsa_red = "#ED1C24"
        self.dsa_gold = "#FFC72C"
        self.dark_bg = "#1A1A1A"
        self.text_color = "#FFFFFF"

        self.selected_file_path = ""

        # Title Header
        self.title_label = tk.Label(
            root, 
            text="DSA PYTHON TO APK PROJECT PACKAGER", 
            bg=self.dark_bg, 
            fg=self.dsa_gold, 
            font=("Arial", 13, "bold")
        )
        self.title_label.pack(pady=10)

        self.instruction_label = tk.Label(
            root, 
            text="Select your Python script, configure the package settings,\nand generate a cloud-ready build bundle.", 
            bg=self.dark_bg, 
            fg=self.text_color, 
            font=("Arial", 9),
            justify="center"
        )
        self.instruction_label.pack(pady=5)

        # File Selection Frame
        self.file_frame = tk.Frame(root, bg=self.dark_bg)
        self.file_frame.pack(pady=10)

        self.select_btn = tk.Button(
            self.file_frame, text="Select Python Script (.py)", command=self.select_python_file,
            bg=self.dsa_gold, fg="#1A1A1A", font=("Arial", 9, "bold"), relief="flat", width=25, height=2
        )
        self.select_btn.pack(side=tk.LEFT, padx=5)

        self.file_status_label = tk.Label(
            self.file_frame, text="No file selected", bg=self.dark_bg, fg="#AAAAAA", font=("Arial", 8), width=30, anchor="w"
        )
        self.file_status_label.pack(side=tk.LEFT, padx=5)

        # App Details Inputs
        self.config_frame = tk.Frame(root, bg=self.dark_bg)
        self.config_frame.pack(pady=10)

        tk.Label(self.config_frame, text="App Title:", bg=self.dark_bg, fg=self.text_color, font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.app_title_entry = tk.Entry(self.config_frame, width=30, font=("Arial", 10))
        self.app_title_entry.insert(0, "Tidewater OpSec App")
        self.app_title_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.config_frame, text="Package Name:", bg=self.dark_bg, fg=self.text_color, font=("Arial", 9, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        self.package_name_entry = tk.Entry(self.config_frame, width=30, font=("Arial", 10))
        self.package_name_entry.insert(0, "dsaopsec")
        self.package_name_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self.config_frame, text="Package Domain:", bg=self.dark_bg, fg=self.text_color, font=("Arial", 9, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        self.domain_entry = tk.Entry(self.config_frame, width=30, font=("Arial", 10))
        self.domain_entry.insert(0, "org.tidewater")
        self.domain_entry.grid(row=2, column=1, padx=10, pady=5)

        # Generate Action Button
        self.build_bundle_btn = tk.Button(
            root, text="Generate Cloud Build Bundle", command=self.generate_bundle,
            bg=self.dsa_red, fg=self.text_color, font=("Arial", 10, "bold"), relief="flat", width=38, height=2
        )
        self.build_bundle_btn.pack(pady=15)

        # Output Log Box
        self.log_area = scrolledtext.ScrolledText(root, width=58, height=10, bg="#222222", fg=self.text_color, font=("Consolas", 8))
        self.log_area.pack(padx=10, pady=5)
        self.log_area.insert(tk.END, "Packager initialized. Select a script to begin.\n")

    def log(self, message):
        self.log_area.insert(tk.END, f"{message}\n")
        self.log_area.see(tk.END)

    def select_python_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Python Source Script",
            filetypes=[("Python Files", "*.py")]
        )
        if file_path:
            self.selected_file_path = file_path
            filename = os.path.basename(file_path)
            self.file_status_label.config(text=filename, fg="#00FF00")
            self.log(f"Loaded script: {filename}")

    def generate_bundle(self):
        if not self.selected_file_path:
            messagebox.showerror("Error", "Please select a Python script first.")
            return

        app_title = self.app_title_entry.get().strip()
        package_name = self.package_name_entry.get().strip()
        domain = self.domain_entry.get().strip()

        if not app_title or not package_name or not domain:
            messagebox.showerror("Error", "All configuration fields must be filled.")
            return

        output_dir = filedialog.askdirectory(title="Select Destination Folder for Build Bundle")
        if not output_dir:
            return

        try:
            project_folder = os.path.join(output_dir, f"{package_name}_android_build")
            os.makedirs(project_folder, exist_ok=True)

            # 1. Copy user python script as main.py
            dest_main = os.path.join(project_folder, "main.py")
            shutil.copy(self.selected_file_path, dest_main)
            self.log(f"Copied source script to main.py")

            # 2. Generate buildozer.spec
            spec_path = os.path.join(project_folder, "buildozer.spec")
            spec_content = f"""[app]
title = {app_title}
package.name = {package_name}
package.domain = {domain}
source.include_exts = py,png,jpg,kv,atlas
requirements = python3,kivy,pillow,certifi,urllib3
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
"""
            with open(spec_path, "w", encoding="utf-8") as f:
                f.write(spec_content)
            self.log(f"Generated buildozer.spec configuration")

            # 3. Generate GitHub Actions workflow folder and file
            workflow_dir = os.path.join(project_folder, ".github", "workflows")
            os.makedirs(workflow_dir, exist_ok=True)
            workflow_path = os.path.join(workflow_dir, "build.yml")

            workflow_content = """name: Build Android APK

on:
  push:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-20.04
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Build with Buildozer
        uses: ArtemSBulgakov/buildozer-action@v1
        id: buildozer
        with:
          command: buildozer android debug

      - name: Upload APK Artifact
        uses: actions/upload-artifact@v4
        with:
          name: android-apk
          path: ${{ steps.buildozer.outputs.filename }}
"""
            with open(workflow_path, "w", encoding="utf-8") as f:
                f.write(workflow_content)
            self.log(f"Generated GitHub Actions workflow file")

            self.log(f"\n[SUCCESS] Build bundle successfully created at:\n{project_folder}")
            messagebox.showinfo("Success", f"Build bundle generated successfully!\n\nLocation:\n{project_folder}")

        except Exception as e:
            self.log(f"[ERROR] Failed to generate bundle: {e}")
            messagebox.showerror("Error", f"Failed to generate bundle: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PyToApkBuilderApp(root)
    root.mainloop()