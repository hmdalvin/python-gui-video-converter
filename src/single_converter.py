import tkinter as tk
from tkinter import filedialog, messagebox
from ttkbootstrap.widgets import Meter
import os
import threading
import queue
import subprocess
import time  # Import time module for sleep function

class SingleVideoConverter:
    def __init__(self, root, queue):
        self.root = root
        self.queue = queue
        self.video_path = None
        self.save_path = None
        self.label_text = tk.StringVar()
        self.label_text.set("Select a video to convert:")

        self.label = tk.Label(root, textvariable=self.label_text, font=("Arial", 12), wraplength=400)
        self.label.pack(pady=10)

        # Frame untuk tombol "Select Video" dan "Convert"
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        self.btn_select = tk.Button(button_frame, text="Select Video", command=self.select_video, bg="#1E88E5", fg="white", font=("Arial", 10, "bold"))
        self.btn_select.pack(side=tk.LEFT, padx=5)

        self.btn_convert = tk.Button(root, text="Convert", command=self.convert_to_audio, state=tk.DISABLED, bg="#43A047", fg="white", font=("Arial", 10, "bold"))
        self.btn_convert.pack(pady=5)

        self.meter = Meter(root, bootstyle="success", subtext="%", interactive=False, amounttotal=100)
        self.meter.pack(pady=10)

    def select_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", ".mp4;.avi;.mkv;.mov")])
        if file_path:
            self.video_path = file_path
            self.label_text.set(self.shorten_text(f"Video selected: {os.path.basename(file_path)}"))
            self.select_audio_format()

    def select_audio_format(self):
        format_choice = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            initialfile=os.path.splitext(os.path.basename(self.video_path))[0] + ".mp3",
            filetypes=[("MP3 Audio", "*.mp3"), ("WAV Audio", "*.wav"), ("OGG Audio", "*.ogg"), ("FLAC Audio", "*.flac"), ("AAC Audio", "*.aac")],
            title="Select Audio Format"
        )
        if format_choice:
            self.save_path = format_choice
            self.btn_convert.config(state=tk.NORMAL)

    def convert_to_audio(self):
        if self.video_path and self.save_path:
            # Pastikan path video dan save path tidak kosong
            if not os.path.isfile(self.video_path):
                messagebox.showerror("Error", "The selected video file is invalid.")
                return
            if not self.save_path:
                messagebox.showerror("Error", "No save path selected.")
                return

            threading.Thread(target=self.process_conversion, daemon=True).start()
        else:
            messagebox.showerror("Error", "Please select a valid video file and output path.")
        
    def process_conversion(self):
        try:
            self.label_text.set(f"Starting conversion...")
            self.meter.configure(amountused=0)

            self.convert_single_video()

            self.root.after(10, self.show_progress_animation)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert video: {e}")
        finally:
            self.meter.configure(amountused=100)

    def convert_single_video(self):
        try:
            self.label_text.set(f"Converting: {self.shorten_text(os.path.basename(self.video_path))}")

            # Simulasi progres sebelum konversi dimulai
            for i in range(1, 51):
                self.queue.put(i)
                self.root.after(10, self.check_queue)
                time.sleep(0.05)

            # Tentukan format berdasarkan ekstensi file output
            if self.save_path.endswith(".aac"):
                command = f'ffmpeg -y -i "{self.video_path}" -c:a aac -b:a 192k "{self.save_path}"'
            else:
                command = f'ffmpeg -y -i "{self.video_path}" "{self.save_path}"'

            # Jalankan perintah ffmpeg tanpa membuka CMD dan tanpa konfirmasi overwrite
            subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Simulasi progres setelah konversi
            for i in range(51, 101):
                self.queue.put(i)
                self.root.after(10, self.check_queue)
                time.sleep(0.05)

            # Notifikasi setelah selesai
            self.root.after(10, self.show_conversion_complete_notification)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert {os.path.basename(self.video_path)}: {e}")

    def show_progress_animation(self):
        self.root.after(10, self.check_queue)

    def shorten_text(self, text, max_length=30):
        # Memastikan text yang dipotong tidak kosong
        if text:
            return text[:max_length] + "..." if len(text) > max_length else text
        return ""

    def check_queue(self):
        try:
            progress_value = self.queue.get_nowait()
            self.meter.configure(amountused=progress_value)
            self.root.update_idletasks()
        except queue.Empty:
            pass

    def show_conversion_complete_notification(self):
        messagebox.showinfo("Conversion Complete", f"Audio conversion for {os.path.basename(self.video_path)} has been completed successfully.")
