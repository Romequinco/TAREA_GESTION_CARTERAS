import pandas as pd

# Explorar el archivo Excel
excel_file = pd.ExcelFile('data/prod_long_sharpe_u60_20260125_v1_train_dataset.csv')

print("Hojas disponibles:")
print(excel_file.sheet_names)
print()

for sheet in excel_file.sheet_names:
    print("="*80)
    print(f"Hoja: {sheet}")
    print("="*80)
    df = pd.read_excel('data/prod_long_sharpe_u60_20260125_v1_train_dataset.csv', sheet_name=sheet)
    print(f"Shape: {df.shape}")
    print(f"Columnas: {df.columns.tolist()}")
    print(f"\nPrimeras 2 filas:")
    print(df.head(2))
    print()
