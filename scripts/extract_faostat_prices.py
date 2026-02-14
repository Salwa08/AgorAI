"""
Extract Morocco producer prices from FAOSTAT bulk download.
Source: FAO FAOSTAT Producer Prices (https://www.fao.org/faostat/en/#data/PP)
Downloaded: Africa bulk data, last updated January 9, 2026.
License: CC BY 4.0
"""
import pandas as pd

# Load FAOSTAT data (wide format: Y1991..Y2025)
df = pd.read_csv('datasets/faostat_prices/Prices_E_Africa_NOFLAG.csv',encoding='latin1')

# Filter Morocco
ma = df[df['Area'] == 'Morocco'].copy()
print(f'Morocco rows: {len(ma)}')
print(f'Items: {ma["Item"].nunique()} unique items')
print(f'Elements: {ma["Element"].unique()}')
print()

# Year columns
year_cols = [c for c in ma.columns if c.startswith('Y') and c[1:].isdigit()]
years = sorted([int(c[1:]) for c in year_cols])
print(f'Year range: {min(years)} - {max(years)}')
print()

# Get latest USD/tonne prices
usd = ma[ma['Element'] == 'Producer Price (USD/tonne)'].copy()

results_usd = []
for _, row in usd.iterrows():
    item = row['Item']
    for yr in reversed(years):
        val = row.get(f'Y{yr}')
        if pd.notna(val):
            results_usd.append({'Item': item, 'Year': yr, 'USD_per_tonne': val})
            break

results_usd = pd.DataFrame(results_usd).sort_values('USD_per_tonne', ascending=False)
print('=== FAOSTAT Morocco Producer Prices (USD/tonne) — Latest Available ===')
for _, row in results_usd.iterrows():
    print(f"  {row['Item']:<45} {int(row['Year'])}  {row['USD_per_tonne']:>10.2f} USD/t")

print()

# Get latest LCU/tonne prices (MAD/tonne)
lcu = ma[ma['Element'] == 'Producer Price (LCU/tonne)'].copy()

results_lcu = []
for _, row in lcu.iterrows():
    item = row['Item']
    for yr in reversed(years):
        val = row.get(f'Y{yr}')
        if pd.notna(val):
            results_lcu.append({'Item': item, 'Year': yr, 'MAD_per_tonne': val})
            break

results_lcu = pd.DataFrame(results_lcu).sort_values('MAD_per_tonne', ascending=False)
print('=== FAOSTAT Morocco Producer Prices (MAD/tonne) — Latest Available ===')
for _, row in results_lcu.iterrows():
    print(f"  {row['Item']:<45} {int(row['Year'])}  {row['MAD_per_tonne']:>10.0f} MAD/t")

# Map to our crop names
print()
print('=== MAPPING to our crops.json ===')
mapping = {
    'Wheat': 'soft_wheat',
    'Barley': 'barley',
    'Chick peas, dry': 'chickpeas',
    'Lentils, dry': 'lentils',
    'Broad beans and horse beans, dry': 'fava_beans',
    'Olives': 'olives',
    'Oranges': 'citrus',
    'Potatoes': 'potatoes',
    'Tomatoes': 'tomatoes',
    'Dates': 'date_palms',
    'Almonds, in shell': 'almonds',
    'Watermelons': 'watermelon',
    'Sugar beet': 'sugar_beet',
    'Sugar cane': 'sugarcane',
    'Sunflower seed': 'sunflower',
    'Grapes': 'grapes',
    'Bananas': 'bananas',
    'Avocados': 'avocados',
    'Rice, paddy (rice milled equivalent)': 'rice',
    'Rice, paddy': 'rice',
    'Green beans and runner beans': 'green_beans',
    'Beans, green': 'green_beans',
    'Sorghum': 'sorghum',
}

for fao_name, our_name in sorted(mapping.items(), key=lambda x: x[1]):
    usd_row = results_usd[results_usd['Item'] == fao_name]
    lcu_row = results_lcu[results_lcu['Item'] == fao_name]
    
    usd_val = f"{usd_row.iloc[0]['USD_per_tonne']:.0f}" if len(usd_row) > 0 else "N/A"
    usd_yr = f"{int(usd_row.iloc[0]['Year'])}" if len(usd_row) > 0 else ""
    lcu_val = f"{lcu_row.iloc[0]['MAD_per_tonne']:.0f}" if len(lcu_row) > 0 else "N/A"
    lcu_yr = f"{int(lcu_row.iloc[0]['Year'])}" if len(lcu_row) > 0 else ""
    
    print(f"  {our_name:<20} <- {fao_name:<45} USD: {usd_val:>6} ({usd_yr})  MAD: {lcu_val:>8} ({lcu_yr})")
