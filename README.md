# Audio Splitter

Audio Splitter is a Python application that allows you to split audio files into smaller segments based on duration and remove silent parts. It provides a graphical user interface (GUI) built with PyQt5 and utilizes the PyDub library for audio processing.

## Features

- Add audio files in various formats (MP3, WAV, FLAC, OGG, M4A)
- Specify the segment duration in seconds
- Adjust the silence threshold to remove silent parts
- Choose the output format for the audio segments
- Monitor progress with a progress bar
- Export the segmented audio files as a zip archive

## Requirements

- Python 3.6 or higher
- PyQt5
- PyDub
- FFmpeg (required by PyDub for audio file processing)

## Installation

1. Clone the repository or download the source code.
2. Install the required dependencies:
   ```bash
   pip install pyqt5 pydub
   ```
3. Install FFmpeg. Refer to the FFmpeg documentation for installation instructions based on your operating system.


# Usage

To run the application, execute the following command:
```bash
python audio_splitter.py
```

The application window will open, providing the following options:

- Add Files: Click this button to select audio files to process.
- Remove Selected Files: Remove the selected audio files from the list.
- Clear All Files: Remove all audio files from the list.
- Segment Duration: Enter the desired duration in seconds for each segment.
- Silence Threshold: Adjust the silence threshold in decibels (dB) to detect and remove silent parts.
- Output Format: Select the desired output format for the segmented audio files.
- Start: Click this button to start the segmentation process.
- Progress Bar: Shows the progress of the segmentation process.
- Finished: Indicates the completion of the segmentation process and the location of the generated zip file.

Contributing
Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

License
This project is licensed under the MIT License.
