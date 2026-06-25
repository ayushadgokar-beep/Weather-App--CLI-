# Weather App (CLI)

## CodTech Internship Task

**Intern ID: CITS2549

## Project Description

Weather App (CLI) is a Python-based command-line application that allows users to check the current weather of any city. The application retrieves real-time weather information using the OpenWeatherMap API and displays details such as temperature, weather condition, humidity, wind speed, and feels-like temperature. It also handles invalid city names and network errors gracefully, making it a simple yet practical project for learning API integration in Python.

## Technologies Used

* Python
* Requests
* OpenWeatherMap API
* JSON

## Features

* Search weather by city name
* Display current temperature
* Show weather condition
* Display humidity
* Show wind speed
* Display feels-like temperature
* Handle invalid city names
* Handle internet connection errors
* Search multiple cities until the user exits

## How to Run

1. Make sure Python 3 is installed.

2. Install the required library:

   ```bash
   pip install -r requirements.txt
   ```

3. Get a free API key from OpenWeatherMap and add it to the `config.py` file.

4. Run the application:

   ```bash
   python weather.py
   ```

## Project Structure

```text
Weather_App/
│
├── weather.py
├── config.py
├── requirements.txt
└── README.md
```


