import time
import board
import adafruit_dht
from datetime import datetime
import pandas as pd
import os

csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sensor_readings.csv")
sensor = adafruit_dht.DHT11(board.D4)

if not os.path.exists(csv_path): 
    columns = ["timestamp", "temp_c", "humidity"]
    df = pd.DataFrame(columns=columns)
    df.to_csv(csv_path, index=False)

# Try to load existing data
try:
    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
except FileNotFoundError:
    df = pd.DataFrame(columns=["timestamp", "temp_c", "humidity"])

try:
    while True:
        try:
            temp_c = sensor.temperature
            hum = sensor.humidity
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if temp_c is not None and hum is not None:
                new_data = pd.DataFrame([{
                    "timestamp": timestamp,
                    "temp_c": temp_c,
                    "humidity": hum
                }])
                df = pd.concat([df, new_data], ignore_index=True)
                df.to_csv(csv_path, index=False)

               
                df = df.tail(2000)

            else:
                print(f"{timestamp}: Sensor reading failed.")

        except RuntimeError as error:
            print("Runtime error:", error.args[0])
            time.sleep(2.0)
            continue
        except KeyboardInterrupt:
            print("Exiting...")
            sensor.exit()
            break
        except Exception as error:
            sensor.exit()
            raise error

        time.sleep(900.0)

except Exception as e:
	print("Fatal error:", e)
	sensor.exit()