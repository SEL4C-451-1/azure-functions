import moviepy.editor as mp
import speech_recognition as sr

video = mp.VideoFileClip("./video.mp4")

audio_file = video.audio
audio_file.write_audiofile("audio.wav")

r = sr.Recognizer()

with sr.AudioFile("audio.wav") as source:
	data = r.record(source)

text = r.recognize_google(data, language="es-MX")

print("\nThe video says...\n")
print(text)
