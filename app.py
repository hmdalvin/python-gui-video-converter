import tkinter as tk
from ttkbootstrap import Style
from src.single_converter import SingleVideoConverter
from src.batch_converter import BatchVideoConverter
import queue

class VideoToAudioConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video to Audio Converter")
        self.root.geometry("500x400")  # Set initial window size
        self.root.resizable(False, False)

        style = Style(theme="superhero")

        # Create queue for thread communication
        self.queue = queue.Queue()

        # Create frames to hold the converters
        self.single_frame = tk.Frame(root)
        self.single_video_converter = SingleVideoConverter(self.single_frame, self.queue)
        self.single_frame.pack(fill="both", expand=True)

        self.batch_frame = tk.Frame(root)
        self.batch_video_converter = BatchVideoConverter(self.batch_frame, self.queue)

        # Button to switch to Batch Converter
        self.btn_switch_to_batch = tk.Button(self.single_frame, text="Switch to Batch Converter", command=self.switch_to_batch)
        self.btn_switch_to_batch.pack(pady=10)

        # Button to switch back to Single Converter (to be added in Batch Converter)
        self.btn_switch_to_single = tk.Button(self.batch_frame, text="Back to Single Converter", command=self.switch_to_single)
        self.btn_switch_to_single.pack(pady=10)

    def switch_to_batch(self):
        # Hide single converter frame
        self.single_frame.pack_forget()

        # Show batch converter frame
        self.batch_frame.pack(fill="both", expand=True)

        # Set the window size when switching to batch converter
        self.root.geometry("500x500")  # Adjust this size as needed

    def switch_to_single(self):
        # Hide batch converter frame
        self.batch_frame.pack_forget()

        # Show single converter frame
        self.single_frame.pack(fill="both", expand=True)

        # Reset the window size when switching to single converter
        self.root.geometry("500x400")  # Return to the original size

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()  # Tambahkan ini
    root = tk.Tk()
    app = VideoToAudioConverterApp(root)
    root.mainloop()
