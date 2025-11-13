import polars as pl
import unicodedata

class Utilities:

    def calculate_hash_based_on_columns(self, df: pl.DataFrame, columns: list[str]) -> pl.DataFrame:
        concat_columns = pl.concat_str([pl.col(col).cast(pl.Utf8) for col in columns], separator="|")
        return df.with_columns(concat_columns.hash().alias("hash_key")) 

    import polars as pl


    def add_primary_key(self, df: pl.DataFrame, mode: str = "auto", primary_key: str = "pk", business_keys: list[str] = None) -> pl.DataFrame:
        """
        Ajoute une clé primaire au DataFrame Polars.
        
        Args:
            df: DataFrame Polars
            mode: "auto" pour auto-increment, "hash" pour hash des business keys
            business_keys: liste des colonnes business key (obligatoire si mode="hash")
        
        Returns:
            DataFrame avec une colonne 'pk'
        """
        if mode == "auto":
            # Auto-increment basé sur l'index
            df = df.with_row_index(name=primary_key, offset=1)  # offset=1 pour commencer à 1
        
        elif mode == "hash":
            if not business_keys:
                raise ValueError("Les business_keys doivent être fournies pour le mode hash")
            
            # Concaténer les colonnes business keys en une seule chaîne
            df = df.with_columns(
                pl.concat_str([pl.col(c).cast(str) for c in business_keys], separator="|")
                .hash()
                .alias(primary_key)
            )
        
        else:
            raise ValueError("Mode non supporté: choisir 'auto' ou 'hash'")
        
        return df

    def remove_accents(self, text: str) -> str:
        # Décompose les caractères accentués en base + diacritiques
        nfkd_form = unicodedata.normalize("NFKD", text)
        # Filtre les diacritiques (catégorie Mn = Mark, Nonspacing)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])