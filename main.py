from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
import os
import urllib.request
import json
import datetime
import subprocess

try:
    from PIL import Image
    PIL_SUPPORT = True
except ImportError:
    PIL_SUPPORT = False

class DSAAndroidOpSecApp(App):
    def build(self):
        self.title = "Tidewater DSA Android OpSec Suite"
        self.telemetry_log_path = "dsa_android_opsec.log"

        root_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        # Header Title
        header = Label(
            text="TIDEWATER DSA ANDROID OPSEC",
            color=(1, 0.78, 0.17, 1), # Gold
            font_size='16sp',
            size_hint=(1, 0.08)
        )
        root_layout.add_widget(header)

        # Scrollable Button Area
        scroll = ScrollView(size_hint=(1, 0.92))
        btn_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        btn_layout.bind(minimum_height=btn_layout.setter('height'))

        # Buttons
        btn_net = Button(text="Run Network Leak Audit", background_color=(0.93, 0.11, 0.14, 1), size_hint_y=None, height=55)
        btn_net.bind(on_press=self.run_network_audit)
        btn_layout.add_widget(btn_net)

        btn_clip = Button(text="Wipe Clipboard Buffers", background_color=(0.93, 0.11, 0.14, 1), size_hint_y=None, height=55)
        btn_clip.bind(on_press=self.run_wipe_clipboard)
        btn_layout.add_widget(btn_clip)

        btn_img = Button(text="Sanitize Image Metadata", background_color=(0.93, 0.11, 0.14, 1), size_hint_y=None, height=55)
        btn_img.bind(on_press=self.prompt_sanitize_image)
        btn_layout.add_widget(btn_img)

        btn_shred = Button(text="Securely Shred File", background_color=(0.93, 0.11, 0.14, 1), size_hint_y=None, height=55)
        btn_shred.bind(on_press=self.prompt_shred_file)
        btn_layout.add_widget(btn_shred)

        btn_hist = Button(text="Clear Termux Shell History", background_color=(0.93, 0.11, 0.14, 1), size_hint_y=None, height=55)
        btn_hist.bind(on_press=self.run_clear_history)
        btn_layout.add_widget(btn_hist)

        btn_log = Button(text="View Telemetry Log", background_color=(1, 0.78, 0.17, 1), color=(0.1, 0.1, 0.1, 1), size_hint_y=None, height=55)
        btn_log.bind(on_press=self.view_telemetry)
        btn_layout.add_widget(btn_log)

        scroll.add_widget(btn_layout)
        root_layout.add_widget(scroll)

        return root_layout

    def log_action(self, action, status):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] ACTION: {action} | STATUS: {status}\n"
        try:
            with open(self.telemetry_log_path, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception:
            pass

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        lbl = Label(text=message, halign='center', valign='middle')
        lbl.bind(size=lbl.setter('text_size'))
        content.add_widget(lbl)
        
        close_btn = Button(text="Close", size_hint=(1, 0.3), background_color=(0.93, 0.11, 0.14, 1))
        popup = Popup(title=title, content=content, size_hint=(0.85, 0.4))
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()

    def run_network_audit(self, instance):
        try:
            req = urllib.request.Request("https://ipinfo.io/json", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                ip = data.get('ip', 'Unknown')
                org = data.get('org', 'Unknown')
                city = data.get('city', '')
                country = data.get('country', '')
                msg = f"Public IP: {ip}\nISP/Org: {org}\nLocation: {city}, {country}"
                self.log_action("Network Audit", f"SUCCESS - IP: {ip}")
                self.show_popup("Network Audit Success", msg)
        except Exception as e:
            self.log_action("Network Audit", f"ERROR - {e}")
            self.show_popup("Audit Error", str(e))

    def run_wipe_clipboard(self, instance):
        try:
            subprocess.run(["termux-clipboard-set", ""])
            self.log_action("Clipboard Wipe", "SUCCESS")
            self.show_popup("Success", "Android clipboard buffers cleared successfully.")
        except Exception as e:
            self.log_action("Clipboard Wipe", f"ERROR - {e}")
            self.show_popup("Error", f"Failed to wipe clipboard:\n{e}")

    def prompt_sanitize_image(self, instance):
        self.show_input_popup("Sanitize Image", "Enter full path to image file:", self.execute_sanitize_image)

    def execute_sanitize_image(self, file_path):
        if not PIL_SUPPORT:
            self.show_popup("Error", "Pillow library is not available.")
            return
        if not file_path or not os.path.exists(file_path):
            self.show_popup("Error", "File path not found.")
            return

        try:
            directory, filename = os.path.split(file_path)
            name, ext = os.path.splitext(filename)
            output_path = os.path.join(directory, f"{name}_sanitized{ext}")

            with Image.open(file_path) as img:
                data = list(img.getdata())
                clean_img = Image.new(img.mode, img.size)
                clean_img.putdata(data)
                clean_img.save(output_path, exif=b"", icc_profile=None)

            self.log_action("Image Sanitize", f"SUCCESS - {filename}")
            self.show_popup("Success", f"Metadata stripped.\nSaved to:\n{output_path}")
        except Exception as e:
            self.log_action("Image Sanitize", f"ERROR - {e}")
            self.show_popup("Error", f"Sanitization failed:\n{e}")

    def prompt_shred_file(self, instance):
        self.show_input_popup("Secure Shred", "Enter full path to file to shred:", self.execute_shred_file)

    def execute_shred_file(self, file_path):
        if not file_path or not os.path.exists(file_path):
            self.show_popup("Error", "File path not found.")
            return

        try:
            file_size = os.path.getsize(file_path)
            with open(file_path, "wb") as f:
                f.write(os.urandom(file_size))
            os.remove(file_path)
            self.log_action("Secure File Shred", f"SUCCESS - {os.path.basename(file_path)}")
            self.show_popup("Success", "File securely shredded and removed from disk.")
        except Exception as e:
            self.log_action("Secure File Shred", f"ERROR - {e}")
            self.show_popup("Error", f"Failed to shred file:\n{e}")

    def run_clear_history(self, instance):
        history_files = [
            os.path.expanduser("~/.bash_history"),
            os.path.expanduser("~/.zsh_history")
        ]
        cleared_count = 0
        for hf in history_files:
            if os.path.exists(hf):
                try:
                    open(hf, "w").close()
                    cleared_count += 1
                except Exception:
                    pass
        self.log_action("Termux History Purge", f"SUCCESS - Cleared {cleared_count} files")
        self.show_popup("History Purge", f"Successfully cleared {cleared_count} shell history files.")

    def view_telemetry(self, instance):
        if not os.path.exists(self.telemetry_log_path):
            self.show_popup("Telemetry Log", "No local telemetry log found yet.")
            return
        try:
            with open(self.telemetry_log_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.show_popup("OpSec Telemetry Log", content[-1500:]) # Show recent logs
        except Exception as e:
            self.show_popup("Error", f"Failed to read log: {e}")

    def show_input_popup(self, title, prompt_text, callback):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=prompt_text, size_hint=(1, 0.3)))
        
        text_input = TextInput(text="", multiline=False, size_hint=(1, 0.3))
        content.add_widget(text_input)

        btn_layout = BoxLayout(size_hint=(1, 0.4), spacing=10)
        submit_btn = Button(text="Confirm", background_color=(0.93, 0.11, 0.14, 1))
        cancel_btn = Button(text="Cancel", background_color=(0.3, 0.3, 0.3, 1))
        
        popup = Popup(title=title, content=content, size_hint=(0.85, 0.45))
        
        def on_submit(instance):
            val = text_input.text.strip()
            popup.dismiss()
            callback(val)

        submit_btn.bind(on_press=on_submit)
        cancel_btn.bind(on_press=popup.dismiss)
        
        btn_layout.add_widget(submit_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        popup.open()

if __name__ == "__main__":
    DSAAndroidOpSecApp().run()