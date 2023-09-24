import azure.functions as func
import logging

# Word Cloud imports
import os
from PIL import Image
import numpy as np
from io import BytesIO
from wordcloud import WordCloud

# Speech Recognition imports
import json
import speech_recognition as sr
import tempfile
import moviepy.editor as mp

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


# Word Cloud function
@app.route(route="word_cloud", methods=["POST"])
def word_cloud(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python word_cloud HTTP trigger function processed a request.")

    # Get text file from the request parameters
    req_body = req.get_json()
    text = req_body.get("text")
    if not text:
        return func.HttpResponse(
            'Bad request: Pass a json like text:"my text" to execute functionality.',
            status_code=400,
        )

    if text:
        try:
            d = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
            logo_mask = np.array(Image.open(os.path.join(d, "logo.png")))

            wc = WordCloud(
                background_color="white",
                max_words=2000,
                mask=logo_mask,
                contour_width=1,
                contour_color="steelblue",
                colormap="winter",
                height=300,
                width=100,
            )

            # Generate word cloud
            wc.generate(text)

            # Convert the image to binary and save it
            img_bytes = BytesIO()
            wc.to_image().save(img_bytes, format="PNG")
            img_bytes.seek(0)

            return func.HttpResponse(
                img_bytes.getvalue(),
                mimetype="image/png",
                status_code=200
            )
        except Exception as e:
            return func.HttpResponse(f"Internal Error: {e}", status_code=500)


# Speech recognition required functions
def convertToWav(mp4_file):
    logging.info("Converting mp4 file to wav file.")
    video = mp.VideoFileClip(mp4_file)
    audio = video.audio

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=tempfile.gettempdir()) as temp_wav:
        audio.write_audiofile(temp_wav.name, codec="pcm_s16le")
        logging.info(f"Audio file saved to {temp_wav.name}")
        return temp_wav.name

def transciptWavToText(wav_file):
    logging.info("Transcribing wav file to text.")
    r = sr.Recognizer()
    with sr.AudioFile(wav_file) as source:
        data = r.record(source)
    text = r.recognize_google(data, language="es-MX")

    return json.dumps({"text": text})


# Speech recognition function
@app.route(route="speech_recognition", methods=["POST"])
def speech_recognition(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python speech_recognition HTTP trigger function processed a request.")

    # Get the file from the request body
    file = req.files.get("file")

    if not file:
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a video or audio file in the request to execute functionality.",
            status_code=400,
        )

    try:
        # Get the file extension
        file_extension = file.filename.split(".")[-1]

        # Check if the file is a video or audio file
        if file_extension in ["mp4", "wav"]:
            if file_extension == "mp4":
                with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False, dir=tempfile.gettempdir()) as temp_mp4:
                    temp_mp4.write(file.read())
                    logging.info(f"File saved to {temp_mp4.name}")
                    wav_filename = convertToWav(temp_mp4.name)
                    logging.info(f"File converted to {wav_filename}")
            else:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=tempfile.gettempdir()) as temp_wav:
                    temp_wav.write(file.read())
                    wav_filename = temp_wav.name

            # Transcribe the wav file to text
            result = transciptWavToText(wav_filename)

            return func.HttpResponse(
                result,
                mimetype="application/json",
                status_code=200
            )

        else:
            return func.HttpResponse(
                "Bad request: File isn't .mp4 or .wav. Pass a video or audio file accepted formats in the request to execute functionality.",
                status_code=400,
            )

    except Exception as e:
        return func.HttpResponse(f"Internal Error: {str(e)}", status_code=500)