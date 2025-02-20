import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# Load dataset
df = pd.read_csv("generated_weather_data.csv")

# Convert date to datetime format
df['date'] = pd.to_datetime(df['date'])

# Feature selection
X = df[['high_temp', 'low_temp', 'humidity', 'rainfall']]

# Target Variables (Shifted 30 days forward for prediction)
df['future_high_temp'] = df['high_temp'].shift(-30)
df['future_low_temp'] = df['low_temp'].shift(-30)

# Drop NaN values caused by shifting
df.dropna(inplace=True)

# Ensure X and y are properly aligned
X = X.iloc[:-30]  # Remove last 30 rows from X to match y
y_high = df['future_high_temp']
y_low = df['future_low_temp']

# Train/Test split
X_train, X_test, y_high_train, y_high_test = train_test_split(X, y_high, test_size=0.2, random_state=42)
X_train, X_test, y_low_train, y_low_test = train_test_split(X, y_low, test_size=0.2, random_state=42)

# Train ML models
model_high = LinearRegression()
model_low = LinearRegression()

model_high.fit(X_train, y_high_train)
model_low.fit(X_train, y_low_train)

# Function to predict future weather based on trained model
def predict_weather(city, state, year, month):
    past_data = df[(df['city'].str.lower().str.strip() == city.lower().strip()) & 
                   (df['state'].str.lower().str.strip() == state.lower().strip())]

    if past_data.empty:
        print("No historical data found for this city.")
        return []

    predictions = []
    for i in range(1, 32):  # Predict for each day
        try:
            date = datetime(year, month, i)
            day_of_week = date.strftime("%A")

            predicted_high_temp = model_high.predict([[past_data['high_temp'].mean(),
                                                       past_data['low_temp'].mean(),
                                                       past_data['humidity'].mean(),
                                                       past_data['rainfall'].mean()]])[0]
            
            predicted_low_temp = model_low.predict([[past_data['high_temp'].mean(),
                                                     past_data['low_temp'].mean(),
                                                     past_data['humidity'].mean(),
                                                     past_data['rainfall'].mean()]])[0]
            
            predicted_humidity = past_data['humidity'].mean()
            predicted_rainfall = past_data['rainfall'].mean()
            rain_status = "Yes" if predicted_rainfall > 1 else "No"

            predictions.append({
                "date": date.strftime("%d-%b-%Y"),
                "day": day_of_week,
                "high_temp": round(predicted_high_temp, 1),
                "low_temp": round(predicted_low_temp, 1),
                "rainfall": f"{predicted_rainfall:.1f} cm" if rain_status == "Yes" else "No",
                "humidity": f"{predicted_humidity:.1f}%"
            })
        except ValueError:
            break  # Stop loop if month has fewer than 31 days

    return predictions

# Function to generate a monthly summary
def generate_month_summary(predictions):
    if not predictions:
        print("No data available for summary.")
        return {}

    total_days = len(predictions)
    avg_high_temp = float(np.mean([day["high_temp"] for day in predictions]))  # Convert np.float64 to float
    avg_low_temp = float(np.mean([day["low_temp"] for day in predictions]))    # Convert np.float64 to float
    avg_humidity = float(np.mean([float(day["humidity"].strip('%')) for day in predictions]))  # Convert to float
    total_rainy_days = sum([1 for day in predictions if "cm" in day["rainfall"]])

    # Determine overall weather condition
    if avg_high_temp > 35:
        overall_weather = "Very Hot"
    elif avg_low_temp < 0:
        overall_weather = "Very Cold"
    elif avg_high_temp > 20:
        overall_weather = "Hot"
    else:
        overall_weather = "Cold"

    summary = {
        "avg_high_temp": avg_high_temp,
        "avg_low_temp": avg_low_temp,
        "avg_humidity": avg_humidity,
        "rainy_days": total_rainy_days,
        "overall_weather": overall_weather
    }

    return summary

def main_predict(c,s,y,m):
    # User Input for Prediction
    city = c
    state = s
    year = y
    month = m

    # Run the Prediction
    forecast = predict_weather(city, state, year, month)
    month_summary = generate_month_summary(forecast)

    # Print Daily Forecast
    print("\nWeather Forecast:")
    for day in forecast:
        print(f"{day['date']} ({day['day']}): {day['high_temp']}°C - {day['low_temp']}°C, Rainfall: {day['rainfall']}, Humidity: {day['humidity']}")

    # Print Monthly Summary
    print("\nMonthly Summary:")
    print(month_summary)
    return month_summary

main_predict('Plano','TX',2027,5)