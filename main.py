from flask import Flask, render_template
import pandas as pd

# Create Flask website instance
app = Flask(__name__)

port = 5002

filename = "data_small/stations.txt"
stations = pd.read_csv(filename, skiprows=17)

stations = stations[['STAID', 'STANAME                                 ']]  # Station ID and Station Name
# stations['URL'] = f"http://127.0.0.1:{port}/api/v1/{stations['STAID']}/1889-01-01"

html_stations = stations.to_html()


def get_station_data(station_id: str, convert_dates=True):
    """
    Read CSV file of specified weather station to retrieve weather history.

    :param station_id: id number of weather station
    :param convert_dates: If True, convert Dates from Ints to Date objects (default)
                          If False, leave Dates in Int format
    :return: df: a Pandas DataFrame -- if station file exists
             df: a string containing an error message -- if station file not found
    """
    station_filename = "data_small/TG_STAID" + f"{station_id:0>6}" + ".txt"
    try:
        if convert_dates:
            df = pd.read_csv(station_filename, skiprows=20, parse_dates=["    DATE"])
        else:
            df = pd.read_csv(station_filename, skiprows=20)
    except FileNotFoundError:
        df = f"*** Station ID (STAID) '{station_id}' Not Found ***"
    return df


# Create Home page and grab tutorial.html
@app.route("/")
def home():
    """Display this website's home page"""
    return render_template("home.html", port=port, data=html_stations)


@app.route("/api/v1/<station>/<date>")
def about(station: str, date: str):
    """
    Get specified station's temperature for a specified date in the past.

    :param station: Station ID (aka STAID)
    :param date: YYYY-MM-DD
    :return: if found: dictionary containing 3 keys:
                date: yyyy-mm-dd (str)
                station: integer (in str format)
                temperature: in Fahrenheit (float)
             if not found: string containing an error message
    """
    if len(date) != 10:  # yyyy-mm-dd
        result = f"*** Invalid date '{date}' - enter as YYYY-MM-DD ***"
        return result

    df = get_station_data(station)  # Return a Pandas DataFrame or an error message string
    if type(df) is str:
        result = df  # Error message returned from get_station_data()
        return result

    # Get temp on specified date
    df_row = df.loc[df['    DATE'] == date]  # This is a Pandas Series
    if len(df_row) == 0:
        result = f"*** Station '{station}' has no records for this date: {date} ***"
        return result

    temperature = df_row['   TG'].squeeze() / 10  # celsius
    fahrenheit = temperature * (9/5) + 32
    result = {"station": station, "date": date, "temperature": fahrenheit}
    return result


@app.route("/api/v1/<station>")
def all_data(station: str):
    """
    Get specified station's temperature for all (recorded) dates in the past.

    :param station: Station ID (aka STAID)
    :return: if found, list of dictionaries, one per date, each containing 5 keys:
                DATE: in this format: "Thu, 01 Jan 1874 00:00:00 GMT" (str)
                TG: temperature in Celsius with 1 implied decimal place (eg: -147 = -14.7 Celsius) (signed int)
                Q_TG: quality of data: 0=valid, 1=suspect, 9=missing (int)
                SOUID: source identifier (int)
                STAID: station ID (int)
             if station not found: string containing an error message
    """
    df = get_station_data(station)  # Return a Pandas DataFrame or an error message string
    if type(df) is str:
        result = df  # Error message returned from get_station_data()
        return result

    # The next line returns dict organized by ROW (index 0 data, index 1 data, etc.):
    result = df.to_dict(orient="records")  # returns a list of dictionaries
    return result


@app.route("/api/v1/yearly/<station>/<year>")
def one_year(station: str, year: str):
    """
    Get specified station's temperature for one specific year in the past.

    :param station: Station ID (aka STAID)
    :param year: YYYY
    :return: if found, list of dictionaries, one per date, each containing 5 keys:
                DATE: yyyymmdd (str)
                TG: temperature in Celsius with 1 implied decimal place (eg: -147 = -14.7 Celsius) (signed int)
                Q_TG: quality of data: 0=valid, 1=suspect, 9=missing (int)
                SOUID: source identifier (int)
                STAID: station ID (int)
             if not found: string containing an error message
    """
    if len(year) != 4:
        result = f"*** Invalid year '{year}' - enter as YYYY ***"
        return result

    df = get_station_data(station, convert_dates=False)  # Return a Pandas DataFrame or an error message string
    if type(df) is str:
        result = df  # Error message returned from get_station_data()
        return result

    # Convert date from Integer to String:
    df['    DATE'] = df['    DATE'].astype(str)

    df = df.loc[df['    DATE'].str.startswith(year)]  # Result is a Pandas DataFrame
    if len(df) == 0:
        result = f"*** Station '{station}' has no records for year: {year} ***"
        return result

    result = df.to_dict(orient="records")  # returns a list of dictionaries
    return result


@app.route("/api/v1/monthly/<station>/<year_month>")
def one_month(station, year_month):
    """
    Get specified station's temperature for one specific month in the past.

    :param station: Station ID (aka STAID)
    :param year_month: YYYY-MM
    :return: if found, list of dictionaries, one per date, each containing 5 keys:
                DATE: yyyymmdd (str)
                TG: temperature in Celsius with 1 implied decimal place (eg: -147 = -14.7 Celsius) (signed int)
                Q_TG: quality of data: 0=valid, 1=suspect, 9=missing (int)
                SOUID: source identifier (int)
                STAID: station ID (int)
             if not found: string containing an error message
    """
    if len(year_month) != 7:  # yyyy-mm
        result = f"*** Invalid date '{year_month}' - enter as YYYY-MM ***"
        return result

    year = year_month[:4]
    month = year_month[5:]
    yearmonth = year + month  # yyyymm

    df = get_station_data(station, convert_dates=False)  # Return a Pandas DataFrame or an error message string
    if type(df) is str:
        result = df  # Error message returned from get_station_data()
        return result

    # Convert date from Integer to String:
    df['    DATE'] = df['    DATE'].astype(str)

    df = df.loc[df['    DATE'].str.startswith(yearmonth)]  # Result is a Pandas DataFrame
    if len(df) == 0:
        result = f"*** Station '{station}' has no records for month: {month} of year: {year} ***"
        return result

    result = df.to_dict(orient="records")  # returns a list of dictionaries
    return result


if __name__ == "__main__":
    app.run(debug=True, port=port)  # port 5000 is the default
