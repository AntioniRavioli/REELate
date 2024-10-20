from cartesia import Cartesia
from dotenv import load_dotenv
import os
import subprocess
import ffmpeg

# library to translate text
from translate import Translator

# libraries to take in videos/audios and convert to text
import moviepy.editor as mp
import speech_recognition as sr
import whisper


load_dotenv()

# grab audio or video file and convert audio to text, store in a string

model = whisper.load_model('base')

# load audio and pad/trim it to fit 30 seconds

audio = whisper.load_audio("reddit_story.mov")
audio = whisper.pad_or_trim(audio)

# make log-Mel spectrogram and move it to the same device as the model
mel = whisper.log_mel_spectrogram(audio).to(model.device)

# detect spoken language
_, probs = model.detect_language(mel)

# output the detected language from input file
print(f"Detected language: {max(probs, key=probs.get)}")

# decode the audio
options = whisper.DecodingOptions()
result = whisper.decode(model, mel, options)





# User input to choose the target language
print("What language would you like to convert this audio to?")
language_choice = input("[0] Spanish\n[1] Korean\n[2] Chinese\n[3] English\n[4] French\n[5] Portugese\n[6] Japanese\n[7] Hindi\n[8] Italian\n[9] Dutch\n[10] Polish\n[11] Russian\n[12] Swedish\n[13] German\n[14] Turkish\n")

# Map user's choice to a language code
if language_choice == "0":
    print("You chose Spanish!")
    target_lang = "es"
elif language_choice == "1":
    print("You chose Korean!")
    target_lang = "ko"
elif language_choice == "2":
    print("You chose Chinese!")
    target_lang = "zh"
elif language_choice == "3":
    print("You chose English!")
    target_lang = "en"
elif language_choice == "4":
    print("You chose French!")
    target_lang = "fr"
elif language_choice == "5":
    print("You chose Portugese!")
    target_lang = "pt"
elif language_choice == "6":
    print("You chose Japanese!")
    target_lang = "ja"
elif language_choice == "7":
    print("You chose Hindi!")
    target_lang = "hi"
elif language_choice == "8":
    print("You chose Italian!")
    target_lang = "it"
elif language_choice == "9":
    print("You chose Dutch!")
    target_lang = "nl"
elif language_choice == "10":
    print("You chose Polish!")
    target_lang = "pl"
elif language_choice == "11":
    print("You chose Russian!")
    target_lang = "ru"
elif language_choice == "12":
    print("You chose Swedish!")
    target_lang = "sv"
elif language_choice == "13":
    print("You chose German!")
    target_lang = "de"
elif language_choice == "14":
    print("You chose Turkish!")
    target_lang = "tr"
else:
    print("Invalid choice. Exiting...")
    exit()

# Function to translate text into the chosen language
def translate(text, target_lang):
    translator = Translator(to_lang=target_lang)
    translation = translator.translate(text)
    return translation

# Translate the text based on the user's choice
text = result.text
translated_text = translate(text, target_lang)


# load Cartesia API key to be able to output audio with AI voice
client = Cartesia(api_key=os.environ.get("CARTESIA_API_KEY"))

voice_id = "d3d3d53e-1760-4a63-919f-6fbdfd0a984f"  # Anthony Legrama
model_id = "sonic-multilingual"
transcript = translated_text
voice = client.voices.get(id=voice_id)
language = target_lang

output_format = {
    "container": "raw",
    "encoding": "pcm_f32le",
    "sample_rate": 44100,
}

# Set up a WebSocket connection
ws = client.tts.websocket()

# Open a file to write the raw PCM audio bytes to
f = open("Anthony.pcm", "wb")

# Create new file and output transcript (better for reading what is being said by AI voice)
with open('Anthony_Caption.txt', 'w', encoding='utf-8') as x:
    # Write text to the file
    x.write(transcript)

# Generate and stream audio
for output in ws.send(
    model_id=model_id,
    transcript=transcript,
    voice_embedding=voice["embedding"],
    #voice_id=voice_id,
    stream=True,
    output_format=output_format,
    language=language,
):
    buffer = output["audio"]  # buffer contains raw PCM audio bytes
    f.write(buffer)

# Close the connection to release resources
ws.close()
f.close()

# Convert the raw PCM bytes to a WAV file
ffmpeg.input("Anthony.pcm", format="f32le").output("Anthony.wav").run()

# Play the file
subprocess.run(["ffplay", "-autoexit", "-nodisp", "Anthony.wav"])
