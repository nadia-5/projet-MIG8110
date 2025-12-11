#!/usr/bin/env python3
"""
Script de Backfill pour Pipeline ETL Olist avec CLEANUP
Charge les données historiques du 2016-09-04 au 2018-08-29
"""

import os
import sys
from datetime import date, timedelta, datetime
from pathlib import Path
import importlib
from typing import Optional
import yaml
import psycopg2
from sqlalchemy import create_engine, text

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent))

from proct_olis.core.config import Config
from proct_olis.core.reader import Reader
from proct_olis.core.writter import Writter
from proct_olis.settings import Settings
from proct_olis.core.session import Session  # ⬅️ pour vérifier les fichiers S3

# --- CONFIGURATION ---
START_DATE = date(2016, 9, 4)
END_DATE = date(2018, 8, 29)

# Mode debug : traiter seulement les X premiers jours
DEBUG_MODE = False
DEBUG_DAYS = 3

# CLEANUP MODE
CLEANUP_BEFORE_RUN = True  # ✅ DROP ALL DATA BEFORE BACKFILL


class Process:
    """Encapsule l'exécution d'un processus ETL."""
    
    def __init__(self, name: str, path: str):
        self.process_name = name
        self.config_path = path
        self.module_path = f"proct_olis.{path.replace('/', '.')}.model"

    def run(self, execution_date: Optional[date] = None):
        """Exécute le processus pour une date donnée."""
        date_str = execution_date.strftime("%Y-%m-%d") if execution_date else None
        
        print(f"\n🔄 [{self.process_name}] Date: {date_str or 'STATIC'}")
        
        try:
            # 1. Charger la configuration
            config_file = Path(__file__).parent / "proct_olis" / self.config_path / "config.yml"
            
            if not config_file.exists():
                raise FileNotFoundError(f"Config introuvable: {config_file}")
            
            with open(config_file, "r") as f:
                config_data = yaml.safe_load(f)
            
            config = Config.from_data(config_data)
            settings = Settings()

            # 2. Charger le module de transformation
            mod = importlib.import_module(self.module_path)
            TransformationClass = getattr(mod, "Transformation")
            
            # 3. Instancier la transformation avec la date
            transformation = TransformationClass(execution_date=date_str)
            
            # 4. Exécuter le pipeline
            transformation.process()
            
            print("   ✅ SUCCESS")
            return True
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            import traceback

            traceback.print_exc()
            return False


def cleanup_databases():
    """🧹 Nettoie toutes les bases avant backfill"""
    print("\n🧹 PHASE -1: NETTOYAGE DES BASES DE DONNÉES")
    print("=" * 70)
    
    # ✅ CORRECT CONNECTION STRINGS
    operational_dsn = "postgresql://admin:admin@postgres:5432/operation"
    
    tables_operational = [
        "order_status_type",
        "payment_type",
        "product_category",
        "customer",
        "seller",
        "product",
        "review",
        "order",
        "order_item",
        "order_payment",
        "order_review",
        "product_seller",
        "location",
    ]
    
    try:
        # Operational DB ONLY (datawarehouse créée par pipeline)
        print("🔗 Connexion Operational DB...")
        engine_op = create_engine(operational_dsn)
        with engine_op.connect() as conn:
            for table in tables_operational:
                try:
                    conn.execute(text(f"TRUNCATE TABLE public.{table} CASCADE"))
                    print(f"🗑️  TRUNCATED: operation.public.{table}")
                except Exception:
                    print(f"⚠️  Table {table} n'existe pas (OK si première run)")
            conn.commit()
        print("✅ Operational DB nettoyée")
        
        print("✅ SKIP Data Warehouse (créée automatiquement par pipeline)")
        print("✅ TOUT PRÊT POUR BACKFILL PROPRE 🚀")
        return True
        
    except Exception as e:
        print(f"❌ Erreur cleanup: {e}")
        print("⚠️  Continuer sans cleanup...")
        return False


# 🔍 Vérifier si la journée a des fichiers sources
def day_has_data(target_date: date) -> bool:
    """
    Retourne True si au moins un CSV source existe pour cette date
    dans s3://sources/daily_data/YYYY-MM-DD/, sinon False.
    """
    settings = Settings()
    fs = Session(settings, kind="s3").s3
    date_str = target_date.strftime("%Y-%m-%d")

    expected_files = [
        "customers.csv",
        "products.csv",
        "sellers.csv",
        "orders.csv",
        "items.csv",
        "order_payments.csv",
        "order_reviews.csv",
    ]

    for filename in expected_files:
        path = f"s3://sources/daily_data/{date_str}/{filename}"
        if fs.exists(path):
            print(f"✅ {date_str}: found {filename} in sources")
            return True

    print(f"⏭️  {date_str}: no source CSVs found, skipping day")
    return False


# --- DÉFINITION DES PROCESSUS (ORDER STRICT POUR FKs) ---

# 🔥 STATIC PRE: Purely independent (run ONCE before everything)
STATIC_PRE_PROCESSES = [
    Process("Geolocation", "datalake/geolocation"),
    Process("Product Category Translation", "datalake/product_category_name"),
    Process("Location", "operations/location"),
    Process("Dim Date", "datawarehouse/dim_date"),
]

# 📊 DAILY PROCESSES
DATALAKE_PROCESSES = [
    Process("Customers Datalake", "datalake/customers"),
    Process("Products Datalake", "datalake/products"),
    Process("Sellers Datalake", "datalake/sellers"),
    Process("Orders Datalake", "datalake/orders"),
    Process("Order Items Datalake", "datalake/order_items"),
    Process("Order Payments Datalake", "datalake/order_payments"),
    Process("Order Reviews Datalake", "datalake/order_reviews"),
]

# 🔥 OPERATIONS: REFERENCE FIRST → PARENTS → CHILDREN
OPERATIONS_PROCESSES = [
    # 1️⃣ REFERENCE TABLES (pour FKs)
    Process("Order Status Type", "operations/order_status_type"),
    Process("Payment Type", "operations/payment_type"),
    Process("Product Category", "operations/product_category"),
    
    # 2️⃣ PARENT TABLES
    Process("Customer", "operations/customer"),
    Process("Seller", "operations/seller"),
    Process("Product", "operations/product"),
    
    # 3️⃣ ORDERS (besoin status_id)
    Process("Order", "operations/order"),
    
    # 4️⃣ CHILD TABLES (besoin order_id)
    Process("Order Item", "operations/order_item"),
    Process("Order Payment", "operations/order_payment"),
    Process("Review", "operations/review"),
    Process("Order Review", "operations/order_review"),
    Process("Product Seller", "operations/product_seller"),
]

DATAWAREHOUSE_PROCESSES = [
    Process("Dim Order Status", "datawarehouse/dim_order_status_type"),
    Process("Dim Location", "datawarehouse/dim_location"),
    Process("Dim Customer", "datawarehouse/dim_customer"),
    Process("Dim Seller", "datawarehouse/dim_seller"),
    Process("Dim Product", "datawarehouse/dim_product"),
    Process("Fact Orders", "datawarehouse/fact_orders"),
]


def run_processes(process_list, phase_name="processes", execution_date=None):
    """Exécute une liste de processus avec date optionnelle."""
    success_count = 0
    total_count = len(process_list)
    
    print(f"\n📋 {phase_name.upper()}")
    print("-" * 50)
    
    for process in process_list:
        if process.run(execution_date=execution_date):
            success_count += 1
    
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
    print(f"\n✅ {phase_name}: {success_count}/{total_count} ({success_rate:.1f}%)")
    return success_count == total_count


def run_daily_processes(target_date: date):
    """Exécute tous les processus quotidiens pour une date donnée."""
    date_str = target_date.strftime("%Y-%m-%d")
    
    print(f"\n{'=' * 70}")
    print(f"📅 TRAITEMENT DU {date_str}")
    print(f"{'=' * 70}")
    
    # 1️⃣ DATALAKE: CSV → Parquet
    print("\n--- 1️⃣ DATALAKE (CSV → Parquet) ---")
    datalake_ok = run_processes(DATALAKE_PROCESSES, f"datalake {date_str}", target_date)
    
    # 2️⃣ OPERATIONS: Reference → Orders → Child tables
    print("\n--- 2️⃣ OPERATIONS (Reference → Orders → Child) ---")
    operations_ok = run_processes(OPERATIONS_PROCESSES, f"operations {date_str}", target_date)
    
    # 3️⃣ DATA WAREHOUSE: SCD2 + Facts
    print("\n--- 3️⃣ DATA WAREHOUSE (SCD2 + Facts) ---")
    dw_ok = run_processes(DATAWAREHOUSE_PROCESSES, f"datawarehouse {date_str}", target_date)
    
    overall_success = datalake_ok and operations_ok and dw_ok
    print(f"\n✅ Journée {date_str} terminée!")
    print(
        f"   📊 Datalake: {'✅' if datalake_ok else '❌'} | "
        f"Operations: {'✅' if operations_ok else '❌'} | "
        f"DW: {'✅' if dw_ok else '❌'}"
    )
    return overall_success


def main():
    """Point d'entrée principal du backfill."""
    print("\n" + "🚀" * 35)
    print("   BACKFILL PIPELINE ETL OLIST + CLEANUP")
    print("🚀" * 35)
    print(f"\nPériode: {START_DATE} → {END_DATE}")
    
    if CLEANUP_BEFORE_RUN:
        print("🧹 CLEANUP MODE: ACTIVÉ ✅")
    else:
        print("🧹 CLEANUP MODE: DÉSACTIVÉ")
    
    if DEBUG_MODE:
        print(f"⚠️  MODE DEBUG: {DEBUG_DAYS} jours seulement")
    
    print(f"Nombre de jours: {(END_DATE - START_DATE).days + 1}")
    
    # Confirmation
    response = input("\n▶️  Continuer ? [o/N] : ")
    if response.lower() not in ["o", "oui", "y", "yes"]:
        print("❌ Annulé par l'utilisateur")
        return
    
    start_time = datetime.now()
    
    # 🧹 PHASE -1: CLEANUP (DROP ALL DATA)
    if CLEANUP_BEFORE_RUN:
        if not cleanup_databases():
            print("\n🛑 CLEANUP ÉCHOUÉ - Arrêt")
            sys.exit(1)
    
    # 🔥 PHASE 0: STATIC PRE (1x only - NO DATE)
    print("\n" + "=" * 70)
    print("🚀 PHASE 0: STATIC PRE-DATALAKE (1x)")
    print("=" * 70)
    if not run_processes(STATIC_PRE_PROCESSES, "static pre-datalake"):
        print("\n🛑 PHASE 0 ÉCHOUÉE")
        sys.exit(1)
    
    # 📊 PHASE 1: DAILY PROCESSING LOOP
    current_date = START_DATE
    days_processed = 0
    days_failed = 0
    
    while current_date <= END_DATE:
        # Mode debug
        if DEBUG_MODE and days_processed >= DEBUG_DAYS:
            print(f"\n⚠️  Mode debug: Arrêt après {DEBUG_DAYS} jours")
            break

        # ✅ Skip days without any source data
        if not day_has_data(current_date):
            current_date += timedelta(days=1)
            continue
        
        success = run_daily_processes(current_date)
        
        if success:
            days_processed += 1
        else:
            days_failed += 1
        
        current_date += timedelta(days=1)
    
    # 📈 RAPPORT FINAL
    duration = datetime.now() - start_time
    print("\n" + "=" * 70)
    print("✨ BACKFILL TERMINÉ")
    print("=" * 70)
    print(f"✅ Jours réussis: {days_processed}")
    print(f"❌ Jours échoués: {days_failed}")
    print(f"⏱️  Durée totale: {duration}")
    print(f"⚡ Temps moyen/jour: {duration / max(days_processed, 1)}")
    
    if CLEANUP_BEFORE_RUN:
        print("🧹 Cleanup exécuté avant ce run")
    
    if days_failed == 0:
        print("\n🎉 SUCCÈS COMPLET! Pipeline prêt pour Power BI! 🚀")
    else:
        print(f"\n⚠️  {days_failed} jours ont échoué (vérifier les logs)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Backfill interrompu par l'utilisateur (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n🛑 ERREUR CRITIQUE: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
