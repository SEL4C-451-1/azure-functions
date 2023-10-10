import azure.functions as func
import logging

# Word Cloud imports
import os
from PIL import Image
import numpy as np
from io import BytesIO
from wordcloud import WordCloud
import pickle
import gensim
import nltk

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
            'Bad request: Pass a JSON like text:"my text" to execute functionality.',
            status_code=400,
        )

    if text:
        try:
            logging.info(f'Text received: {text}')
            
            # Generate topics and add them to the text
            text_data = [text]
            nltk.download('stopwords')
            sw_nltk = nltk.corpus.stopwords.words('spanish')
            
            def preprocess(text):
                result = []
                for token in gensim.utils.simple_preprocess(text):
                    if token not in sw_nltk:
                        result.append(token)
                return result
            
            processed_text_data = [preprocess(text) for text in text_data]
            dictionary = gensim.corpora.Dictionary(processed_text_data)
            corpus = [dictionary.doc2bow(text) for text in processed_text_data]

            # Save the corpus to a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_corpus_file:
                pickle.dump(corpus, temp_corpus_file)
                temp_corpus_file.close()
                # Get the path of the temporary corpus file
                temp_corpus_path = temp_corpus_file.name

            # Save the dictionary to a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_dict_file:
                dictionary.save(temp_dict_file.name)
                temp_dict_file.close()
                # Get the path of the temporary dictionary file
                temp_dict_path = temp_dict_file.name

            ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=5, id2word=dictionary, passes=15)

            # Save the model to a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_model_file:
                ldamodel.save(temp_model_file.name)
                temp_model_file.close()
                # Get the path of the temporary model file
                temp_model_path = temp_model_file.name

            topics = ldamodel.print_topics(num_words=3)
            for topic in topics:
                topic_id, topic_words = topic
                word_probabilities = topic_words.split('+')
                words = [word_prob.split('*')[1].strip().strip('"') for word_prob in word_probabilities]
                probabilities = [float(word_prob.split('*')[0].strip()) for word_prob in word_probabilities]
                for word, prob in zip(words, probabilities):
                    text_data[0] += (' ' + word) * int(prob * 100)

            # Generate word cloud
            logging.info("Topics appended.")
            d = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
            logo_mask = np.array(Image.open(os.path.join(d, "logo.png")))

            wc = WordCloud(
                background_color="white",
                max_words=2000,
                mask=logo_mask,
                contour_width=5,
                contour_color="steelblue",
                colormap="Blues_r",
                height=300,
                width=100,
            )

            # Generate word cloud
            logging.info("Generating word cloud.")
            wc.generate(text)

            # Convert the image to binary and save it
            img_bytes = BytesIO()
            wc.to_image().save(img_bytes, format="PNG")
            img_bytes.seek(0)

            # Removing temporary files
            os.remove(temp_corpus_path)
            os.remove(temp_dict_path)
            os.remove(temp_model_path)

            logging.info("Word cloud generated successfully. Returning image.")
            return func.HttpResponse(
                img_bytes.getvalue(),
                mimetype="image/png",
                status_code=200
            )
        except Exception as e:
            logging.error(f"Internal Error: {e}")
            return func.HttpResponse(f"Internal Error: {e}", status_code=500)


# Speech recognition required functions
def convertToWav(mp4_file):
    logging.info("Converting mp4 file to wav file.")
    video = mp.VideoFileClip(mp4_file)
    audio = video.audio

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=tempfile.gettempdir()) as temp_wav:
        audio.write_audiofile(temp_wav.name, codec="pcm_s16le")
        temp_wav.close()
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
                    temp_mp4.close()
                    wav_filename = convertToWav(temp_mp4.name)
                    logging.info(f"File converted to {wav_filename}")
            else:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False, dir=tempfile.gettempdir()) as temp_wav:
                    temp_wav.write(file.read())
                    wav_filename = temp_wav.name

            # Transcribe the wav file to text
            result = transciptWavToText(wav_filename)

            # Clean up: Delete the temporary files
            if file_extension == "mp4" and 'temp_mp4' in locals():
                os.remove(temp_mp4.name)
            elif 'temp_wav' in locals():
                os.remove(temp_wav.name)

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