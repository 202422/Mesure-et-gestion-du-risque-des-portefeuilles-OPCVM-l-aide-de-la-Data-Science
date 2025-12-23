import os
import csv
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm
from requests.exceptions import RequestException
import re
from urllib.parse import unquote
import pandas as pd



# =======================
# CONFIGURATION
# =======================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))



BASE_URL = "https://www.wafagestion.com"
START_PATH = "/fr/rapports-et-analyses/Weekly-OPCVM"
START_URL = urljoin(BASE_URL, START_PATH)

DOWNLOAD_DIR = os.path.join(BASE_DIR, "data", "weekly_opcvm")
CSV_FILE = os.path.join(BASE_DIR, "downloaded_files.csv")
NEW_CSV_FILE = os.path.join(BASE_DIR, "new_data.csv")


REQUEST_TIMEOUT = 15
SLEEP_BETWEEN_REQUESTS = 1

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; WeeklyOPCVM-Scraper/1.0)"
}

# =======================
# SETUP
# =======================

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

session = requests.Session()
session.headers.update(HEADERS)

# =======================
# CSV MANAGEMENT
# =======================

def load_downloaded_files():
    """Charge les fichiers déjà téléchargés depuis le CSV"""
    downloaded = set()

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                downloaded.add(row["filename"])

    return downloaded



def save_downloaded_file(filename, url):
    """Ajoute un fichier téléchargé au CSV en conservant un index correct"""
    # Extraire la date du filename
    try:
        file_date_str = filename.replace(".pdf", "")
        file_date = datetime.strptime(file_date_str, "%d-%m-%Y").date()
    except ValueError:
        print(f"⚠️ Impossible de convertir la date du fichier : {filename}")
        file_date = ""

    # Créer un DataFrame temporaire
    df_new = pd.DataFrame([{
        "filename": filename,
        "url": url,
        "download_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date": file_date.strftime("%Y-%m-%d") if file_date else ""
    }])

    # Si le CSV existe, concaténer ; sinon créer
    if os.path.exists(CSV_FILE):
        df_existing = pd.read_csv(CSV_FILE)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    # Sauvegarder en écrasant l'ancien CSV et sans créer de colonne index supplémentaire
    df_combined.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")



def save_new_downloaded_file(filename, url):
    """
    Ajoute un fichier téléchargé au CSV new_data.csv
    avec colonne 'date' extraite du filename
    """

    file_exists = os.path.exists(NEW_CSV_FILE)

    # Extraire la date depuis le filename (ex: 31-12-2022.pdf)
    try:
        file_date_str = filename.replace(".pdf", "")
        file_date = datetime.strptime(file_date_str, "%d-%m-%Y").date()
    except ValueError:
        print(f"⚠️ Impossible de convertir la date du fichier : {filename}")
        file_date = ""

    with open(NEW_CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Écriture de l’en-tête si fichier inexistant
        if not file_exists:
            writer.writerow(["filename", "url", "download_date", "date"])

        writer.writerow([
            filename,
            url,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # download_date
            file_date.strftime("%Y-%m-%d") if file_date else ""
        ])

# =======================
# SCRAPING FUNCTIONS
# =======================

MAX_RETRIES = 5

def safe_get(url, timeout=15):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except RequestException as e:
            print(f"⚠️ Tentative {attempt} échouée : {e}")
            time.sleep(2 * attempt)  # backoff exponentiel
    raise Exception(f"❌ Échec après {MAX_RETRIES} tentatives : {url}")


from bs4 import BeautifulSoup

def get_soup(url):
    """Télécharge la page et retourne un objet BeautifulSoup"""
    response = safe_get(url, timeout=REQUEST_TIMEOUT)
    return BeautifulSoup(response.text, "lxml")


def extract_pdf_links(soup):
    pdf_links = []
    for a in soup.select('a[href$=".pdf"]'):
        href = a.get("href")
        if href:
            pdf_links.append(urljoin(BASE_URL, href))
    return list(set(pdf_links))

"""
def download_pdf(url, downloaded_files):
    filename = url.split("/")[-1]
    filepath = os.path.join(DOWNLOAD_DIR, filename)

    if filename in downloaded_files:
        return False

    with session.get(url, stream=True, timeout=REQUEST_TIMEOUT) as r:
        r.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    

    save_downloaded_file(filename, url)
    downloaded_files.add(filename)
    return True
"""

def extract_date_from_filename(url):
    """
    Extrait une date depuis le nom du fichier et la normalise en DD-MM-YYYY
    """
    filename = unquote(url.split("/")[-1]).lower()

    # Formats possibles :
    patterns = [
        r'(\d{2})[_\-](\d{2})[_\-](\d{4})',   # 12_02_2021 ou 12-02-2021
        r'(\d{2})(\d{2})(\d{4})'             # 08012021
    ]

    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            day, month, year = match.groups()
            return f"{day}-{month}-{year}.pdf"

    return None


# Load already downloaded files CSV
downloaded_df = pd.read_csv(CSV_FILE)  # columns: filename,url,download_date,date

# Convert the 'date' column to datetime
downloaded_df['date'] = pd.to_datetime(downloaded_df['date'], format='%Y-%m-%d')


# Find the most recent downloaded file date
if not downloaded_df.empty:
    most_recent_date = downloaded_df['date'].max()
else:
    most_recent_date = None

def download_pdf(url, downloaded_files):
    # Extraire une date propre
    new_filename = extract_date_from_filename(url)

    if not new_filename:
        print(f"⚠️ Date non reconnue dans l'URL : {url}")
        return False

    # Extract date from filename
    file_date_str = new_filename.replace(".pdf", "")
    try:
        file_date = datetime.strptime(file_date_str, "%d-%m-%Y")
    except ValueError:
        print(f"⚠️ Impossible de convertir la date du fichier : {new_filename}")
        return False

    # Skip if file date is not newer than most recent downloaded
    if most_recent_date and file_date <= most_recent_date:
        print(f"⏹️ Reached already downloaded file: {new_filename}, skipping.")
        return "stop"


    # Skip if file already downloaded in memory
    if new_filename in downloaded_files:
        return False

    

    filepath = os.path.join(DOWNLOAD_DIR, new_filename)

    with session.get(url, stream=True, timeout=REQUEST_TIMEOUT) as r:
        r.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    save_downloaded_file(new_filename, url)
    save_new_downloaded_file(new_filename, url)
    downloaded_files.add(new_filename)
    print(f"✅ Downloaded {new_filename}")
    return True



def get_next_page(soup):
    next_link = soup.select_one("li.pager-next a")
    if next_link:
        return urljoin(BASE_URL, next_link.get("href"))
    return None

# =======================
# MAIN
# =======================


def scrape_all_reports():
    downloaded_files = load_downloaded_files()
    page_number = 0
    new_files = 0
    stop_scraping = False  # <-- nouveau drapeau

    while True:
        # Génère l'URL de la page
        if page_number == 0:
            current_page = START_URL
        else:
            current_page = f"{START_URL}?page={page_number}"

        print(f"\n📄 Page {page_number + 1} : {current_page}")
        soup = get_soup(current_page)

        pdf_links = extract_pdf_links(soup)
        if not pdf_links:
            print("⚠️ Plus de PDF trouvés, fin du scraping.")
            break

        print(f"➡️  {len(pdf_links)} PDF trouvés")

        for pdf_url in tqdm(pdf_links, desc="Téléchargement"):
            result = download_pdf(pdf_url, downloaded_files)

            if result == "stop":  # <-- PDF trop ancien détecté
                stop_scraping = True
                continue  # continuer la boucle for jusqu'au dernier PDF

            elif result:
                new_files += 1

            time.sleep(0.5)  # pause pour ne pas surcharger le serveur

        if stop_scraping:
            print("⏹️ PDF ancien détecté : arrêt après cette page.")
            break  # arrêter le while, ne pas passer à la page suivante

        page_number += 1
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    print("\n✅ Scraping terminé")
    print(f"📊 Nouveaux fichiers téléchargés : {new_files}")
    print(f"📁 Total fichiers connus : {len(downloaded_files)}")




if __name__ == "__main__":
    scrape_all_reports()
