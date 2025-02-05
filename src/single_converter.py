import tkinter as tk
from tkinter import filedialog, messagebox
from ttkbootstrap.widgets import Meter
from moviepy import VideoFileClip
import os
import threading
import queue
import time

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

        # Frame for horizontal buttons: Select Video and Convert
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        self.btn_select = tk.Button(button_frame, text="Select Video", command=self.select_video, bg="#1E88E5", fg="white", font=("Arial", 10, "bold"))
        self.btn_select.pack(side=tk.LEFT, padx=5)

        self.btn_convert = tk.Button(root, text="Convert", command=self.convert_to_audio, state=tk.DISABLED, bg="#43A047", fg="white", font=("Arial", 10, "bold"))
        self.btn_convert.pack(pady=5)

        self.meter = Meter(root, bootstyle="success", subtext="Progress", interactive=False, amounttotal=100)
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
            filetypes=[("MP3 Audio", "*.mp3"), ("WAV Audio", "*.wav"), ("OGG Audio", "*.ogg"), ("FLAC Audio", "*.flac")],
            title="Select Audio Format"
        )
        if format_choice:
            self.save_path = format_choice
            self.btn_convert.config(state=tk.NORMAL)

    def convert_to_audio(self):
        if self.video_path and self.save_path:
            threading.Thread(target=self.process_conversion, daemon=True).start()

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
            
            video = VideoFileClip(self.video_path)
            audio = video.audio
            video_duration = video.duration

            loading_steps_fast = 25
            step_duration_fast = video_duration / (loading_steps_fast * 10)

            loading_steps_slow = 25
            step_duration_slow = video_duration / (loading_steps_slow * 30)

            for i in range(loading_steps_fast):
                progress_value = int((i + 1) * 50 / loading_steps_fast)  # Convert to integer
                self.queue.put(progress_value)
                self.root.after(10, self.check_queue)
                time.sleep(step_duration_fast)

            audio.write_audiofile(self.save_path)

            for i in range(loading_steps_slow):
                progress_value = int(50 + (i + 1) * 50 / loading_steps_slow)  # Convert to integer
                self.queue.put(progress_value)
                self.root.after(10, self.check_queue)
                time.sleep(step_duration_slow)

            # Display notification after conversion is complete
            self.root.after(10, self.show_conversion_complete_notification)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert {os.path.basename(self.video_path)}: {e}")

    def show_progress_animation(self):
        self.root.after(10, self.check_queue)

    def shorten_text(self, text, max_length=30):
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text

    def check_queue(self):
        try:
            progress_value = self.queue.get_nowait()
            self.meter.configure(amountused=progress_value)
            self.root.update_idletasks()
        except queue.Empty:
            pass

    def show_conversion_complete_notification(self):
        messagebox.showinfo("Conversion Complete", f"Audio conversion for {os.path.basename(self.video_path)} has been completed successfully.")
