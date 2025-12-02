import argparse
import importlib
import sys

# On n'a pas besoin d'importer Settings ici, TransformationBase s'en charge

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, required=False, help="Date de simulation (YYYY-MM-DD)")
    parser.add_argument('--module', type=str, required=True, help="Ex: operations")
    parser.add_argument('--transformation_name', type=str, required=True, help="Ex: product_seller")
    
    args = parser.parse_args()

    print(f"🚀 Lancement : {args.module}/{args.transformation_name} pour la date {args.date}")

    try:
        # Chargement dynamique du module (ex: proct_olis.operations.product_seller.model)
        module_path_str = f"proct_olis.{args.module}.{args.transformation_name}.model"
        mod = importlib.import_module(module_path_str)
        
        # Récupération de la classe Transformation
        TransformationClass = getattr(mod, "Transformation")
        
        # Instanciation AVEC la date
        process_instance = TransformationClass(execution_date=args.date)
        
        # Lancement
        process_instance.process()
        
    except Exception as e:
        print(f"❌ Erreur critique : {e}")
        # Affiche plus de détails si besoin pour le débogage
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()