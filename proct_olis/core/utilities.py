import polars as pl
import unicodedata

class Utilities:

    def calculate_hash_based_on_columns(self, df: pl.DataFrame, columns: list[str]) -> pl.DataFrame:
        concat_columns = pl.concat_str([pl.col(col).cast(pl.Utf8) for col in sorted(columns)], separator="|")
        return df.with_columns(concat_columns.hash().cast(pl.Utf8).alias("hash_key")) 

    def add_primary_key(self, df: pl.DataFrame, mode: str = "auto", primary_key: str = "pk", business_keys: list[str] = None) -> pl.DataFrame:

        if not isinstance(primary_key, str):
            raise TypeError("La clé primaire doit être une chaîne de caractères.")

        # ----------- AUTO INCREMENT -----------
        if mode == "auto":
            # Crée la clé primaire même si elle n'existe pas
            return df.with_row_index(name=primary_key, offset=1)

        # ----------- HASH MODE -----------
        elif mode == "hash":
            if not business_keys:
                raise ValueError("Les business_keys doivent être fournies pour le mode hash")

            return df.with_columns(
                pl.concat_str([pl.col(c).cast(str) for c in business_keys], separator="|")
                .hash()
                .alias(primary_key)
            )

        else:
            raise ValueError("Mode non supporté: choisir 'auto' ou 'hash'")



    def remove_accents(self, text: str) -> str:
        # Décompose les caractères accentués en base + diacritiques
        nfkd_form = unicodedata.normalize("NFKD", text)
        # Filtre les diacritiques (catégorie Mn = Mark, Nonspacing)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])