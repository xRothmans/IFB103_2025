from flask import Blueprint, request, jsonify
from markupsafe import Markup
import openai
import pandas as pd
import os
from datetime import datetime

# API Key
client = openai.Client(api_key="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")

analyse_bp = Blueprint('analyse', __name__)


# Pull data from CSV and create list for chart
@analyse_bp.route('/get-data')
def get_data():
    start_str = request.args.get("start_date")
    end_str = request.args.get("end_date")

    try:
        start_date = datetime.fromisoformat(start_str)
        end_date = datetime.fromisoformat(end_str)
    except Exception as e:
        return jsonify({"error": f"Invalid date format: {str(e)}"}), 400

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, 'sensor_readings.csv')

    df = pd.read_csv(data_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp'])
    filtered_df = df[(df['timestamp'] >= start_date) & (df['timestamp'] < end_date)]

    data = {
        "timestamps": filtered_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
        "temperature": filtered_df['temp_c'].tolist(),
        "humidity": filtered_df['humidity'].tolist()
    }

    return jsonify(data)


# Take data from CSV and analyse it
@analyse_bp.route('/analyse-data')
def analyse_data():
    start_str = request.args.get("start_date")
    end_str = request.args.get("end_date")

    try:
        start_date = datetime.fromisoformat(start_str)
        end_date = datetime.fromisoformat(end_str)
    except Exception as e:
        return f"Invalid date format: {str(e)}"

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, 'sensor_readings.csv')

    df = pd.read_csv(data_path)
    if not all(col in df.columns for col in ['temp_c', 'humidity', 'timestamp']):
        return "Missing expected columns in CSV."

    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp'])
    filtered_df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]

    if filtered_df.empty:
        return "No data found in the selected date range."

    temp_stats = filtered_df['temp_c'].describe().round(2).to_dict()
    humidity_stats = filtered_df['humidity'].describe().round(2).to_dict()

    prompt = f"""
    You are a weather analyst. Analyze the following sensor data summary for the date range {start_str} to {end_str}:

    **Temperature (°C) Stats:**
    - Mean: {temp_stats['mean']}
    - Min: {temp_stats['min']}
    - Max: {temp_stats['max']}
    - Std Dev: {temp_stats['std']}

    **Humidity (%) Stats:**
    - Mean: {humidity_stats['mean']}
    - Min: {humidity_stats['min']}
    - Max: {humidity_stats['max']}
    - Std Dev: {humidity_stats['std']}

    Write a short report describing trends and patterns in temperature and humidity for the given range. Format this report for HTML, 
    with correct spacing and gaps between paragraphs, weight for headings and length of sentences.
    Include any anomalies or interesting observations you find. Use the data provided to support your analysis.
    Be concise and clear in your writing. Use bullet points.
    Make sure the report begins with "Weather Analysis Report:\n{start_str}\n{end_str}\n", and format the dates to be DD/MM/YYYY HH:MM.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=750
        )
        results = response.choices[0].message.content
        return Markup(results)
    except Exception as e:
        return f"Error during analysis: {str(e)}"
