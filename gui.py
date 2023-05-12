import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from pydub import AudioSegment, silence
import zipfile
import os
import multiprocessing as mp
import tempfile

def browse_audio_files():
    file_paths = filedialog.askopenfilenames(title="Select Audio Files", filetypes=[("Audio Files", "*.wav;*.mp3")])
    audio_files_list.delete(0, tk.END)
    for file_path in file_paths:
        audio_files_list.insert(tk.END, file_path)


def remove_silence(audio):
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
        joined_segments.append(current_segment)

    return joined_segments


def process_audio_file(audio_file_path, i, segment_duration):
    audio = AudioSegment.from_file(audio_file_path)

    is_mp3 = audio_file_path.lower().endswith('.mp3')

    non_silent_audio = remove_silence(audio)

    segments = []
    for j, segment in enumerate(non_silent_audio):
        if segment.duration_seconds >= segment_duration:
            segments.extend(segment[0:segment_duration * 1000] for segment in segment[::segment_duration * 1000])
        else:
            segments.append(segment)

    joined_segments = join_audio_segments(segments, segment_duration)

    temp_files = []
    for k, segment in enumerate(joined_segments):
        segment_file_name = f"segment_{i + 1}_{k + 1}.wav" if not is_mp3 else f"segment_{i + 1}_{k + 1}.mp3"
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        segment.export(temp_file.name, format="wav" if not is_mp3 else "mp3")
        temp_files.append((segment_file_name, temp_file.name))

    return temp_files


def process_audio_files(audio_files, segment_duration, progress_queue):
    for i, audio_file_path in enumerate(audio_files):
        temp_files = process_audio_file(audio_file_path, i, segment_duration)  # Corrected here

        # when finished processing, put something in the queue
        progress_queue.put((i, temp_files))


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

    progress_queue = mp.Queue()

    zip_file_name = "audio_segments.zip"
    with zipfile.ZipFile(zip_file_name, 'w') as zip_file:
        # start worker process
        p = mp.Process(target=process_audio_files, args=(audio_files, segment_duration, progress_queue))
        p.start()

        completed = 0
        while completed < len(audio_files):
            # update progress bar whenever a process finishes
            i,temp_files = progress_queue.get()
            completed += 1
            progress = (completed / len(audio_files)) * 100
            progress_var.set(progress)
            progress_label.config(text=f"{int(progress)}%")
            root.update()

            # save the results
            for segment_file_name, temp_file_name in temp_files:
                with open(temp_file_name, 'rb') as f:
                    zip_file.writestr(segment_file_name, f.read())
                os.remove(temp_file_name)

        p.join()

    messagebox.showinfo("Info", f"Audio segments have been saved to {zip_file_name}.")
    progress_var.set(0)  # reset progress bar
    progress_label.config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Audio Splitter")
    root.geometry('500x300')  # set window size
    root.configure(bg='white')  # set background color

    # Create a frame for file selection
    frame1 = tk.Frame(root, bg='white')
    frame1.pack(fill=tk.X, padx=20, pady=10)

    audio_files_label = tk.Label(frame1, text="Audio Files:", bg='white', font=('Arial', 14))
    audio_files_label.pack(side=tk.LEFT)

    audio_files_list = tk.Listbox(frame1, selectmode=tk.MULTIPLE, height=5)
    audio_files_list.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=10)

    browse_button = tk.Button(frame1, text="Browse", command=browse_audio_files, font=('Arial', 12), fg='white', bg='blue')
    browse_button.pack(side=tk.RIGHT)

    # Create a frame for segment duration
    frame2 = tk.Frame(root, bg='white')
    frame2.pack(fill=tk.X, padx=20, pady=10)

    segment_duration_label = tk.Label(frame2, text="Segment Duration (seconds):", bg='white', font=('Arial', 14))
    segment_duration_label.pack(side=tk.LEFT)

    segment_duration_entry = tk.Entry(frame2, font=('Arial', 12))
    segment_duration_entry.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=10)

    # Create a frame for the split button
    frame3 = tk.Frame(root, bg='white')
    frame3.pack(fill=tk.X, padx=20, pady=10)

    split_button = tk.Button(frame3, text="Split Audio Files", command=split_audio_files, font=('Arial', 12), fg='white', bg='green')
    split_button.pack(fill=tk.X)

    # Create a frame for the progress bar
    frame4 = tk.Frame(root, bg='white')
    frame4.pack(fill=tk.X, padx=20, pady=10)

    progress_label = tk.Label(frame4, text="", bg='white', font=('Arial', 14))
    progress_label.pack(side=tk.LEFT)

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(frame4, length=300, variable=progress_var, maximum=100)
    progress_bar.pack(fill=tk.X, expand=True, side=tk.LEFT)

    root.mainloop()