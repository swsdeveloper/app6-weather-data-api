from flask import Flask, render_template
import pandas as pd

# Create Flask website instance
app = Flask(__name__)


# Create Home page and grab tutorial.html
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/api/v1/<station>/<date>")
def about(station, date):
    # One way to convert station to a 6 byte string with leading zeros:
    # str(station).zfill(6)
    #
    # Here's another way using an f-string:
    filename = "data_small/TG_STAID" + f"{station:0>6}" + ".txt"
    df = pd.read_csv(filename, skiprows=20, parse_dates=["    DATE"])

    # get temp on specified date
    df_row = df.loc[df['    DATE'] == date]
    temperature = df_row['   TG'].squeeze() / 10  # celsius
    fahrenheit = temperature * (9/5) + 32

    result_dictionary = {"station": station, "date": date, "temperature": fahrenheit}
    return result_dictionary


if __name__ == "__main__":
    app.run(debug=True, port=5000)  # port 5000 is the default
