import pandas as pd
import random
from datetime import datetime, timedelta

# Define cities and states
cities_tx = ["Houston", "San Antonio", "Dallas", "Austin", "Fort Worth", "El Paso", "Arlington", "Corpus Christi",
             "Plano", "Laredo", "Lubbock", "Garland", "Irving", "Amarillo", "Grand Prairie", "McKinney", "Frisco",
             "Brownsville", "Pasadena", "Killeen"] * 5

states_tx = ["TX"] * 100

# Merge lists
cities = cities_tx
states = states_tx

# Set date range
start_date = datetime(2021, 1, 1)
end_date = datetime(2024, 1, 1)

# Generate dataset
data = []
current_date = start_date

while current_date <= end_date:
    for city, state in zip(cities, states):
        high_temp = random.randint(-5, 40)
        low_temp = high_temp - random.randint(5, 15)
        humidity = random.randint(40, 100)
        rainfall = round(random.uniform(0, 5), 1) if random.random() > 0.7 else 0
        rain_status = "Yes" if rainfall > 0 else "No"

        data.append([city, state, current_date.strftime("%Y-%m-%d"), high_temp, low_temp, rain_status, rainfall, humidity])

    current_date += timedelta(days=1)

df = pd.DataFrame(data, columns=["city", "state", "date", "high_temp", "low_temp", "rainfall_status", "rainfall", "humidity"])

# Save dataset
df.to_csv("weather_data.csv", index=False)
print("Dataset with all cities and dates created successfully!")
