from flask import Flask, render_template, jsonify
import requests
from datetime import datetime

app = Flask(__name__)


def fetch_worldbank_data(indicator):
    url = f"https://api.worldbank.org/v2/country/all/indicator/{indicator}?format=json&date=2022&per_page=300"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data[1] if len(data) > 1 else []
    except Exception as e:
        print(f"Error fetching {indicator}: {str(e)}")
        return []


def process_population_data():
    raw_data = fetch_worldbank_data('SP.POP.TOTL')
    return {
        item['country']['id']: {
            'value': item['value'],
            'country_name': item['country']['value']
        }
        for item in raw_data if item['value'] is not None
    }

def process_wealth_data():
    raw_data = fetch_worldbank_data('NY.GDP.MKTP.CD')
    return {
        item['country']['id']: {
            'value': item['value'],
            'country_name': item['country']['value']
        }
        for item in raw_data if item['value'] is not None
    }


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/data')
def get_data():
    population = process_population_data()
    gdp = process_wealth_data()

    combined = {}
    for country_id in population:
        if country_id in gdp and population[country_id] and gdp[country_id]:
            # Get country name from population data (both sources should match)
            country_name = population[country_id]['country_name']
            combined[country_id] = {
                'population': population[country_id]['value'],
                'gdp': gdp[country_id]['value'],
                'gdp_per_capita': gdp[country_id]['value'] / population[country_id]['value'],
                'country_name': country_name
            }
    return jsonify(combined)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
