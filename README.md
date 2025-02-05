# Video to Audio Converter

A video-to-audio conversion application using Python and Tkinter for the user interface. This app allows users to convert video files into various audio formats like MP3, WAV, OGG, and FLAC. The conversion is done using `moviepy`, and the user interface is built with `ttkbootstrap` for a more modern design.

## Features
- **Single Video Conversion**: Select individual video files and convert them into the desired audio format (MP3, WAV, OGG, FLAC).
- **Separate Conversion Process**: Conversion is done in a separate thread to keep the UI responsive.
- **Progress Indicator**: Displays a real-time progress bar showing the conversion progress.
- **Audio Format Selection**: Supports multiple audio formats for the conversion result, such as MP3, WAV, OGG, and FLAC.

## Prerequisites
Ensure you have the following dependencies installed to run this application:
- **Python 3.6+**
- **moviepy**: For video-to-audio conversion.
- **ttkbootstrap**: For the user interface design.
- **Pillow**: For UI image support.
- **queue**: For managing thread progress.



