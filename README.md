# azure-functions

## Running it

### Speech Recognition

<details close>
<summary>Expand</summary>
To run the speech recognition function you can do it locally using VS Code or deploy it to Azure.

Then execute a web request to the function endpoint using the [speech_recognition_make_request.py](tools/speech_recognition_make_request.py) script:
- The use of the script requires the installation of the requests python package.
:exclamation: :exclamation: :exclamation: Be sure to modify the function_url and file_path according to your environment. :exclamation: :exclamation: :exclamation:

:exclamation: :exclamation: :exclamation: As for now, the function takes around 18 seconds to process a request with a similar video input such as the sample provided, further testing is required. :exclamation: :exclamation: :exclamation:

</details>

### Word Cloud

<details close>
<summary>Expand</summary>
To run the word cloud function you can do it locally using VS Code or deploy it to Azure.

Then execute a web request to the function endpoint using the [word_cloud_make_request.py](tools/word_cloud_make_request.py) script:
- The use of the script requires the installation of the requests python package.
:exclamation: :exclamation: :exclamation: Be sure to modify the function_url and file_path according to your environment. :exclamation: :exclamation: :exclamation:

:exclamation: :exclamation: :exclamation: As for now, the function takes around 18 seconds to process a request with a similar video input such as the sample provided, further testing is required. :exclamation: :exclamation: :exclamation:

</details>

## Deploying to Azure

<details close>
<summary>Expand</summary>
To deploy the any of the functions to Azure I recommend using VS Code.

:exclamation: Be sure to already haev the postgresql database deployed and to modify the connection string according to your environment. _cnx = psycopg2.connect(user="your_user_name", password="password", host="your_azure_postgresql_host", port=5432, database="database_name")_ :exclamation:

1. Install the Azure Tools extension for VS Code; Azurite (Azure Storage Emulator) extension is recommended; [Azure Functions Core Tools](https://github.com/Azure/azure-functions-core-tools/blob/v4.x/README.md#installing)
2. Sign in to Azure using the Azure: Sign In command.
3. Create a new folder on root to contain the function app.
4. Create a virtual environment in the folder you just created.
``` python
python -m venv .venv
```
5. Go to the Azure tab and click on Create Function... option on the Functions button.
6. Select the folder you just created 3 steps above.
7. Select Python (Programming Model V2) as the language.
8. Select the virtual environment you just created if prompted.
9. Select HTTP trigger as the template. Write the name of the function and select anonymous as the authorization level.
10. Copy and paste the files from word_cloud folder to the folder you just created.
11. Run the function locally by starting Azurite though the command palette: **F1** + _Azurite: Start_, then pressing **f5** and ensuring correct functionality.
12. Create a new Function App on Azure through the Resources tab at the Azure extension tab, or use the Azure portal.
    - You must:
        - Select an active subscription.
        - Create a new resource group or use an existing one.
        - Select the python runtime stack.
        - Select the region you want to deploy the function app.
13. Go to the Workspace tab at the Azure extension tab and click on Deploy to Function App on the Functions button.

:question: :question: :question: If you have any issues deploying the function you can look at the following [tutorial](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python?pivots=python-mode-configuration). :question: :question: :question:

:exclamation: :exclamation: :exclamation: If there is any other issue, the ones I had were related to networking allowed IP addresses and postgresql python packages. :exclamation: :exclamation: :exclamation:

</details>
