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

# Define PostgreSQL database connection parameters
db_connection_string = "dbname=sel4c user=azure_functions password=azure1# host=sel4c-postgresql.postgres.database.azure.com"

@app.route(route="http_word_cloud")
def http_word_cloud(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    text_file = req.files.get("text")
    if not text_file:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a text file for a personalized response.",
             status_code=200
        )
    

    if text_file:
        
        text = text_file.read().decode("utf-8")
        d = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
        alice_mask = np.array(Image.open(os.path.join(d, "logo.png")))

        stopwords = set(STOPWORDS)
        stopwords.add("said")

        wc = WordCloud(
            background_color="white", max_words=2000, mask=alice_mask,
            stopwords=stopwords, contour_width=1, contour_color='steelblue',
            colormap='winter', height=300, width=100
        )

        # Generate word cloud
        wc.generate(text)

        # Convert the image to bytes
        img_bytes = BytesIO()
        wc.to_image().save(img_bytes, format='PNG')
        img_bytes.seek(0)

        conn = None
        # Store the image in PostgreSQL
        try:
            conn = psycopg2.connect(db_connection_string)
            cur = conn.cursor()
            
            # Define a SQL query to insert the image into the database
            insert_query = sql.SQL("INSERT INTO word_cloud_images (image_data) VALUES (%s);")
            
            # Execute the query with the image bytes
            cur.execute(insert_query, (img_bytes.read(),))
            conn.commit()
            
            return func.HttpResponse(
                "Image saved in PostgreSQL database.",
                status_code=200
            )
        except Exception as e:
            return func.HttpResponse(
                f"Error saving image to PostgreSQL: {str(e)}",
                #status_code=500
            )
        finally:
            if conn:
                cur.close()
                conn.close()