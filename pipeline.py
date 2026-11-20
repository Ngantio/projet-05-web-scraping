# ============================================================
# PROJET 5 — PIPELINE ETL : BOOKS.TOSCRAPE.COM -> SQLITE
# Extract (scraping) -> Transform (Pandas) -> Load (SQLite)
# ============================================================

import logging
import sqlite3
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- Configuration ---
BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
NB_PAGES = 50
DOSSIER = Path(__file__).parent            # dossier où se trouve ce script
DB_PATH = DOSSIER / "livres.db"
LOG_PATH = DOSSIER / "pipeline.log"

NOTES = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

# --- Journal d'exécution ---
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
)


def extract():
    """E : scrape les pages du catalogue et retourne une liste de livres bruts."""
    livres_bruts = []
    for numero in range(1, NB_PAGES + 1):
        try:
            reponse = requests.get(BASE_URL.format(numero), timeout=10)
            reponse.encoding = "utf-8"
            reponse.raise_for_status()      # lève une erreur si le code n'est pas 200
        except requests.RequestException as erreur:
            logging.warning(f"Page {numero} ignorée : {erreur}")
            continue

        soup = BeautifulSoup(reponse.text, "html.parser")
        for livre in soup.find_all("article", class_="product_pod"):
            livres_bruts.append({
                "titre": livre.h3.a["title"],
                "prix": livre.find("p", class_="price_color").text,
                "note": livre.find("p", class_="star-rating")["class"][1],
                "disponibilite": livre.find("p", class_="instock availability").text.strip(),
                "page": numero,
            })
        time.sleep(1)                       # scraping poli : 1 seconde entre les pages
    return livres_bruts


def transform(livres_bruts):
    """T : nettoie les données et ajoute la date de collecte."""
    df = pd.DataFrame(livres_bruts)
    df["prix"] = df["prix"].str.replace("£", "", regex=False).astype(float)
    df["note"] = df["note"].map(NOTES)
    df["en_stock"] = df["disponibilite"] == "In stock"
    df = df.drop(columns=["disponibilite"])
    df["date_collecte"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Contrôle qualité : on refuse de stocker des données incohérentes
    if df.empty or (df["prix"] <= 0).any() or df["note"].isnull().any():
        raise ValueError("Données invalides détectées, stockage annulé")
    return df


def load(df):
    """L : ajoute les données dans la table SQLite (un historique se construit)."""
    with sqlite3.connect(DB_PATH) as connexion:
        df.to_sql("livres", connexion, if_exists="append", index=False)


def main():
    debut = time.time()
    logging.info("=== Démarrage du pipeline ===")
    try:
        livres_bruts = extract()
        logging.info(f"Extract : {len(livres_bruts)} livres récupérés")

        df = transform(livres_bruts)
        logging.info(f"Transform : {len(df)} lignes propres")

        load(df)
        logging.info(f"Load : données ajoutées dans {DB_PATH.name}")
        logging.info(f"=== Pipeline terminé en {time.time() - debut:.0f} secondes ===")
        print("✅ Pipeline terminé avec succès")
    except Exception as erreur:
        logging.error(f"Pipeline en échec : {erreur}")
        print(f"❌ Pipeline en échec : {erreur}")


if __name__ == "__main__":
    main()