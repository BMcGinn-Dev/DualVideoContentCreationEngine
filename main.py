from datetime import timedelta
import os
import whisper
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.fx.all import crop
from moviepy import *
import random
import whisper_timestamped
from gtts import gTTS
import time
from pydub import AudioSegment
import math
import pyttsx3
from moviepy.editor import VideoFileClip
from moviepy.config import change_settings


# import Pygame

cartoon_video_path = "{ENTER FULL PATH TO CARTOON .MP4}"
mindless_video_path = "{ENTER FULL PATH TO MINDLESS VIDEO .MP4}"
music_path = "{ENTER FULL PATH TO BACKGROUND MUSIC .MP3 -- IT IS CURRENTLY DISABLED}"
music_mp3 = "{ENTER JUST THE .MP3 TO BACKGROUND MUSIC .MP3 -- IT IS CURRENTLY DISABLED}"
content_folder_path = "Y_Clips"
mindless_folder_path = "X_Clips"
stacked_folder_path = "XY_Clips"
temp_audio_path = "TempAudio"
final_video_path = "FinalVideos"


# This is a list of the seconds of each clip in the cartoon_video_path. These of course need to be very accurate
#clip_times = [[0, 13], [13.5, 35], [36, 44], [45, 59], [68, 77]]
clip_times =[[0, 60],[60.01, 120],[120.01, 145]]


# ------ Helper Functions -------

def we_are_done(sentence):
   # Initialize the TTS engine
    engine = pyttsx3.init()

    # Set properties (optional)
    engine.setProperty('rate', 150)  # Speed of speech

    # Convert text to speech and play
    engine.say(sentence)
    engine.runAndWait()

    # Allow the speech to play for a few seconds
    time.sleep(5)

def show_clip_times(clip_times_list):
    for i, ranges in enumerate(clip_times_list):
        print(f"Clip #{i+1} begins at time: {ranges[0]} and ends at time: {ranges[1]}")


def get_clip_duration(video_clip):
    print("\n--- Getting Clip Duration --- \n")
    clip_duration = video_clip.duration
    return clip_duration


def background_music_jump(music_mp3):
    print("\n--- Jumping Background Music --- \n")

    music_path = f"MusicAudio/{music_mp3}"
    audio = AudioSegment.from_file(music_path)
    # Set the start time to skip the first 30 seconds (30,000 milliseconds)
    start_time = 30 * 1000  # 30 seconds * 1000 (milliseconds per second)
    # Trim the audio to skip the first 30 seconds
    trimmed_audio = audio[start_time:]

    # Export the trimmed audio to a new file
    trimmed_audio.export((f"MusicAudio/{music_mp3}_trimmed.mp3"), format="mp3")


def add_background_music(video_clip, music_path):
    print("\n--- Adding Background Music --- \n")

    # Get the duration of the video clip
    video_duration = get_clip_duration(video_clip)

    # Create audio file from music path
    music_clip = AudioFileClip(music_path)

    # Set duration of audio file to that of the video duration
    music_clip = music_clip.set_duration(video_duration)

    # Set audio of video to the music (Can you hear the music?)
    video_clip = video_clip.set_audio(music_clip)

    return video_clip


def crop_to_iphone_size(vid):
    print("\n---  Cropping to iPhone size --- ")
    (w, h) = vid.size
    vid = crop(vid, width=596, height=530, x_center=w / 2, y_center=h / 2)
    return vid


def vertically_stack(content_file, mindless_file):
    print("\n--- Vertically Stacking Clips ---")
    content_buffer = "Y_Clips\\"
    mindless_buffer = "X_Clips\\"

    full_content_path = content_buffer + content_file
    full_mindless_path = mindless_buffer + mindless_file

    print(full_content_path)
    print(full_mindless_path)

    # Load the video clips
    content_vid = VideoFileClip(full_content_path)
    mindless_vid = VideoFileClip(full_mindless_path)

    # Ensuring both videos have the same duration
    duration = min(content_vid.duration, mindless_vid.duration)
    content_vid = content_vid.subclip(0, duration)
    mindless_vid = mindless_vid.subclip(0, duration)

    # Stack the videos vertically --> Change the content_vid & the mindless_vid if you want to change the orientation. First video is on top, second is on bottom.
    stacked_clip = clips_array([[mindless_vid], [content_vid]])

    return stacked_clip


def convert_to_mp3(vid, count):
    print("\n--- Converting Video to MP3 ---")
    # video_clip = VideoFileClip(vid)
    audio_clip = vid.audio
    audio_clip.write_audiofile(f"TempAudio/temp_audio_{count}.mp3")
    return audio_clip


def transcribe_audio(audio_clip):
    print("\n--- Transcribing Audio ---")
    model = whisper.load_model("medium.en")
    # audio = whisper.load_audio(audio_clip)
    result = whisper_timestamped.transcribe(model, audio_clip)
    print(result["text"])
    return result

    # Specify the path to the Montserrat-Bold.ttf file
    font_path_bold = "Fonts\Montserrat-Bold\static\Montserrat-Bold.ttf"

    subs = []
    clip = VideoFileClip(video)
    subs.append(clip)

    for segment in result["segments"]:
        for word in segment["words"]:
            text = word["text"].upper()
            start = word["start"]
            end = word["end"]
            duration = end - start

            # Create text clip using MoviePy's TextClip
            txt_clip = TextClip(
                txt=text,
                fontsize=55,
                color="yellow",
                bg_color="black",
                stroke_width=2,
                stroke_color="white",
                font=font_path_bold,
                method="caption",  # Use 'caption' method instead of 'label' (default)
                kerning=True,
            )

            # Apply shadow effect
            shadow_clip = txt_clip.fx(
                lambda x: x.margin(10, color=(0, 0, 0), opacity=0.7)
            )

            # Apply scaling or "burst" effect
            burst_clip = txt_clip.fx(
                lambda x: x.resize(
                    width=x.w * 1.2, height=x.h * 1.2, resample="bicubic"
                )
            )

            # Set position, start time, and duration for both shadow and burst clips
            shadow_clip = (
                shadow_clip.set_start(start)
                .set_duration(duration)
                .set_pos(("center", "center"))
            )
            burst_clip = (
                burst_clip.set_start(start)
                .set_duration(duration)
                .set_pos(("center", "center"))
            )

            # Add shadow and burst clips to the list
            subs.append(shadow_clip)
            subs.append(burst_clip)

    # Create composite video clip
    composite_clip = CompositeVideoClip(subs)

    # Combine the composite clip with the original video
    final_clip = CompositeVideoClip([clip, composite_clip])

    # Write the final video file
    return final_clip.write_videofile(f"FinalVideos/final_video_{vid_count}.mp4")


def add_subtitles(result, video, vid_count):
    # Specify the corrected path to the BubblegumSans-Regular.ttf file
    font_path_bold = r"F:/CodeProjects/ClipCrop&Merge/Fonts/Bubblegum_Sans/BubblegumSans-Regular.ttf"

    # Check if the font file is found
    try:
        with open(font_path_bold):
            print("Font found")
    except FileNotFoundError:
        print("Font not found")
    subs = []
    clip = VideoFileClip(video)
    subs.append(clip)

    # Flag for the color swap
    flag = True

    for segment in result["segments"]:
        if flag:
            curr_color = 'yellow'
        else:
            curr_color = 'white'

        for word in segment["words"]:
            text = word["text"].upper()
            start = word["start"]
            end = word["end"]
            duration = end - start
            txt_clip = TextClip(
                txt=text,
                fontsize=65,
                color=curr_color,
                stroke_width=4.0,
                stroke_color="black",
                font=font_path_bold,
            )
            txt_clip = (
                txt_clip.set_start(start)
                .set_duration(duration)
                .set_pos(("center", "center"))
            )
            subs.append(txt_clip)
            flag = not flag 

    final_clip = CompositeVideoClip(subs)

    if final_clip.duration > 60:
        final_clip = final_clip.subclip(0, 60)
    
    return final_clip.write_videofile(f"FinalVideos/final_video_{vid_count}.mp4", fps=24)


def add_video_part(clip_path, part):
    print("\n--- Adding Video Part ---")

    video_clip = VideoFileClip(clip_path)
    
    # Create the TextClip
    text_clip = TextClip(
        txt=f"Part {part}.",
        fontsize=60,
        color="blue",
        stroke_width=3.0,
        stroke_color="blue",
    )

    text_clip = text_clip.set_position(("center", 65))
    text_clip = text_clip.set_duration(video_clip.duration)

    final_clip = CompositeVideoClip([video_clip, text_clip])

    if final_clip.duration > 59.5:
        final_clip = final_clip.subclip(.5, 59.8)

    return final_clip.write_videofile(f"FinalFinalVideos/final_video_{part}_wPart.mp4", fps=24)


def clear_all_temp_files():
    print("\n--- Clearing all Temp Files ---")
    # Clear all temp audio files
    for file in os.listdir(temp_audio_path):
        os.remove(os.path.join(temp_audio_path, file))

    for file in os.listdir(content_folder_path):
        os.remove(os.path.join(content_folder_path, file))

    for file in os.listdir(mindless_folder_path):
        os.remove(os.path.join(mindless_folder_path, file))
    
    for file in os.listdir(stacked_folder_path):
        os.remove(os.path.join(stacked_folder_path, file))

    print("--- All temporary files have been removed ---")


# ------ Helper Functions End -------


# ______________________ RUN TIME FUNCTIONS BEGIN _____________________________________________________________________


# Creates numerous subclips of the original video based on the clip_times list, writes them to the Y_Clips folder
def create_indv_cartoon_clips(cartoon_video_path, clip_times):
    print("\n--- Creating Content Clips --- \n")

    # Loading the original video as a VideoFileClip
    original_video = VideoFileClip(cartoon_video_path)

    # Creating a list of VideoFileClips, this may take awhile & it uses CPU
    intervaled_clips = []

    # Creating video clips that are subclips of the original video based on the clip_times list.
    for interval in clip_times:
        start_time, end_time = interval[0], interval[1]
        temp_clip = original_video.subclip(start_time, end_time)
        intervaled_clips.append(temp_clip)

    # Printing the length of the intervaled_clips list. This should be the same as the length of the clip_times list.
    clip_count = len(intervaled_clips)

    """
    print(f"Intervaled Clips: \n {intervaled_clips} \n")
    print(f"Clip count: {clip_count}")
    """

    # Writing the intervaled_clips to the Y_Clips folder.
    for i, clip in enumerate(intervaled_clips):
        # Firstly cropping the clips to fit iphone ratio, iPhone aspect is w=480, he=720
        clip = crop_to_iphone_size(clip)

        print(f"Creating clip {i+1} of {clip_count}")
        clip.write_videofile(f"Y_Clips/content_clip{i+1}.mp4")

    return clip_count


# Now we need a function to create the gameplay clips that are cropped to the same size, and have the same length as the content_subclips for each clip in the Y_clips folder
# We can take the large video and pick a random point in the middle and run that for as long as the corresponding clip & then crop that to iPhone size
# This also removes the audio from the clip
def create_mindless_clips(mindless_video_path, folder_path="Y_Clips"):
    print("\n--- Creating mindless clips")
    count = 1
    for filename in os.listdir(folder_path):
        if filename.endswith(".mp4"):
            print(f"Creating mindless clip for {filename}")

            # Loading the video as a VideoFileClip
            video_clip = VideoFileClip(f"{folder_path}/{filename}")

            # Getting the duration of the video
            content_clip_duration = get_clip_duration(video_clip)

            # Pick a random point in the middle of the mindelss clip
            mindless_clip = VideoFileClip(mindless_video_path)
            mindless_clip_duration = get_clip_duration(mindless_clip)

            """
            # Printing the duration of the clips
            print(f"Content clip duration: {content_clip_duration}")
            print(f"Mindless clip duration: {mindless_clip_duration}")
            """

            # Pick a random point in the middle of the mindelss clip
            random_start_time = random.uniform(
                0, mindless_clip_duration - content_clip_duration
            )

            # Crop the mindelss clip to the same size as the content clip, and then crop it to iPhone size
            timed_mindless_clip = mindless_clip.subclip(
                random_start_time, random_start_time + content_clip_duration
            )

            print(f"Content clip duration: {content_clip_duration}")
            print(f"Timed mindless clip duration: {timed_mindless_clip.duration}")

            # Cropping the mindless clip to fit iphone ratio, iPhone aspect is w=480, he=720
            timed_mindless_clip = crop_to_iphone_size(timed_mindless_clip)

            # Remove the audio from the mindless clip
            timed_mindless_clip = timed_mindless_clip.without_audio()

            # Adding the background music to the mindless clip which is now trimmed to the same length as the content clip & cropped to iPhone size
            """
            #timed_mindless_clip = add_background_music(timed_mindless_clip, music_path)
            """

            # Writing the cropped and timed mindless clip to the X_Clips folder
            # print(f"Creating clip } of {clip_count}")
            timed_mindless_clip.write_videofile(f"X_Clips/mindless_clip{count}.mp4")
            count += 1


# Creating a function that will take the content clips and the mindless clips and stack them together vertically
def created_stacked_clips(content_folder_path, mindless_folder_path):
    print("\n--- Stacking Clips --- ")

    content_file_count = len(os.listdir(content_folder_path))
    mindless_file_count = len(os.listdir(mindless_folder_path))

    if content_file_count != mindless_file_count:
        print(
            f"The Content and Mindless file counts do not match. \nThe content file count is {content_file_count}\nThe mindless file count is {mindless_file_count}. \nExiting..."
        )
        return
    else:
        print(
            f"The file counts match!! \nThe content file count is {content_file_count}\nThe mindless file count is {mindless_file_count}. \n"
        )

        content_file_list = []
        mindless_file_list = []

        for filename in os.listdir(content_folder_path):
            content_file_list.append(filename)

        for filename in os.listdir(mindless_folder_path):
            mindless_file_list.append(filename)

        print(content_file_list)
        print(mindless_file_list)

        for i in range(content_file_count):
            temp_content_file = content_file_list[i]
            temp_mindless_file = mindless_file_list[i]
            stacked_vid = vertically_stack(temp_content_file, temp_mindless_file)
            stacked_vid.write_videofile(f"XY_Clips/stacked_clip{i+1}.mp4")


# NEXT UP TO IS ADD SUBTITLES AND YOURE GOLDEN !!!!!
def generated_subtitled_videos():
    print("\n--- Generating Subtitled Videos ---")
    result_list = []

    # Set count for naming of audio files
    count = 1

    # Set count for naming of video files
    vid_count = 1

    # Generate temp_audio files into TempAudio folder --> could make this a function if I wanted
    
    for filename in os.listdir(content_folder_path):
        # Need to convert the CONTENT VIDEOS to a video file
        vid = VideoFileClip(f"{content_folder_path}/{filename}")

        # Turn that video file to an mp3 and increase count by 1
        audio = convert_to_mp3(vid, count)
        count += 1
        time.sleep(1)

    # Locating the temp_audio files and transcribing each using WhisperAI. This creates a 'result' dictionary that we append to the result_list. Directly creating final videos from here
    for filename in os.listdir(temp_audio_path):
        full_audio_path = temp_audio_path + "/" + filename
        result = transcribe_audio(full_audio_path)
        result_list.append(result)
    

    # Adding the subtitles to the final videos and writing them to the FinalVideos folder.
    for idx, file in enumerate(os.listdir(stacked_folder_path)):
        full_file_path = f"{stacked_folder_path}/{file}"
        add_subtitles(result_list[idx], full_file_path, vid_count)
        vid_count += 1

    vid_count = 1

    # Add the "Part X" textclip to the file
    for idx, file in enumerate(os.listdir(final_video_path)):
        full_file_path = f"{final_video_path}/{file}"
        add_video_part(full_file_path, vid_count)
        vid_count += 1

# _________________________________________ RUN TIME FUNCTIONS END _______________________________________________________________
video_paths = [

]

for vid_path in video_paths:
    cartoon_video_path = vid_path
    break

# Shows the clip times, you need to manually create this list
show_clip_times(clip_times)

# Creates individual cartoon clips based upon your list input, returns clip count
clip_count = create_indv_cartoon_clips(cartoon_video_path, clip_times)
print(f"You will be generating: ----------- {clip_count} Cartoon Clips")

# Creates mindless clips based on the timing of the content clips, crops accordingly, and removes audio. If you want to add in background music it is also added here.
create_mindless_clips(mindless_video_path)

# Takes the content clips & the mindless clips & stacks them on top of each other, order can be changed here
created_stacked_clips(content_folder_path, mindless_folder_path)

# Adds subtitles to the video, font and other display can be changed in add_subtitles helper function
generated_subtitled_videos()

#Letting me know we are done
we_are_done("We are done! We are done!")
# Delete all the temporary files
time.sleep(2)
#clear_all_temp_files()


# __________________________________________ Helper Functions Testing  ____________________________________________________________
# Made for running individually

# background_music_jump(music_mp3)

# vertically_stack("content_clip1.mp4", "mindless_clip1.mp4")

# convert_to_mp3("Y_Clips/content_clip1.mp4")

# transcribe_audio("testing.mp3")
