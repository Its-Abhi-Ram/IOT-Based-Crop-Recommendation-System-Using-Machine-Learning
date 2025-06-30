# # -*- coding: utf-8 -*-
# #import libraries
# import numpy as np
# import requests , json
# from flask import Flask, render_template,request
# import http.client
# import pickle#Initialize the flask App
# app = Flask(__name__)
# model = pickle.load(open('model.pkl', 'rb'))


# #default page of our web-app
# @app.route('/')
# def home():
#     return render_template('./index.html')


# @app.route('/form')
# def form():
#     return render_template('./form.html')

# #To use the predict button in our web-app
# @app.route('/predict',methods=['POST'])
# def predict():
#     #For rendering results on HTML GUI
#     int_features = [float(x) for x in request.form.values()]
#     final_features = [np.array(int_features)]
#     # print(final_features)
#     prediction = model.predict(final_features)
#     output = prediction 
#     return render_template('./result.html', prediction_text=f'{output[0].capitalize()}')



# @app.route('/weather', methods= ['POST', 'GET'])
# def weather():
#     print(request.method)
#     if request.method == "POST":
#         location = request.form.get("place")
#         print(location)
#         api_key ='03b1acbfd0387ac994dad57eb102fe01'
        
#         link = "https://api.openweathermap.org/data/2.5/weather?q="+location+"&appid="+api_key
#         api_link = requests.get(link)
#         data = api_link.json()
#         # print(data)
#         temp= round((data['main']['temp'])-273.15,2)
#         humidity=data['main']['humidity']
#         pressure1=data['main']['pressure']
#         # weather_desc = data['weather'][0]['description'].capitalize()
#         wind_speed = data['wind']['speed']
#         place =data['name']
#         visible=data['visibility']
#         latitude=data['coord']['lat']
#         longitude=data['coord']['lon']
#         # return render_template('./weather.html', info=data,tempr=temp,desc=weather_desc,speed=wind_speed,humid=humidity,pressure=pressure1,placeo=place)
#     else:
#         api_key ='03b1acbfd0387ac994dad57eb102fe01'
#         location = 'Kolar'
#         link = "https://api.openweathermap.org/data/2.5/weather?q="+location+"&appid="+api_key
#         api_link = requests.get(link)
#         data = api_link.json()
#             # print(data)
#         temp= round((data['main']['temp'])-273.15,2)
#         humidity=data['main']['humidity']
#         pressure1=data['main']['pressure']
#         # weather_desc = data['weather'][0]['description'].capitalize()
#         wind_speed = data['wind']['speed']
#         place =data['name']
#         visible=data['visibility']
#         latitude=data['coord']['lat']
#         longitude=data['coord']['lon']
#     return render_template('./weather.html', info=data,tempr=temp,speed=wind_speed,humid=humidity,pressure=pressure1,placeo=place,visible=visible,latitude=latitude,longitude=longitude)
# if __name__ == "__main__":
#     app.run(debug=True)






# -*- coding: utf-8 -*-
import numpy as np
import requests
from flask import Flask, render_template, request
import pickle
from warnings import filterwarnings
filterwarnings('ignore')

# Initialize the Flask app
app = Flask(__name__)

# Load the pre-trained model
model = pickle.load(open('model_edited.pkl', 'rb'))



@app.route('/')
def home():
    return render_template('./index.html')


# Default route - IoT ML Prediction
@app.route('/iot')
def iot():
    try:
        # Fetch data from the IoT ThingSpeak API
        data = requests.get("https://api.thingspeak.com/channels/2900389/feeds.json?api_key=0QLB3KNKJI62Q9E8&results=2")
        data = data.json()  # Parse JSON response

        # Extract sensor values from the API response
        n = float(data['feeds'][-1]['field4'])
        p = float(data['feeds'][-1]['field5'])
        k = float(data['feeds'][-1]['field6'])
        temp = float(data['feeds'][-1]['field2'])
        hum = float(data['feeds'][-1]['field3'])
        ph = float(data['feeds'][-1]['field7'])

        # Generate predictions based on the fetched data
        prediction = model.predict([[n, p, k, temp, hum, ph]])[0]

        # Render the IoT ML HTML template with the fetched/predicted data
        return render_template(
            'iot.html',
            prediction_text=f'{prediction.capitalize()}',
            N=n,
            P=p,
            K=k,
            Temp=temp,
            Humid=hum,
            pH=ph
        )
    except Exception as e:
        # Handle errors gracefully
        return f"Error fetching data or generating prediction: {e}"

# Route to display the form for manual predictions
@app.route('/form')
def form():
    return render_template('./form.html')

# Route to handle predictions via form input
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Fetch input features from the form
        int_features = [float(x) for x in request.form.values()]
        final_features = [np.array(int_features)]

        # Generate prediction based on input features
        prediction = model.predict(final_features)
        output = prediction[0]

        # Render the result HTML page with the prediction
        return render_template('./result.html', prediction_text=f'{output.capitalize()}')
    except Exception as e:
        return f"Error predicting the result: {e}"

# Weather API integration route
@app.route('/weather', methods=['POST', 'GET'])
def weather():
    try:
        if request.method == "POST":
            location = request.form.get("place")
        else:
            location = 'Kolar'  # Default location if none is provided

        # Fetch weather data from the OpenWeatherMap API
        api_key = '03b1acbfd0387ac994dad57eb102fe01'
        link = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
        api_link = requests.get(link)
        data = api_link.json()

        # Extract and process weather details
        temp = round((data['main']['temp']) - 273.15, 2)
        humidity = data['main']['humidity']
        pressure = data['main']['pressure']
        wind_speed = data['wind']['speed']
        place = data['name']
        visibility = data['visibility']
        latitude = data['coord']['lat']
        longitude = data['coord']['lon']

        # Render the weather HTML template with the fetched data
        return render_template(
            './weather.html',
            tempr=temp,
            speed=wind_speed,
            humid=humidity,
            pressure=pressure,
            placeo=place,
            visible=visibility,
            latitude=latitude,
            longitude=longitude
        )
    except Exception as e:
        return f"Error fetching weather data: {e}"

if __name__ == "__main__":
    # Run the Flask app in debug mode
    app.run(debug=True)
