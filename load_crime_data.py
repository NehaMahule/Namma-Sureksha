import pandas as pd

def load_crime_data(filepath='crime_dataset_with_latlon.csv'):
    df = pd.read_csv(filepath)
    crimes = []
    for _, row in df.iterrows():
        crime = {
            'lat': row['Latitude'],
            'lon': row['Longitude'],
            'intensity': min(1, row['Number_of_Crimes'] / 10)  # normalize
        }
        crimes.append(crime)
    return crimes
