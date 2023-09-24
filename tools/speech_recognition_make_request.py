import requests
import json

# URL of your Azure Function or local deployment
function_url = "https://http-word-cloud.azurewebsites.net/api/speech_recognition?code=_FB1pPcUH0r-p5qzzC99JyiK1BRfMhJci2yL4wVw-azwAzFuhcv83w=="

# Path to the audio or video file you want to send
file_path = "../samples/text.mp4"

# Create a dictionary with the file data
files = {"file": open(file_path, "rb")}

# Make the POST request
response = requests.post(function_url, files=files)

# Check the response status code and content
if response.status_code == 200:
    print("Azure Function executed successfully.")
    # Parse the JSON response
    try:
        response_json = json.loads(response.text)
        print("Transcription:", response_json["text"])
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {str(e)}")
else:
    print("Error: Azure Function returned a non-200 status code.")
    print(response.text)
