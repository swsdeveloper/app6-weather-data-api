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


# Create Home page and grab tutorial.html
@app.route("/")
def home():
    return render_template("home.html", data=html_stations)


@app.route("/api/v1/<station>/<date>")
def about(station, date):
    # One way to convert station to a 6 byte string with leading zeros:
    # str(station).zfill(6)
    #
    # Here's another way using an f-string:
    txt_filename = "data_small/TG_STAID" + f"{station:0>6}" + ".txt"
    df = pd.read_csv(txt_filename, skiprows=20, parse_dates=["    DATE"])

    # get temp on specified date
    df_row = df.loc[df['    DATE'] == date]
    temperature = df_row['   TG'].squeeze() / 10  # celsius
    fahrenheit = temperature * (9/5) + 32

    result_dictionary = {"station": station, "date": date, "temperature": fahrenheit}
    return result_dictionary


if __name__ == "__main__":
    app.run(debug=True, port=port)  # port 5000 is the default
