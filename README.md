# StreamingCommunityDownloader

Downloader per StreamingCommunityDownloader.to

- Installa Python3
- Installa le dipendenze presenti in requerements.txt
### Create virtualenv
1) Create virtualenv `python3 -m virtualenv venv`. This will create a venv folder with (almost) no package installed.
2) Enable virtualenv (see next paragraph)
3) Upgrade pip `pip install -U pip`
4) Install requirements `pip install -r requirements.txt`

## Work with virtualenv
#### Enable
You can enable the repo virtualenv with `source venv/bin/activate`, you'll notice a (venv) has appeared in your terminal.
By doing this you load all the requirements to run the python code.

#### Disable
To disable the virtualenv simply type `disable` in the terminal

## Run
`python main.py`