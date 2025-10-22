import pandas as pd
import os

data_folder = "data"
files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]

for file in files:
    file_path = os.path.join(data_folder, file)
    df = pd.read_csv(file_path)
    
    print(f"\n--- Analyse pour {file} ---")
    print("Dimensions:", df.shape)
    
    # KPI
    total_clients = len(df)
    unique_clients = df['customer_unique_id'].nunique()
    unique_cities = df['customer_city'].nunique()
    unique_states = df['customer_state'].nunique()
    
    #print(f"Nombre total de clients : {total_clients}")
    print(f"Nombre de clients uniques : {unique_clients}")
    print(f"Nombre de villes distinctes : {unique_cities}")
    print(f"Nombre d'états distincts : {unique_states}")
    
    # Top villes
    top_cities = df['customer_city'].value_counts().head(5)
    print("\nTop 5 des villes avec le plus de clients :")
    print(top_cities)
    
    # Top états
    top_states = df['customer_state'].value_counts().head(5)
    print("\nTop 5 des états avec le plus de clients :")
    print(top_states)
