# Import libraries
import pdfplumber
import pandas as pd
import re
from IPython.display import display
from datetime import datetime
import os
from glob import glob


# Update this path to your PDF file
PDF_FILE = "../weekly-opcvm-scraper/data/weekly_opcvm/weekly_opcvm_01_03_2024.pdf"


def extract_diversifie_data(pdf_path):
    """
    Extract ATTIJARI DIVERSIFIE data with precise field mapping.
    
    Returns:
        Dictionary with all performance metrics
    """
    
    # Extract text from PDF
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    
    # Search for ATTIJARI DIVERSIFIE line
    lines = text.split('\n')

    
    for line in lines:
        # Look for line containing "ATTĲARI DIVERSIFIE" or "ATTIJARI DIVERSIFIE"
        if 'DIVERSIFIE' in line.upper() and 'PATRIMOINE' not in line.upper():
            print(f"Found line: {line}\n")
            
            # Use regex to extract all numeric values
            # Pattern matches: numbers with optional decimals and percentage signs
            pattern = r'(\d+(?:\.\d+)?%?)'
            matches = re.findall(pattern, line)
            
            print(f"Extracted values: {matches}\n")
            
            
            if len(matches) >= 9:
                result = {
                    'Fonds': 'ATTIJARI DIVERSIFIE',
                    'Horizon minimum conseillé': f"{matches[0]}",
                    'Valeur Liquidative': matches[1],
                    'Performances glissantes Depuis Début d\'année': matches[2],
                    'Performances glissantes 1 semaine': matches[3],
                    'Performances glissantes 6 mois': matches[4],
                    'Performances glissantes 1 an': matches[5],
                    'Performances glissantes 2 ans': matches[6],
                    'Performances glissantes 3 ans': matches[7],
                    'Performances glissantes 5 ans': matches[8]
                }
                
                return result
            else:
                print(f"Warning: Expected at least 9 values, found {len(matches)}")
                
                # Try alternative extraction
                # Split by whitespace and filter numeric values
                parts = line.split()
                numeric_parts = []
                for part in parts:
                    # Check if part contains numbers
                    if re.search(r'\d', part):
                        numeric_parts.append(part)
                
                print(f"Alternative extraction: {numeric_parts}")
                
                if len(numeric_parts) >= 9:
                    result = {
                        'Fonds': 'ATTIJARI DIVERSIFIE',
                        'Horizon minimum conseillé': f"{numeric_parts[0]}",
                        'Valeur Liquidative': numeric_parts[1],
                        'Performances glissantes Depuis Début d\'année': numeric_parts[2],
                        'Performances glissantes 1 semaine': numeric_parts[3],
                        'Performances glissantes 6 mois': numeric_parts[4],
                        'Performances glissantes 1 an': numeric_parts[5],
                        'Performances glissantes 2 ans': numeric_parts[6],
                        'Performances glissantes 3 ans': numeric_parts[7],
                        'Performances glissantes 5 ans': numeric_parts[8]
                    }
                    return result
    
    print("ATTIJARI DIVERSIFIE not found in PDF")
    return None




def extract_date_from_filename(filepath):
    """
    Extract date from filename in format: DD-MM-YYYY.pdf
    Example: 01-03-2024.pdf -> 2024-03-01
    """
    # Get just the filename without path
    filename = os.path.basename(filepath)
    
    # Pattern for DD-MM-YYYY
    pattern = r'(\d{2})-(\d{2})-(\d{4})'
    match = re.search(pattern, filename)
    
    if match:
        day = match.group(1)
        month = match.group(2)
        year = match.group(3)
        
        try:
            # Convert to datetime to validate and format as YYYY-MM-DD
            date = datetime(int(year), int(month), int(day))
            return date.strftime('%Y-%m-%d')
        except ValueError:
            print(f"  Warning: Invalid date in filename: {filename}")
            return None
    else:
        print(f"  Warning: No date found in filename: {filename}")
        return None



# ============================================
# PDFs in a specific folder
pdf_files = glob("../weekly-opcvm-scraper/data/weekly_opcvm/*.pdf")
# ============================================

print("=" * 70)
print("ATTIJARI DIVERSIFIE Data Extraction")
print("=" * 70)
print()


# Extract data from all files
all_data = []

for pdf_file in pdf_files:
    print(f"Processing: {pdf_file}")
    
    # Extract date from filename
    date = extract_date_from_filename(pdf_file)
    
    # Extract data from PDF
    data = extract_diversifie_data(pdf_file)
    
    if data:
        # Add Date column as the first column
        data['Date'] = date
        
        all_data.append(data)
        print(f"  ✓ Extracted: Date={date}, VL={data['Valeur Liquidative']}")
    else:
        print(f"  ✗ No data found")

# Save to CSV
if all_data:
    df = pd.DataFrame(all_data)
    
    # Reorder columns to put Date first
    cols = ['Date'] + [col for col in df.columns if col != 'Date']
    df = df[cols]
    
    # Sort by date
    df = df.sort_values('Date').reset_index(drop = True)
    
    # Save to CSV
    df.to_csv("DIVERSIFIE_ALL.csv", index=False, encoding='utf-8-sig')
    print(f"\n✓ Saved {len(all_data)} records to DIVERSIFIE_ALL.csv")
    print("\nData Preview:")
    print(df.to_string(index=False))
else:
    print("\n✗ No data extracted")



