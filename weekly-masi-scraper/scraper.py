from playwright.sync_api import sync_playwright
import time
import pandas as pd
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

cleaned_file = os.path.join(BASE_DIR, 'MASI_cleaned.csv')

URL = "https://fr.investing.com/indices/masi-historical-data"

CSV_FILE = os.path.normpath(
    os.path.join(BASE_DIR, '..', 'weekly-opcvm-scraper', 'new_data.csv')
)

OUTPUT_DIR = os.path.join(BASE_DIR, 'data', 'weekly_masi')
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'weekly_masi_data.csv')

def get_dates_from_csv(csv_file):
    """
    Récupère les dates à scraper depuis le fichier CSV existant.
    Retourne une liste de dates au format 'dd/mm/yyyy', décalées de +2 jours.
    """
    if not os.path.exists(csv_file):
        print(f"⚠️ Le fichier {csv_file} n'existe pas. Aucun scraping effectué.")
        return []

    df = pd.read_csv(csv_file)
    dates = df['date'].dropna().unique().tolist()  # colonne 'date' extraite du CSV
    # Convertir en format dd/mm/yyyy si nécessaire
    dates_str = []
    for d in dates:
        try:
            date_obj = pd.to_datetime(d)
            date_obj = date_obj + pd.Timedelta(days=2)  # Ajouter 2 jours
            dates_str.append(date_obj.strftime("%d/%m/%Y"))
        except:
            continue
    return dates_str

def get_weekly_data_by_date(date_str: str):

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,          # ✅ headless OBLIGATOIRE ici
            args=[
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-extensions",
                "--disable-background-networking",
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
            ]
        )

        context = browser.new_context(
            locale="fr-FR",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        # 🚫 BLOQUER TOUT CE QUI EST LOURD
        context.route("**/*", lambda route, request:
            route.abort()
            if request.resource_type in ["image", "media", "font"]
            else route.continue_()
        )

        page = context.new_page()

        # ⚠️ NE PAS attendre "load"
        page.goto(URL, wait_until="domcontentloaded", timeout=120000)

        # 🍪 Cookies
        try:
            page.locator("button:has-text('Tout accepter')").click(timeout=5000)
        except:
            pass


        # 📅 Sélecteur Unité de temps
        page.locator("div.historical-data-v2_selection-arrow__3mX7U").first.click()
        # Sélection Hebdomadaire (sélecteur précis)
        page.locator(
            "span.historical-data-v2_menu-row-text__ZgtVH",
            has_text="Hebdomadaire"
        ).click()

        time.sleep(2)

        # 📊 Tableau
        rows = page.locator("tr.historical-data-v2_price__atUfP")
        count = rows.count()

        for i in range(count):
            row = rows.nth(i)
            cells = row.locator("td")

            row_date = cells.nth(0).inner_text().strip()

            if row_date == date_str:
                data = {
                    "date": row_date,
                    "close": cells.nth(1).inner_text().strip(),
                    "open": cells.nth(2).inner_text().strip(),
                    "high": cells.nth(3).inner_text().strip(),
                    "low": cells.nth(4).inner_text().strip(),
                    "volume": cells.nth(5).inner_text().strip(),
                    "variation": cells.nth(6).inner_text().strip(),
                }

                browser.close()
                return data

        browser.close()
        return None



def save_results_to_csv(results, output_dir=OUTPUT_DIR, output_file=OUTPUT_FILE):
    """
    Concatène les résultats, transforme les colonnes et sauvegarde dans un CSV.
    Format final : Date, Variation %, weekly_mean
    """
    if not results:
        print("⚠️ Aucun résultat à sauvegarder.")
        return

    # Créer le dossier si nécessaire
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Transformation des données
    formatted_results = []
    for row in results:
        # Date
        date_val = row.get("date", "")

        # Variation %
        var_str = row.get("variation", "").replace("%", "").replace("+", "").replace(",", ".").strip()
        try:
            var_val = float(var_str)
        except:
            var_val = None

        # weekly_mean = close
        close_str = row.get("close", "").replace(".", "").replace(",", ".").strip()
        try:
            weekly_mean_val = float(close_str)
        except:
            weekly_mean_val = None

        formatted_results.append({
            "Date": date_val,
            "Variation %": var_val,
            "weekly_mean": weekly_mean_val
        })

    df = pd.DataFrame(formatted_results)
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"✅ Données sauvegardées dans {output_file}")



if __name__ == "__main__":
    dates_to_scrape = get_dates_from_csv(CSV_FILE)
    if not dates_to_scrape:
        print("Aucune date à scraper.")
    else:
        all_results = []
        for date_str in dates_to_scrape:
            print(f"Scraping pour la date {date_str} ...")
            result = get_weekly_data_by_date(date_str)
            if result:
                all_results.append(result)
            else:
                print(f"⚠️ Pas de données trouvées pour {date_str}")

        save_results_to_csv(all_results)
