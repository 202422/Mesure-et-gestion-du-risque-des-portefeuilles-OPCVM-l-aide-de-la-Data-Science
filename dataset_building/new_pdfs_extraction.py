# Import libraries
import pdfplumber
import pandas as pd
import re
from datetime import datetime
import os
from glob import glob

# ============================================
# Functions
# ============================================




def extract_diversifie_data(pdf_path):
    """
    Extract ATTIJARI DIVERSIFIE data with precise field mapping.
    Returns a dictionary with all performance metrics.
    """
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    
    lines = text.split('\n')
    
    for line in lines:
        if 'DIVERSIFIE' in line.upper() and 'PATRIMOINE' not in line.upper():
            pattern = r'(\d+(?:\.\d+)?%?)'
            matches = re.findall(pattern, line)
            
            if len(matches) >= 9:
                return {
                    'Fonds': 'ATTIJARI DIVERSIFIE',
                    'Horizon minimum conseillé': matches[0],
                    'Valeur Liquidative': matches[1],
                    'Performances glissantes Depuis Début d\'année': matches[2],
                    'Performances glissantes 1 semaine': matches[3],
                    'Performances glissantes 6 mois': matches[4],
                    'Performances glissantes 1 an': matches[5],
                    'Performances glissantes 2 ans': matches[6],
                    'Performances glissantes 3 ans': matches[7],
                    'Performances glissantes 5 ans': matches[8]
                }
    return None


def extract_date_from_filename(filepath):
    """
    Extract date from filename in format: DD-MM-YYYY.pdf -> YYYY-MM-DD
    """
    filename = os.path.basename(filepath)
    pattern = r'(\d{2})-(\d{2})-(\d{4})'
    match = re.search(pattern, filename)
    if match:
        day, month, year = match.groups()
        try:
            date = datetime(int(year), int(month), int(day))
            return date.strftime('%Y-%m-%d')
        except ValueError:
            return None
    return None


# ============================================
# Paths
# ============================================

# ============================================
# Base directory
# ============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PDF_FOLDER = os.path.normpath(os.path.join(BASE_DIR, "../weekly-opcvm-scraper/data/weekly_opcvm"))
OUTPUT_CSV = os.path.normpath(os.path.join(BASE_DIR, "DIVERSIFIE_ALL.csv"))

# Load existing CSV
if os.path.exists(OUTPUT_CSV):
    existing_df = pd.read_csv(OUTPUT_CSV)
    existing_dates = set(pd.to_datetime(existing_df['Date']).dt.date)
else:
    existing_df = pd.DataFrame()
    existing_dates = set()

# Get all PDFs in folder
pdf_files = glob(os.path.join(PDF_FOLDER, "*.pdf"))


# ============================================
# Extraction
# ============================================

all_data = []

for pdf_file in pdf_files:
    date_str = extract_date_from_filename(pdf_file)
    if date_str is None:
        print(f"⚠️ Could not extract date from {pdf_file}")
        continue
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    # Skip if already extracted
    if date_obj in existing_dates:
        print(f"⏹️ Already extracted: {pdf_file} | Date={date_str}")
        continue
    
    # Extract data
    data = extract_diversifie_data(pdf_file)
    if data:
        data['Date'] = date_str
        all_data.append(data)
        print(f"✓ Extracted: {pdf_file} | Date={date_str}, VL={data['Valeur Liquidative']}")
    else:
        print(f"✗ No data found in {pdf_file}")

# ============================================
# Save updated CSV
# ============================================

if all_data:
    df_new = pd.DataFrame(all_data)
    combined_df = pd.concat([existing_df, df_new], ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset=["Date"])
    combined_df = combined_df.sort_values("Date").reset_index(drop=True)
    combined_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    print(f"\n✅ Saved {len(df_new)} new records to {OUTPUT_CSV}")
else:
    print("\n✗ No new data extracted")
