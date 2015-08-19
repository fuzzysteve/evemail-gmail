# evemail-gmail
Evemail to gmail uploader.



Requirements:
    python 2.7

    pip install evelink

    pip install google-api-python-client


API key with mail, mail body, and mailing list. That's a mask of 3584


Set up project with credentials with access to the gmail api at:

https://console.developers.google.com/

Download the credential file, and save it as client_secret.json in the directory with the rest of the files. (do not commit it to a copy)

once you have python downloaded, and the modules installed with pip (which may not be in your path. c:\python27\scripts\pip is a common location)

* download the files from here, and stick them in a directory somewhere
* make sure you put the client_secret.json in with them
* fill the details into the conf file
* start a command prompt (if you hold shift and right click in the directory, you should get an option to start a command prompt there)
* python uploader.py
* The first time it runs, it'll open a browser and get you to select the account and accept the privileges for insertion. After that, it'll run on cached credentials
* Then it should start inserting mail into your gmail account, under the eve label.

This will upload everything the API hands it the first time, then on each subsequent run, it'll only update new mail into there.
