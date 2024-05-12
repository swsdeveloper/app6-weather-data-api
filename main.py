from flask import Flask, render_template

# Create Flask website instance
app = Flask(__name__)


# Create Home page and grab tutorial.html
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/api/v1/<station>/<date>")
def about(station, date):
    # df = pandas.csv("")
    # temperature = df.station(date)
    temperature = 23
    return {"station": station, "date": date, "temperature": temperature}


if __name__ == "__main__":
    app.run(debug=True)
