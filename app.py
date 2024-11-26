import os
import requests

from pprint import PrettyPrinter
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
from geopy.geocoders import Nominatim


################################################################################
## SETUP
################################################################################

app = Flask(__name__)

# Get the API key from the '.env' file
load_dotenv()

pp = PrettyPrinter(indent=4)

API_KEY = os.getenv('API_KEY')
API_URL = 'http://api.openweathermap.org/data/2.5/weather'


################################################################################
## ROUTES
################################################################################

@app.route('/')
def home():
    """Displays the homepage with forms for current or historical data."""
    context = {
        'min_date': (datetime.now() - timedelta(days=5)),
        'max_date': datetime.now()
    }
    return render_template('home.html', **context)

def get_letter_for_units(units):
    """Returns a shorthand letter for the given units."""
    return 'F' if units == 'imperial' else 'C' if units == 'metric' else 'K'

@app.route('/results')
def results():
    """Displays results for current weather conditions."""
    city = request.args.get('city')
    units = request.args.get('units')

    params = {
        'appid': API_KEY,
        'q': city,
        'units': units
    }

    result_json = requests.get(API_URL, params=params).json()

    pp.pprint(result_json)

    context = {
        'date': datetime.now().strftime('%m-%d-%Y'),
        'city': result_json['name'],
        'description': result_json['weather'][0]['description'],
        'temp': result_json['main']['temp'],
        'humidity': result_json['main']['humidity'],
        'wind_speed': result_json['wind']['speed'],
        'sunrise': datetime.fromtimestamp(result_json['sys']['sunrise']),
        'sunset': datetime.fromtimestamp(result_json['sys']['sunset']),
        'units_letter': get_letter_for_units(units)
    }

    return render_template('results.html', **context)


@app.route('/comparison_results')
def comparison_results():
    """Displays the relative weather for 2 different cities."""
    city1 = request.args.get('city1')
    city2 = request.args.get('city2')
    units = request.args.get('units')


    def get_weather_data(city, units):
        params = {
            'appid': API_KEY,
            'q': city,
            'units': units
        }
        response = requests.get(API_URL, params=params)
        return response.json()

    city1_json = get_weather_data(city1, units)
    city2_json = get_weather_data(city2, units)

    city1_info = {
        'city': city1_json['name'],
        'description': city1_json['weather'][0]['description'],
        'temp': round(city1_json['main']['temp'], 2),
        'humidity': city1_json['main']['humidity'],
        'wind_speed': city1_json['wind']['speed'],
        'sunrise': datetime.fromtimestamp(city1_json['sys']['sunrise']),
        'sunset': datetime.fromtimestamp(city1_json['sys']['sunset']),
        'units_letter': get_letter_for_units(units)
    }

    city2_info = {
        'city': city2_json['name'],
        'description': city2_json['weather'][0]['description'],
        'temp': round(city2_json['main']['temp'], 2),
        'humidity': city2_json['main']['humidity'],
        'wind_speed': city2_json['wind']['speed'],
        'sunrise': datetime.fromtimestamp(city2_json['sys']['sunrise']),
        'sunset': datetime.fromtimestamp(city2_json['sys']['sunset']),
        'units_letter': get_letter_for_units(units)
    }
    
    context = {
        'date': datetime.now().strftime('%m-%d-%Y'),
        'city1': city1_info,
        'city2': city2_info,
        'temp_dif': round(city1_info['temp'] - city2_info['temp'])
    }


    return render_template('comparison_results.html', **context)


if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)