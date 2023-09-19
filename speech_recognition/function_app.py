import azure.functions as func
import logging
import psycopg2
from psycopg2 import sql
import speech_recognition as sr
import mimetypes
from tempfile import NamedTemporaryFile
import moviepy.editor as mp

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="http_speech_recognition", methods=['POST'])
def http_speech_recognition(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Get the file from the request body
    file = req.files.get("file")

    if not file:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a video or audio file in the request to execute functionality.",
             status_code=400
        )

    try:
        # Get the file extension
        file_extension = file.filename.split(".")[-1]

        # Check if the file is a video or audio file
        if file_extension in ["mp4", "wav"]:

            if file_extension == "mp4":
                with NamedTemporaryFile(suffix=".mp4", delete=False) as temp_mp4:
                    temp_mp4.write(file.read())
                    logging.info(f"File saved to {temp_mp4.name}")
                    wav_filename = convertToWav(temp_mp4.name)
                    logging.info(f"File converted to {wav_filename}")
            else:
                with NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                    temp_wav.write(file.read())
                    wav_filename = temp_wav.name

            # Transcribe the wav file to text
            return transciptWavToText(wav_filename)

        else:
            return func.HttpResponse(
                "This HTTP triggered function executed successfully, but file isn't .mp4 or .wav. Pass a video or audio file in the request to execute functionality.",
                status_code=400
            )

    except Exception as e:
        return func.HttpResponse(
            f"Internal Error: {str(e)}",
            status_code=500
        )

def convertToWav(mp4_file):
    logging.info("Converting mp4 file to wav file.")
    video = mp.VideoFileClip(mp4_file)
    audio = video.audio

    with NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
        audio.write_audiofile(temp_wav.name, codec='pcm_s16le')
        logging.info(f"Audio file saved to {temp_wav.name}")
        return temp_wav.name

def transciptWavToText(wav_file):
    logging.info("Transcribing wav file to text.")
    r = sr.Recognizer()
    with sr.AudioFile(wav_file) as source:
        data = r.record(source)
    text = r.recognize_google(data, language="es-MX")

    # Insert text into PostgreSQL database as a txt file
    cnx = psycopg2.connect(user="your_user_name", password="password", host="your_azure_postgresql_host", port=5432, database="database_name")
    cur = cnx.cursor()
    insert_query = sql.SQL("INSERT INTO speech_recognition_text (text_transcript) VALUES (%s);")
    cur.execute(insert_query, (text,))
    cnx.commit()
    cur.close()
    cnx.close()

    return func.HttpResponse(
        "Transcription saved successfully in PostgreSQL database.",
        status_code=200
    )
