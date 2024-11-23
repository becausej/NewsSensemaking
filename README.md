# NewsSensemaking

## Chrome Extension
* Start the Flask server (server.py)
* Open Chrome -> Extensions -> Manage Extensions
* Turn on Developer Mode
* Click "Load Upacked" and select the "Extension" folder
* It should be running

## Google Cloud API
This also has all the info: [Quickstart](https://cloud.google.com/natural-language/docs/setup)
### Google Cloud Project
* Everyone should all be on the project with ID: `news-sensemaking`
* Confirm by visiting the [website](https://console.cloud.google.com/welcome/new?inv=1&invt=AbiMxA&project=news-sensemaking)
* Make a free account
### Authentication
* Install the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) 
* Open terminal and initialize gcloud:
```console
gcloud init
```
* When prompted to pick cloud project select `news-sensemaking`
### Running the Code
* You'll need the Python libraries
```console
pip install gcloud
pip install google-cloud-language
```
