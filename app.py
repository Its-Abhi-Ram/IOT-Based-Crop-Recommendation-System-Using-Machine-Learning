# -*- coding: utf-8 -*-
import os
import numpy as np
import requests
from flask import Flask, render_template, request
from warnings import filterwarnings
from model import load_model

filterwarnings('ignore')

app = Flask(__name__)

# Load the trained ML model
model = load_model()


# -------------------------------------------------------
# HOME
# -------------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html')


# -------------------------------------------------------
# IOT PREDICTION
# -------------------------------------------------------
@app.route('/iot')
def iot():
    try:
        # Read IoT API key from environment variable
        thingspeak_api_key = os.environ.get("THINGSPEAK_KEY")

        if not thingspeak_api_key:
            return "Error: THINGSPEAK_KEY is not set in environment variables."

        url = f"https://api.thingspeak.com/channels/2900389/feeds.json?api_key={thingspeak_api_key}&results=2"
        data = requests.get(url).json()

        feed = data['feeds'][-1]

        n = float(feed['field4'])
        p = float(feed['field5'])
        k = float(feed['field6'])
        temp = float(feed['field2'])
        hum = float(feed['field3'])
        ph = float(feed['field7'])

        prediction = model.predict([[n, p, k, temp, hum, ph]])[0]

        return render_template(
            'iot.html',
            prediction_text=prediction.capitalize(),
            N=n, P=p, K=k, Temp=temp, Humid=hum, pH=ph
        )

    except Exception as e:
        return f"Error fetching IoT data: {e}"


# -------------------------------------------------------
# MANUAL FORM INPUT
# -------------------------------------------------------
@app.route('/form')
def form():
    return render_template('form.html')


@app.route('/predict', methods=['POST'])
def predict():
    try:
        values = [float(x) for x in request.form.values()]
        prediction = model.predict([values])[0]

        return render_template('result.html',
            prediction_text=prediction.capitalize()
        )

    except Exception as e:
        return f"Error predicting data: {e}"


# -------------------------------------------------------
# WEATHER API
# -------------------------------------------------------
@app.route('/weather', methods=['POST', 'GET'])
def weather():
    try:
        location = request.form.get("place") if request.method == "POST" else "Kolar"

        # Weather API key from environment variable
        api_key = os.environ.get("OPENWEATHER_KEY")

        if not api_key:
            return "Error: OPENWEATHER_KEY not set in environment variables."

        url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
        data = requests.get(url).json()

        temp = round(data['main']['temp'] - 273.15, 2)
        humidity = data['main']['humidity']
        pressure = data['main']['pressure']
        wind = data['wind']['speed']
        place = data['name']
        visibility = data['visibility']
        lat = data['coord']['lat']
        lon = data['coord']['lon']

        return render_template(
            'weather.html',
            tempr=temp, speed=wind, humid=humidity,
            pressure=pressure, placeo=place,
            visible=visibility, latitude=lat, longitude=lon
        )

    except Exception as e:
        return f"Error fetching weather: {e}"


# -------------------------------------------------------
# RENDER DEPLOYMENT PORT
# -------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
