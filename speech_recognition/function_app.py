import azure.functions as func
import logging
import psycopg2
from psycopg2 import sql
import moviepy.editor as mp
import speech_recognition as sr

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="http_speech_recognition")
def http_speech_recognition(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Get video/audio file from the request parameters
    file = req.files.get("file")
    if not file:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a video or audio file to execute functionality.",
             status_code=200
        )
    
    if file:
        cnx = None
        try:
            cnx = psycopg2.connect(user="your_user_name", password="password", host="your_azure_postgresql_host", port=5432, database="database_name")
            cur = cnx.cursor()

            video = mp.VideoFileClip(file)

            audio_file = video.audio

            r = sr.Recognizer()

            with sr.AudioFile(audio_file) as source:
                data = r.record(source)

            text = r.recognize_google(data, language="es-MX")

            # Insert text into PostgreSQL database as a txt file
            insert_query = sql.SQL("INSERT INTO speech_recognition_text (text) VALUES (%s)")
            cur.execute(insert_query, (text))
            cnx.commit()

            return func.HttpResponse(
                "Transcription saved succesfully in PostgreSQL database.",
                status_code=200
            )

        except Exception as e:
            return func.HttpResponse(
                f"Internal Error: {e}",
                status_code=500
            )
        finally:
            # Close database connection
            if cnx:
                cur.close()
                cnx.close()