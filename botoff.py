import gspread
import psycopg2
from oauth2client.service_account import ServiceAccountCredentials
from dateutil.rrule import rrule, DAILY, MO, TU, WE, TH, FR
from datetime import date, datetime, timedelta
import calendar
import sys
import configparser

# Les query SQL
GET_USERS = """
  select id, first_name, last_name from users
  where business_unit_id = 1
  order by id
"""

GET_OFF_REPORTS = """
  select date, percentage_of_day from time_reports
  where activity_id =  1     and
        user_id     =  {0}   and
        date        >= '{1}' and
        date        <  '{2}'
"""

def work_day_offset(month):
    year = datetime.now().year

    first_day_of_year = date(year, 1, 1)
    first_day_of_month = date(year, month, 1)

    current_workdays = rrule(
        DAILY,
        dtstart=first_day_of_year,
        until=first_day_of_month,
        byweekday=(MO, TU, WE, TH, FR)
    )

    return current_workdays.count() + 1


def open_drivesheet(config):
    # Lecture de la clef d'API google
    key_file = config.get("google", "secret")
    scope = [config.get("google", "scope")]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        key_file, scope
    )
    client = gspread.authorize(creds)

    # On ouvre la feuille des objectifs
    name = config.get("google", "sheetname")
    tab = config.get("google", "sheettab")
    return client.open(name).worksheet(tab)


def readconf():
    config = configparser.RawConfigParser()
    config.read("config.cfg")
    return config


def connect_to_db(config):
    # Connexion à la BDD planbot
    dbid = "dbname='{0}' user='{1}' host='{2}' password='{3}'".format(
        config.get("bdd", "dbname"),
        config.get("bdd", "user"),
        config.get("bdd", "host"),
        config.get("bdd", "p")
    )

    try:
        conn = psycopg2.connect(dbid)
    except:
        print("I am unable to connect to the database")

    return conn.cursor()


# Main
config = readconf()

day_offset = 0
day_interval_lower = 0
day_interval_upper = 0
objectifs_drivesheet = None
cursor = None

month = datetime.now().month
try:
    monthparam = int(sys.argv[1])
    month = monthparam
except:
    pass

# To work on a specific month, we need to set the row offset
# according to the number of work day since de begining of the
# year until the current month
day_offset = work_day_offset(month)

# date filter to match current month in SQL query
day_interval_lower = date(datetime.now().year, month, 1)
day_interval_upper = date(datetime.now().year, month+1, 1)

# Opening spreadsheet with credentials and google API
objectifs_drivesheet = open_drivesheet(config)

# Connecting to planbot database
cursor = connect_to_db(config)

# Fetch all embeded users
cursor.execute(GET_USERS)
embeded_users = cursor.fetchall()

header_row = config.getint("google", "first_cell_row")
row = header_row + 1
col = config.getint("google", "first_cell_col")

for mate in embeded_users:
    # Update user name in spreadsheet header
    formated_user_name = mate[1] + " " + mate[2]
    print (formated_user_name)
    objectifs_drivesheet.update_cell(
        header_row,
        col,
        formated_user_name
    )

    # fetch user off-project time reports
    cursor.execute(
        GET_OFF_REPORTS.format(
            mate[0],
            day_interval_lower,
            day_interval_upper
        )
    )
    off_reports = cursor.fetchall()

    # Mark off-reports in user column
    for entry in off_reports:
        day = entry[0].day
        percentage = entry[1]
        print("\t{0} : {1}".format(entry[0], percentage))

        # target row is
        #   - below header
        #   - below previous months days
        #   - indexed by current month day
        day_row = header_row + day_offset + day

        objectifs_drivesheet.update_cell(day_row, col, percentage)

    # Next user, next column
    col = col + 1
