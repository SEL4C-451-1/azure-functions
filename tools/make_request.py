import requests

# URL of your Azure Function or local deployment
function_url = "https://<your_function_app_name>.azurewebsites.net/api/<project>"

# Path to the text, audio or video file you want to send
file_path = "C:/azure-functions/samples/sample_file"

# Create a dictionary with the file data
files = {"file": open(file_path, "rb")}

# Make the POST request
response = requests.post(function_url, files=files)

# Check the response status code and content
if response.status_code == 200:
    print("Azure Function executed successfully.")
    print(response.text)
else:
    print("Error: Azure Function returned a non-200 status code.")
    print(response.text)
