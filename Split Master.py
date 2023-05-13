from pydub import AudioSegment, silence
import zipfile
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

def browse_audio_files():
    file_paths = filedialog.askopenfilenames(title="Select Audio Files", filetypes=[("Audio Files", "*.wav;*.mp3")])
    audio_files_list.delete(0, tk.END)
    for file_path in file_paths:
        audio_files_list.insert(tk.END, file_path)

def remove_silence(audio):
    # Remove silence
    non_silent_audio = silence.split_on_silence(audio, min_silence_len=1000, silence_thresh=-40)
    return non_silent_audio

def join_audio_segments(segments, segment_duration):
    joined_segments = []
    current_segment = None
    for segment in segments:
        if current_segment is None:
            current_segment = segment
        elif current_segment.duration_seconds < segment_duration:
            current_segment += segment
        else:
            joined_segments.append(current_segment)
            current_segment = segment

    if current_segment is not None:
        if current_segment.duration_seconds < segment_duration:
            if joined_segments:
                joined_segments[-1] += current_segment
            else:
                joined_segments.append(current_segment)
        else:
            joined_segments.append(current_segment)

    return joined_segments


def split_audio_files():
    audio_files = audio_files_list.get(0, tk.END)
    if len(audio_files) == 0:
        messagebox.showwarning("Warning", "Please select audio file(s) to split.")
        return

    segment_duration = segment_duration_entry.get()
    try:
        segment_duration = int(segment_duration)
    except ValueError:
        messagebox.showerror("Error", "Invalid segment duration. Please enter an integer.")
        return

    zip_file_name = "audio_segments.zip"
    with zipfile.ZipFile(zip_file_name, 'w') as zip_file:
        for i, audio_file_path in enumerate(audio_files):
            audio = AudioSegment.from_file(audio_file_path)

            # Check if the file is in mp3 format
            is_mp3 = False
            if audio_file_path.lower().endswith('.mp3'):
                is_mp3 = True

            # Remove silence
            non_silent_audio = remove_silence(audio)

            segments = []
            for j, segment in enumerate(non_silent_audio):
                if segment.duration_seconds >= segment_duration:
                    segments.extend(segment[0:segment_duration * 1000] for segment in segment[::segment_duration * 1000])
                else:
                    segments.append(segment)

            # Join segments less than the specified duration with the nearest audio segment
            joined_segments = join_audio_segments(segments, segment_duration)

            for k, segment in enumerate(joined_segments):
                segment_file_name = f"segment_{i + 1}_{k + 1}.wav" if not is_mp3 else f"segment_{i + 1}_{k + 1}.mp3"
                segment.export(segment_file_name, format="wav" if not is_mp3 else "mp3")
                zip_file.write(segment_file_name)
                os.remove(segment_file_name)

    messagebox.showinfo("Info", f"Audio segments have been saved to {zip_file_name}.")

# Create main window
root = tk.Tk()
root.title("Audio Splitter")

# Add components to the main window
audio_files_label = tk.Label(root, text="Audio Files:")
audio_files_label.grid(row=0, column=0, sticky=tk.W)

audio_files_list = tk.Listbox(root, selectmode=tk.MULTIPLE, height=5)
audio_files_list.grid(row=0, column=1, columnspan=2, padx=10, pady=10)

browse_button = tk.Button(root, text="Browse", command=browse_audio_files)
browse_button.grid(row=0, column=3)

segment_duration_label = tk.Label(root, text="Segment Duration (seconds):")
segment_duration_label.grid(row=1, column=0, sticky=tk.W)

segment_duration_entry = tk.Entry(root)
segment_duration_entry.grid(row=1, column=1, columnspan=2, padx=10)

split_button = tk.Button(root, text="Split Audio Files", command=split_audio_files)
split_button.grid(row=2, column=1, pady=10)

root.mainloop()
