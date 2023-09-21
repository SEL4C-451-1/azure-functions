import azure.functions as func
import logging
import os
from PIL import Image
import numpy as np
import os
from io import BytesIO
from wordcloud import WordCloud, STOPWORDS
import psycopg2
from psycopg2 import sql

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="http_word_cloud", methods=['POST'])
def http_word_cloud(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Get text file from the request parameters
    text_file = req.files.get("text")
    if not text_file:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a text file to execute functionality.",
             status_code=400
        )
    

    if text_file:
        cnx = None
        try:
            cnx = psycopg2.connect(user="your_user_name", password="password", host="your_azure_postgresql_host", port=5432, database="database_name")
            cur = cnx.cursor()

            # Retrieve existing text from the database from table word_cloud_text
            cur.execute("SELECT text FROM word_cloud_text WHERE id = 1")
            existing_text_bytes = cur.fetchone()[0]

            # Convert the memoryview object to a string
            existing_text = existing_text_bytes.tobytes().decode("utf-8")

            if not existing_text:
                return func.HttpResponse(
                    "Failed to retrieve text from the database.",
                    status_code=500
                )

            # Append new text to the existing text
            new_text = existing_text + text_file.read().decode("utf-8")

            # Update the database with the modified text
            update_query = sql.SQL("UPDATE word_cloud_text SET text = %s WHERE id = 1")
            cur.execute(update_query, (new_text,))
            cnx.commit()

            # Get mask image to create word cloud
            d = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
            logo_mask = np.array(Image.open(os.path.join(d, "logo.png")))

            # Create a set of stopwords which are ignored during teh creation of the word cloud
            stopwords = set(STOPWORDS)
            stopwords.add("said")

            wc = WordCloud(
                background_color="white", max_words=2000, mask=logo_mask,
                stopwords=stopwords, contour_width=1, contour_color='steelblue',
                colormap='winter', height=300, width=100
            )

            # Generate word cloud
            wc.generate(new_text)

            # Convert the image to binary and save it
            img_bytes = BytesIO()
            wc.to_image().save(img_bytes, format='PNG')
            img_bytes.seek(0)

            # Store the image in PostgreSQL
            insert_image_query = sql.SQL("INSERT INTO word_cloud_images (image_data) VALUES (%s);")
            cur.execute(insert_image_query, (img_bytes.read(),))
            cnx.commit()

            return func.HttpResponse(
                "Image saved succesfully in PostgreSQL database.",
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