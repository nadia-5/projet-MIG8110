import subprocess
import time
from datetime import datetime, timedelta

# --- CONFIGURATION ---
# 1. Temps Métier (La date envoyée au pipeline)
# Tu commences le 1er Janvier 2027
SIMULATION_CURRENT_DATE = datetime(2017, 1, 5)

# 2. Temps Réel (Intervalle d'attente entre deux lancements)
# 15 minutes * 60 secondes
REAL_TIME_INTERVAL_SECONDS = 2 * 60 

# ID de ton DAG
DAG_ID = "olis_etl_operationnel"

def trigger_airflow(sim_date):
    """Déclenche le DAG avec la date simulée en paramètre"""
    date_str = sim_date.strftime("%Y-%m-%d") # On envoie juste la date (YYYY-MM-DD)
    
    # Construction du JSON de config
    conf_json = f'{{"simulation_date": "{date_str}"}}'
    
    print(f"⏰ [Temps Réel: {datetime.now().strftime('%H:%M:%S')}] -> Lancement pour la date de données : {date_str}")
    
    try:
        # Commande CLI Airflow pour déclencher le DAG
        cmd = ["airflow", "dags", "trigger", DAG_ID, "--conf", conf_json]
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    print("🚀 Démarrage de la simulation accélérée (1 jour de données toutes les 15 minutes)...")

    while True:
        # 1. Déclencher le pipeline pour la date actuelle
        trigger_airflow(SIMULATION_CURRENT_DATE)
        
        # 2. Avancer le Temps Métier de 1 JOUR (et non 15 min)
        SIMULATION_CURRENT_DATE += timedelta(days=1)
        
        # 3. Attendre le Temps Réel de 15 MINUTES
        print(f"💤 Pause de {REAL_TIME_INTERVAL_SECONDS/60} minutes avant le prochain jour...")
        time.sleep(REAL_TIME_INTERVAL_SECONDS)