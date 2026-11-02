
import streamlit as st
import requests
from openai import OpenAI
from datetime import datetime
from zoneinfo import ZoneInfo

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="🤖",
    layout="centered"
)

# ---------------- OPENROUTER ----------------

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

# ---------------- DATE AND TIME ----------------

def get_datetime():
    now = datetime.now(ZoneInfo("Asia/Kolkata"))

    return (
        f"Date: {now.strftime('%d %B %Y')}\n"
        f"Day: {now.strftime('%A')}\n"
        f"Time: {now.strftime('%I:%M:%S %p')}\n"
        f"Timezone: India Standard Time"
    )

# ---------------- WEATHER ----------------

def get_weather(city):

    try:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"

        geo = requests.get(
            geo_url,
            params={"name": city, "count": 1},
            timeout=10
        ).json()

        if not geo.get("results"):
            return "City not found. Please check the city name."

        place = geo["results"][0]

        weather_url = "https://api.open-meteo.com/v1/forecast"

        weather = requests.get(
            weather_url,
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
                "timezone": "Asia/Kolkata"
            },
            timeout=10
        ).json()

        current = weather["current"]

        return f"""
Weather in {place['name']}, {place.get('country', '')}

Temperature: {current['temperature_2m']}°C
Feels Like: {current['apparent_temperature']}°C
Humidity: {current['relative_humidity_2m']}%
Wind Speed: {current['wind_speed_10m']} km/h
Weather Code: {current['weather_code']}
"""

    except Exception:
        return "Weather service is temporarily unavailable."


# ---------------- SESSION STATE ----------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.title("🤖 AI Assistant")

    st.write("Your personal learning companion.")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.subheader("Features")
    st.write("📚 All Subject Study Help")
    st.write("💻 Coding Assistance")
    st.write("🕒 Date & Time")
    st.write("🌤️ Live Weather")
    st.write("💬 Chat History")

# ---------------- MAIN UI ----------------

st.title("🤖 AI Study Assistant")

st.caption("Ask anything. Learn everything.")

# Display old messages

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------- USER INPUT ----------------

if prompt := st.chat_input("Ask me anything..."):

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        try:

            question = prompt.lower().strip()

            # Date and time questions

            time_words = [
                "time", "date", "today",
                "current time", "current date",
                "what day", "aaj"
            ]

            if any(word in question for word in time_words):

                reply = get_datetime()

            # Weather questions

            elif "weather" in question or "mausam" in question:

                city = prompt.lower()

                for word in ["weather", "mausam", "in", "of", "ka", "ki"]:
                    city = city.replace(word, "")

                city = city.strip()

                if city:
                    reply = get_weather(city)
                else:
                    reply = "Please mention a city name."

            # AI study assistant

            else:

                messages = [
                    {
                        "role": "system",
                        "content": f"""
You are an intelligent AI Study Assistant.

Current date and time:
{get_datetime()}

Rules:
1. Answer questions from all academic subjects.
2. Support Python, Java, C, DBMS, SQL,
   Computer Science, Maths, Science, History,
   English and other subjects.
3. Explain concepts in simple language.
4. Use Hinglish if the user asks in Hinglish.
5. Give definitions, examples and bullet points.
6. Provide complete working code when coding is requested.
7. Give accurate and useful educational answers.
8. Do not invent information.
9. Keep answers clear and well structured.
"""
                    }
                ]

                # Add conversation history

                for msg in st.session_state.messages[-12:]:

                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })

                response = client.chat.completions.create(
                    model="openrouter/free",
                    messages=messages
                )

                reply = (
                    response.choices[0].message.content
                    or "No response received."
                )

            st.markdown(reply)

            st.session_state.messages.append({
                "role": "assistant",
                "content": reply
            })

        except Exception as e:

            st.error(f"Something went wrong: {e}")
# python -m streamlit run app.py