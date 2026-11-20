# Projet 5 — Web Scraping & Pipeline de Données 

## Contexte
Construction d'un **pipeline ETL complet et automatisé** : collecte de données sur un site web,
nettoyage, stockage dans une base SQLite, puis analyse SQL et visualisation. Le pipeline
s'exécute seul via le planificateur de tâches et construit un **historique** des collectes.

Le site utilisé, [books.toscrape.com](https://books.toscrape.com), est un faux site de librairie
conçu pour s'entraîner au scraping : aucun risque légal ou éthique.

## Architecture du pipeline

```
Site web ──► EXTRACT ──► TRANSFORM ──► LOAD ──► SQLite ──► Analyse SQL
            requests     Pandas        to_sql    livres.db    + Plotly
            BeautifulSoup contrôle
                          qualité
                 ▲
                 ├── Planificateur de tâches (exécution automatique)
                 └── pipeline.log (journal de chaque exécution)
```

## Données collectées
| Champ | Description |
|---|---|
| titre | Titre complet du livre |
| prix | Prix en livres sterling (converti de texte en nombre) |
| note | Note de 1 à 5 (convertie depuis "One", "Two"...) |
| en_stock | Disponibilité (booléen) |
| page | Page du catalogue d'origine |
| date_collecte | Horodatage de la collecte, base de l'historique |

**Volume :** 1 000 livres sur 50 pages, collectés en environ 90 secondes.

## Bonnes pratiques mises en œuvre
- **Scraping poli** : pause d'1 seconde entre les requêtes (rate limiting) et `timeout` de 10 secondes
- **Gestion des erreurs** : une page en échec est ignorée et journalisée, sans interrompre la collecte
- **Contrôle qualité** : le pipeline refuse de stocker des données incohérentes (prix ≤ 0, notes manquantes)
- **Journalisation** : chaque exécution écrit dans `pipeline.log`
- **Historique** : chaque collecte est ajoutée (`append`) avec sa date, sans écraser les précédentes
- **Chemins robustes** : le script retrouve ses fichiers via `Path(__file__)`, quel que soit le dossier de lancement

## Automatisation (Windows)
```bash
schtasks /create /tn "PipelineLivres" /tr "\"<chemin>\python.exe\" \"<chemin>\pipeline.py\"" /sc daily /st 08:00
```
Test de la planification : deux collectes distinctes de 1 000 livres sont présentes dans la base,
dont une lancée automatiquement par le planificateur.

## Stack technique
![Python](https://img.shields.io/badge/Python-3.14-blue)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4-green)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57)
![Pandas](https://img.shields.io/badge/Pandas-2.0-lightblue)
![Plotly](https://img.shields.io/badge/Plotly-6.3-blue)

## Structure du repo
```
projet-05-web-scraping/
├── scraping_pipeline.ipynb   — Exploration pas à pas (scraping, nettoyage, SQL, graphiques)
├── pipeline.py               — Pipeline ETL automatisable
├── .gitignore                — Exclut livres.db et pipeline.log (fichiers générés)
└── README.md
```

> `livres.db` et `pipeline.log` sont générés à l'exécution et ne sont pas versionnés.

## Utilisation
```bash
pip install requests beautifulsoup4 pandas plotly
python pipeline.py
```

## Auteur
**Shanice Marvin Tiogang** · Business Analytics & Data Science · Tunis
