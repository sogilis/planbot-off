# Planbot-off readme

## Goal

Planbot-off is a nasty manager tool to report all off-project time
reports from every employee into a Google Drive spreadsheet. This way,
we can visualize who is doing nothing, since reporting off-project
time means slacking off, right ?

basically, it :
- Connects to the Planbot database
- Fetch all embeded team registered users
- Fetch all off-project reports from them for the requested month
- Connect to the Google Drive API
- Feed the spreadsheet with the bad reports with the incriminated
  names in bold

## Technolojeez

- Python
- psycopg2
- gspread
- configparser

## Database

In the configuration file, replace the following fields with the
authentication information from Basecamp.

		[bdd]
		host           = <database amazon host>
		user           = <READONLY database user>
		dbname         = <database name>
		p              = <READONLY database user password>

## Google API

Given you have write access to your Google Spreadsheet and have a
Google managed account, follow these steps :

1. Go to the
   [Google API console](https://console.developers.google.com/)
2. Look for the "planbot-off" project
3. Click on "Identifiants" in the side menu
4. Click on "Créer des identifiants", select "Clé de compte de service"
   1. Select "Nouveau compte de service"
   2. Choose a name, then select the "Rôle" as "Project" > "Éditeur"
   3. Select the key type "JSON"
5. Save the file the to directory of the cloned project
6. In the config file, fill the google information :

        [google]
		secret         = <your_new_JSON_key_file.json>
		scope          = https://spreadsheets.google.com/feeds
		sheetname      = <The name of your Spreadsheet>
		sheettab       = <The name of the tab>
		first_cell_row = <The row number where to start inserting>
		first_cell_col = <The col nombre where to start inserting>

## Usage

Just enter :

    $ python botoff.py [target month]

By default, it fetches the current month.

## Python3 fuckery

    $ virtualenv -p /usr/bin/python3 py3env
    $ source py3env/bin/activate

    $ python botoff.py [target month]

    $ deactivate
