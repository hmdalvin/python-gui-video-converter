import tkinter as tk
from tkinter import filedialog, messagebox
from ttkbootstrap.widgets import Meter
from moviepy import VideoFileClip
import os
import threading
import queue

class BatchVideoConverter:
    def __init__(self, root, queue):
        self.root = root
        self.queue = queue
        self.folder_path = None
        self.audio_format = None
        self.label_text = tk.StringVar()
        self.label_text.set("Please select a folder for batch conversion.")

        self.label = tk.Label(root, textvariable=self.label_text, font=("Arial", 12), wraplength=400)
        self.label.pack(pady=10)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        self.btn_select = tk.Button(button_frame, text="Select Folder", command=self.select_folder, bg="#1E88E5", fg="white", font=("Arial", 10, "bold"))
        self.btn_select.pack(side=tk.LEFT, padx=5)

        self.label_format = tk.Label(root, text="Select Output Format:", font=("Arial", 10), anchor="w")
        self.label_format.pack(pady=5)

        self.audio_format_var = tk.StringVar()
        self.audio_format_var.set("MP3 Audio")  # Default format

        self.format_options = ["MP3 Audio", "WAV Audio", "OGG Audio", "FLAC Audio"]
        self.option_menu = tk.OptionMenu(root, self.audio_format_var, *self.format_options)
        self.option_menu.config(width=20, font=("Arial", 10))
        self.option_menu.pack(pady=5)

        self.btn_convert = tk.Button(root, text="Batch Convert", command=self.batch_convert, state=tk.DISABLED, bg="#FFB300", fg="white", font=("Arial", 10, "bold"))
        self.btn_convert.pack(pady=5)

        self.meter = Meter(root, bootstyle="info", subtext="Progress", interactive=False, amounttotal=100)
        self.meter.pack(pady=10)

        # Label to show the conversion status
        self.status_label = tk.Label(root, text="Please select a folder for batch conversion.", font=("Arial", 12))
        self.status_label.pack(pady=5)

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Select Folder Containing Videos")
        if folder_path:
            self.folder_path = folder_path
            self.label_text.set(f"Folder selected: {os.path.basename(folder_path)}")
            self.btn_convert.config(state=tk.NORMAL)

    def batch_convert(self):
        if self.folder_path:
            self.audio_format = self.audio_format_var.get()
            self.status_label.config(text="Conversion in progress...")  # Update status
            # Start the conversion in a separate thread
            threading.Thread(target=self.process_batch_conversion, daemon=True).start()

    def process_batch_conversion(self):
        try:
            files = [f for f in os.listdir(self.folder_path) if f.endswith(('.mp4', '.avi', '.mkv', '.mov'))]
            if not files:
                messagebox.showwarning("Warning", "No video files found in the selected folder.")
                return

            total_files = len(files)

            # Show the progress bar after the first file starts processing
            self.root.after(100, self.update_progress)  # Delay progress bar appearance

            for index, video_file in enumerate(files):
                video_path = os.path.join(self.folder_path, video_file)
                video_name = os.path.splitext(video_file)[0]
                save_path = os.path.join(self.folder_path, f"{video_name}.{self.audio_format.split()[0].lower()}")

                # Convert video to audio
                self.convert_single_video(video_path, save_path)

                # Update progress bar after processing each file
                progress_value = int((index + 1) * 100 / total_files)  # Convert to integer
                self.queue.put(progress_value)
                self.root.after(10, self.check_queue)

            # Change progress bar color to green once all files are processed
            self.meter.configure(bootstyle="success", amountused=100)
            self.status_label.config(text="Conversion complete.")  # Update status to complete
            messagebox.showinfo("Success", f"Batch conversion completed for {total_files} files.")

        except Exception as e:
            self.status_label.config(text="An error occurred.")  # Update status on error
            messagebox.showerror("Error", f"Batch conversion failed: {e}")

    def convert_single_video(self, video_path, save_path):
        try:
            # Start the video conversion with moviepy
            video = VideoFileClip(video_path)
            audio = video.audio
            audio.write_audiofile(save_path)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert {os.path.basename(video_path)}: {e}")

    def check_queue(self):
        try:
            # Get the current progress value (ensure it's an integer)
            progress_value = self.queue.get_nowait()

            # Update the progress bar with integer value
            if 0 <= progress_value <= 100:
                self.meter.configure(amountused=progress_value)

            self.root.update_idletasks()
        except queue.Empty:
            pass

    def update_progress(self):
        # Initially show the progress bar
        self.meter.configure(amountused=0)
