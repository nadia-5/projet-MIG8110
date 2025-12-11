import subprocess
import time
from datetime import datetime

# --- CONFIGURATION ---
# Intervalle d'attente entre deux lancements (4 minutes)
REAL_TIME_INTERVAL_SECONDS = 4 * 60

# ID du DAG datawarehouse
DAG_ID = "olis_etl_datawarehouse"

def trigger_airflow():
    """Déclenche le DAG datawarehouse"""
    print(f"⏰ [Temps Réel: {datetime.now().strftime('%H:%M:%S')}] -> Lancement du chargement datawarehouse")
    
    try:
        # Commande CLI Airflow pour déclencher le DAG
        cmd = ["airflow", "dags", "trigger", DAG_ID]
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    print("🚀 Démarrage du chargement continu du datawarehouse (toutes les 4 minutes)...")

    while True:
        # 1. Déclencher le pipeline datawarehouse
        trigger_airflow()
        
        # 2. Attendre 4 minutes avant le prochain lancement
        print(f"💤 Pause de {REAL_TIME_INTERVAL_SECONDS/60} minutes avant le prochain chargement...")
        time.sleep(REAL_TIME_INTERVAL_SECONDS)
