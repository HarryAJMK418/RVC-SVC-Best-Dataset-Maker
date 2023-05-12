# RVC-SVC-Best-Dataset-Maker
RVC/SVC Best Dataset Maker Allows You To Make The Best Datasets FOR RVC/SVC Voice Models

Features: It Removes Silenced Parts From Audio And Then Split The Audio In As many numbers Of Second U Want And Add It In A Zip Automatically, Enjoy!

# Prerequisites

Before running the application, you need to have Python installed on your system. You can download Python from [here](https://www.python.org/downloads/). This application was developed with Python 3.8, but it should work with other versions as well.

To install these dependencies, run the following command:

```shell
pip install pydub tkinter
```


How To Make THE BEST DATASET -
1) Download All Songs From Either https://spotifydown.com/ Or https://yt2mp3.info/?l=en (Make Sure ALL AUDIOS ARE OF WAV FORMAT BEFORE RUNNING THE SCRIPT)
2) Remove Instrumentals Of ALL SONGS Using Either https://studio.gaudiolab.io/gsep Or Ultimate Vocal Remover
3) Download The Python Script Uploaded Here
4) Run The Script
5) Select All The Audio
6) Write Segment Duration (Recommended For Models: 10 Seconds)
7) Press Split Audio Files(It Will Take Some Time)
8) When There Is A Pop Up Of Audios Has Been Splitted, Your Work Has Done!
9) There Will Be A Zip Named "audio_segments" It Will Have The All Audios Files!


# Using the application
The application presents a GUI with the following elements:

1. Browse button: Allows you to select one or more audio files (.wav or .mp3 format) from your file system.

2. Segment Duration field: Allows you to specify the duration (in seconds) for each segment of audio.

3. Split Audio Files button: Begins the process of splitting the selected audio files.

4. Progress bar: Displays the progress of the splitting process.

To use the application, follow these steps:

1. Click the "Browse" button and select one or more audio files.

2. Enter a segment duration (in seconds) into the "Segment Duration" field.

3. Click the "Split Audio Files" button.

The application will remove silence from the audio files and split each file into segments of the specified duration. The segments will be saved as separate audio files and compressed into a zip file named audio_segments.zip in the same directory as the script.


Notes: 

. It Might Take A Lot Of Time For Many Audios Might Even Not Respond But It Will Get Completed Just Keep Patience!

. The application removes silence from audio files based on pydub's split_on_silence function, which considers anything quieter than -40 dBFS as silence.

. The script is designed to handle large audio files and uses multiprocessing to speed up the splitting process.

. The script will notify you with a popup message once all the audio files have been successfully split.

. The resulting segments are saved in the same format as the input audio files.
