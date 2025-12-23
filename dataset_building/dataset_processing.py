"""
Converted from `dataset_processing.ipynb`.
Prepares MASI and Attijari datasets, computes GARCH volatility and future 2-week volatility,
and writes `final_dataset.csv`.
"""
import os
import pandas as pd
import numpy as np
from arch import arch_model

# =====================================================
# Base directory (robust paths)
# =====================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def main():

    # =====================================================
    # File paths
    # =====================================================
    cleaned_file = os.path.join(BASE_DIR, 'MASI_cleaned.csv')
    output_masi = os.path.join(BASE_DIR, 'MASI_combined.csv')

    weekly_file = os.path.join(
        BASE_DIR,
        '..',
        'weekly-masi-scraper',
        'data',
        'weekly_masi',
        'weekly_masi_data.csv'
    )

    attijari_file = os.path.join(BASE_DIR, 'DIVERSIFIE_ALL.csv')
    attijari_out = os.path.join(BASE_DIR, 'attijari_diversifie.csv')

    final_out = os.path.join(BASE_DIR, 'final_dataset.csv')

    # =====================================================
    # Load / combine MASI
    # =====================================================
    if not os.path.exists(cleaned_file):
        raise FileNotFoundError(f"❌ MASI_cleaned.csv introuvable : {cleaned_file}")

    cleaned_df = pd.read_csv(cleaned_file, parse_dates=['Date'], dayfirst=True)
    cleaned_df["Date"] = pd.to_datetime(cleaned_df["Date"])

    if not os.path.exists(weekly_file):
        print(f"⚠️ Weekly MASI file not found: {weekly_file}")
        combined_MASI_df = cleaned_df.copy()
        

    else:
        weekly_df = pd.read_csv(weekly_file, parse_dates=['Date'], dayfirst=True)
        weekly_df["Date"] = pd.to_datetime(weekly_df["Date"]) - pd.Timedelta(days=2)
        # weekly_df["Variation %"] = weekly_df["Variation %"]*100  # Convert to percentage

        # Merge, keeping weekly_df values when dates match
        combined_MASI_df = pd.concat([cleaned_df, weekly_df], ignore_index=True)
        combined_MASI_df = combined_MASI_df.sort_values('Date').reset_index(drop=True)
        combined_MASI_df = combined_MASI_df.drop_duplicates(subset=['Date'], keep='last')
        
        # Recompute variation percentage
        combined_MASI_df['Variation %'] = (
            combined_MASI_df['weekly_mean'].pct_change() * 100
        )


    combined_MASI_df["Date"] = pd.to_datetime(combined_MASI_df["Date"])
    combined_MASI_df.to_csv(output_masi, index=False, encoding='utf-8')
    print(f"✅ MASI dataset saved: {output_masi}")

    # =====================================================
    # Process Attijari dataset
    # =====================================================
    if not os.path.exists(attijari_file):
        raise FileNotFoundError(f"❌ Attijari file introuvable : {attijari_file}")

    attijari = pd.read_csv(attijari_file, parse_dates=['Date'])

    # Drop unused columns if present
    for col in ['Fonds', 'Horizon minimum conseillé']:
        if col in attijari.columns:
            attijari.drop(columns=[col], inplace=True)

    columns_to_clean = [
        "Performances glissantes Depuis Début d'année",
        "Performances glissantes 1 semaine",
        "Performances glissantes 6 mois",
        "Performances glissantes 1 an",
        "Performances glissantes 2 ans",
        "Performances glissantes 3 ans",
        "Performances glissantes 5 ans",
    ]

    for col in columns_to_clean:
        if col in attijari.columns:
            attijari[col] = (
                attijari[col]
                .astype(str)
                .str.replace('%', '', regex=False)
                .str.replace(',', '.', regex=False)
            )
            attijari[col] = pd.to_numeric(attijari[col], errors='coerce')

    attijari.to_csv(attijari_out, index=False)
    print(f"✅ Attijari cleaned dataset saved: {attijari_out}")

    # =====================================================
    # Merge datasets
    # =====================================================
    df_merged = pd.merge(attijari, combined_MASI_df, on='Date', how='inner')

    # =====================================================
    # Feature engineering
    # =====================================================
    for lag in range(1, 3):
        df_merged[f'rendement_lag_{lag}'] = (
            df_merged['Performances glissantes 1 semaine'].shift(lag)
        )

    df_lagged = df_merged.copy()

    # Weekly returns in decimal
    df_lagged['returns'] = df_lagged['Performances glissantes 1 semaine'] / 100

    returns = df_lagged['returns'].dropna()

    if returns.var() == 0:
        raise ValueError("❌ Returns variance is zero → GARCH cannot be fitted")

    # =====================================================
    # GARCH (1,1)
    # =====================================================
    garch = arch_model(
        returns,
        mean='Constant',
        vol='GARCH',
        p=1,
        q=1,
        dist='normal'
    )

    garch_result = garch.fit(disp='off')

    df_lagged.loc[returns.index, 'garch_vol'] = (
        garch_result.conditional_volatility
    )

    df_lagged['garch_vol_lag_1'] = df_lagged['garch_vol'].shift(1)
    df_lagged['garch_vol_lag_2'] = df_lagged['garch_vol'].shift(2)

    # =====================================================
    # Future 2-week volatility (RMS of next 2 weekly returns)
    # =====================================================
    future_sq_returns = (
        df_lagged['returns'].shift(-1) ** 2 +
        df_lagged['returns'].shift(-2) ** 2
    )

    df_lagged['vol_future_2w'] = np.sqrt(future_sq_returns / 2)

    df_lagged['vol_future_2w_1'] = df_lagged['vol_future_2w'].shift(1)
    df_lagged['vol_future_2w_2'] = df_lagged['vol_future_2w'].shift(2)
    df_lagged['vol_future_2w_3'] = df_lagged['vol_future_2w'].shift(3)

    # =====================================================
    # Final cleanup
    # =====================================================
    #df_lagged = df_lagged.dropna().reset_index(drop=True)

    df_lagged.to_csv(final_out, index=False)
    print(f"🚀 Final dataset saved: {final_out} (rows: {len(df_lagged)})")


if __name__ == '__main__':
    main()
