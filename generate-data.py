import numpy as np
import pandas as pd

# -----------------------------
# trading_synthetic.py - versão mais simples e direta
# -----------------------------

np.random.seed(42)

# -----------------------------
# PERÍODO (SEMANAL)
# -----------------------------
dates = pd.date_range(start="2023-01-01", end="2026-12-31", freq="W")
n = len(dates)

df = pd.DataFrame({"date": dates})

# -----------------------------
# COMPONENTE DE CRESCIMENTO (CARTEIRA)
# -----------------------------
growth_curve = np.linspace(1.0, 2.5, n)  # crescimento estrutural forte

# -----------------------------
# SAZONALIDADE AGRÍCOLA
# -----------------------------
month = df["date"].dt.month

soy_season = np.where(month.isin([1, 2, 3, 4, 5]), 1.3, 0.9)
corn_season = np.where(month.isin([6, 7, 8, 9]), 1.25, 0.95)
sugar_season = np.where(month.isin([10, 11, 12]), 1.2, 0.97)
cotton_season = np.where(month.isin([3, 4, 5, 9]), 1.15, 0.98)

seasonality_index = (soy_season + corn_season + sugar_season + cotton_season) / 4

# -----------------------------
# ÍNDICE DE MERCADO (VOLATILIDADE)
# -----------------------------
market_index = 100 + np.cumsum(np.random.normal(0, 0.8, n))

market_factor = market_index / np.mean(market_index)

# -----------------------------
# PRODUTOS (MIX)
# -----------------------------
product_mix = np.random.choice(["origination", "export", "barter"], size=n, p=[0.6, 0.25, 0.15])

product_factor = np.where(product_mix == "origination", 1.0, np.where(product_mix == "export", 1.4, 0.9))

# -----------------------------
# BASE DE CLIENTES
# -----------------------------
clients = (500 * growth_curve * np.random.normal(1, 0.05, n)).astype(int)

# -----------------------------
# CONTRATOS (TARGET PRINCIPAL)
# -----------------------------
base_contracts = clients * 4.2 * seasonality_index * market_factor * product_factor * np.random.normal(1, 0.08, n)

df["clients"] = clients
df["product"] = product_mix
df["market_index"] = market_index
df["contracts"] = base_contracts.astype(int)

# -----------------------------
# DERIVAÇÕES OPERACIONAIS
# -----------------------------

# NF por contrato varia por produto
nf_factor = df["product"].map({"origination": 2.5, "export": 5.8, "barter": 3.1})

df["nf_volume"] = (df["contracts"] * nf_factor).astype(int)

# toneladas por contrato
ton_factor = df["product"].map({"origination": 180, "export": 850, "barter": 220})

df["tons"] = (df["contracts"] * ton_factor).astype(int)

# -----------------------------
# EXPORT
# -----------------------------
df.to_csv("data/raw/trading_synthetic.csv", index=False)

print("Dataset gerado com sucesso:", df.shape)



# -----------------------------
# trading_synthetic_v2.py - versão mais complexa e realista
# -----------------------------

np.random.seed(42)

# -----------------------------
# PERÍODO SEMANAL
# -----------------------------
dates = pd.date_range(start="2023-01-01", end="2026-12-31", freq="W")
n = len(dates)

df = pd.DataFrame({"date": dates})

month = df["date"].dt.month

# -----------------------------
# CRESCIMENTO DE CARTEIRA
# -----------------------------
growth = np.linspace(1.0, 2.6, n)
clients = (500 * growth * np.random.normal(1, 0.06, n)).astype(int)

# -----------------------------
# COMMODITIES (PREÇO SIMULADO)
# -----------------------------
def random_walk(start, vol):
    return start + np.cumsum(np.random.normal(0, vol, n))

soy_price = random_walk(130, 1.5)
corn_price = random_walk(90, 1.2)
sugar_price = random_walk(22, 0.3)
cotton_price = random_walk(85, 1.0)

# -----------------------------
# FX (USD/BRL)
# -----------------------------
usd_brl = random_walk(5.0, 0.02)

# -----------------------------
# VOLATILIDADE (proxy de stress)
# -----------------------------
vol_soy = np.abs(np.random.normal(0.02, 0.01, n))
vol_corn = np.abs(np.random.normal(0.025, 0.012, n))

# -----------------------------
# SAZONALIDADE AGRÍCOLA
# -----------------------------
soy_season = np.where(month.isin([1,2,3,4,5]), 1.3, 0.9)
corn_season = np.where(month.isin([6,7,8,9]), 1.25, 0.95)
sugar_season = np.where(month.isin([10,11,12]), 1.2, 0.97)
cotton_season = np.where(month.isin([3,4,5,9]), 1.15, 0.98)

seasonality = (soy_season + corn_season + sugar_season + cotton_season) / 4

# -----------------------------
# PRODUTO + COMMODITY + TIPO OPERAÇÃO
# -----------------------------
product_type = np.random.choice(
    ["origination", "export", "barter"],
    size=n,
    p=[0.55, 0.30, 0.15]
)

commodity = np.random.choice(
    ["soy", "corn", "sugar", "cotton"],
    size=n,
    p=[0.45, 0.30, 0.15, 0.10]
)

operation_type = np.random.choice(
    ["spot", "future", "hedge"],
    size=n,
    p=[0.4, 0.35, 0.25]
)

# -----------------------------
# EFEITOS ECONÔMICOS
# -----------------------------
commodity_price = np.select(
    [
        commodity == "soy",
        commodity == "corn",
        commodity == "sugar",
        commodity == "cotton"
    ],
    [soy_price, corn_price, sugar_price, cotton_price]
)

price_effect = commodity_price / np.mean(commodity_price)

fx_effect = usd_brl / np.mean(usd_brl)

vol_effect = 1 + (vol_soy + vol_corn)

product_effect = np.select(
    [
        product_type == "origination",
        product_type == "export",
        product_type == "barter"
    ],
    [1.0, 1.35, 0.9]
)

operation_effect = np.select(
    [
        operation_type == "spot",
        operation_type == "future",
        operation_type == "hedge"
    ],
    [1.0, 1.2, 1.15]
)

# -----------------------------
# CONTRATOS (TARGET)
# -----------------------------
base = clients * 4.0

contracts = (
    base
    * seasonality
    * price_effect
    * fx_effect
    * vol_effect
    * product_effect
    * operation_effect
    * np.random.normal(1, 0.07, n)
)

# -----------------------------
# DATAFRAME FINAL
# -----------------------------
df["clients"] = clients
df["product_type"] = product_type
df["commodity"] = commodity
df["operation_type"] = operation_type

df["soy_price"] = soy_price
df["corn_price"] = corn_price
df["sugar_price"] = sugar_price
df["cotton_price"] = cotton_price

df["usd_brl"] = usd_brl
df["vol_soy"] = vol_soy
df["vol_corn"] = vol_corn

df["contracts"] = contracts.astype(int)

# -----------------------------
# DERIVAÇÕES OPERACIONAIS
# -----------------------------

nf_factor = np.select(
    [
        product_type == "origination",
        product_type == "export",
        product_type == "barter"
    ],
    [2.5, 5.8, 3.1]
)

ton_factor = np.select(
    [
        product_type == "origination",
        product_type == "export",
        product_type == "barter"
    ],
    [180, 850, 220]
)

df["nf_volume"] = (df["contracts"] * nf_factor).astype(int)
df["tons"] = (df["contracts"] * ton_factor).astype(int)

# -----------------------------
# EXPORT
# -----------------------------
df.to_csv("data/raw/trading_synthetic_v2.csv", index=False)

print("Dataset V2 gerado:", df.shape)
