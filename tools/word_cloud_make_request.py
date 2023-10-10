import requests

# URL of your Azure Function or local deployment
function_url = "http://localhost:7071/api/word_cloud"

# JSON data to send in the POST request
json_data = {"text": "La mayoria de las problematicas sociales que vivo en mi localidad estan relacionadas con la diferencia en el acceso a servicios basicos, asi como agua, luz, electricidad, entre otros. Asi que creo que es muy importante hacer un cambio en este aspecto."}

# Make the POST request
response = requests.post(function_url, json=json_data)

# Check the response status code and content
if response.status_code == 200:
    print("Azure Function executed successfully.")

    # Define the path where you want to save the image locally
    local_image_path = "wordcloud.png"  # Modify this as needed

    # Save the received image data to the local file
    with open(local_image_path, "wb") as image_file:
        image_file.write(response.content)

    print(f"Image saved locally as '{local_image_path}'")
else:
    print("Error: Azure Function returned a non-200 status code.")
