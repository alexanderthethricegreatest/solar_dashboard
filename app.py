from flask import Flask, render_template, request
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

def get_sheet_data(sheet_name="Solar WV News"):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("gsheet_creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

@app.route("/", methods=["GET"])
def index():
    df = get_sheet_data()

    tag = request.args.get("tag")
    source = request.args.get("source")
    date = request.args.get("date")

    if tag:
        df = df[df["Tags"].str.contains(tag, case=False, na=False)]
    if source:
        df = df[df["Source"].str.contains(source, case=False, na=False)]
    if date:
        df = df[df["Published At"].str.startswith(date)]

    tag_series = df["Tags"].dropna().str.split("; ").explode()
    tag_counts = tag_series.value_counts().to_dict()
    sentiment_counts = df["Sentiment"].value_counts().to_dict()

    data = df.to_dict(orient="records")
    columns = df.columns.tolist()

    return render_template("index.html",
        data=data,
        columns=columns,
        tag=tag,
        source=source,
        date=date,
        tag_counts=tag_counts,
        sentiment_counts=sentiment_counts,
        all_sources=sorted(df["Source"].dropna().unique()),
        all_dates=sorted(df["Published At"].dropna().str[:10].unique(), reverse=True)
    )

if __name__ == "__main__":
    app.run(debug=True)
