import requests
import wikipedia
import pywhatkit as kit
from email.message import EmailMessage
import smtplib
from decouple import config

EMAIL = config('EMAIL', default='')
PASSWORD = config('PASSWORD', default='')
NEWS_API_KEY = config('NEWS_API_KEY', default='')
WEATHER_API_KEY = config('WEATHER_API_KEY', default='')


def find_my_ip():
    try:
        ip_address = requests.get('https://api.ipify.org?format=json').json()
        return ip_address["ip"]
    except Exception as e:
        print(f"Error getting IP: {e}")
        return "Unable to get IP address"


def search_on_wikipedia(query):
    try:
        results = wikipedia.summary(query, sentences=2)
        return results
    except Exception as e:
        print(f"Wikipedia error: {e}")
        return "Sorry, I couldn't find information on Wikipedia"


def search_on_google(query):
    try:
        kit.search(query)
    except Exception as e:
        print(f"Google search error: {e}")


def youtube(video):
    try:
        kit.playonyt(video)
    except Exception as e:
        print(f"YouTube error: {e}")


def send_email(receiver_add, subject, message):
    if not EMAIL or not PASSWORD:
        print("Email not configured. Please add EMAIL and PASSWORD to .env file")
        return False

    try:
        email = EmailMessage()
        email['To'] = receiver_add
        email['Subject'] = subject
        email['From'] = EMAIL

        email.set_content(message)
        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()
        s.login(EMAIL, PASSWORD)
        s.send_message(email)
        s.close()
        return True

    except Exception as e:
        print(f"Email error: {e}")
        return False


def get_news():
    try:
        if not NEWS_API_KEY:
            return ["News API key not configured"]

        news_headlines = []
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
        result = requests.get(url).json()

        if "articles" not in result:
            return ["Unable to fetch news - API error"]

        articles = result["articles"]
        for article in articles:
            news_headlines.append(article["title"])
        return news_headlines[:6]
    except Exception as e:
        print(f"News error: {e}")
        return ["Unable to fetch news"]


def weather_forecast(city):
    try:
        # First get coordinates for the city
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={WEATHER_API_KEY}"
        geo_response = requests.get(geo_url).json()

        if not geo_response:
            return "City not found", "N/A", "N/A"

        lat = geo_response[0]["lat"]
        lon = geo_response[0]["lon"]

        # Get weather data
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
        res = requests.get(weather_url).json()

        weather = res["weather"][0]["main"]
        temp = res["main"]["temp"]
        feels_like = res["main"]["feels_like"]

        return weather, f"{temp}°C", f"{feels_like}°C"
    except Exception as e:
        print(f"Weather error: {e}")
        return "Unable to get weather", "N/A", "N/A"