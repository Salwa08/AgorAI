# AgroAI — Agent-Based Agricultural Simulation for Morocco

An agent-based model (ABM) built with [Mesa](https://mesa.readthedocs.io/) that simulates farmer decision-making across Morocco's agro-ecological zones. The simulation compares **cooperative (SHARED)** and **individual (INDIVIDUAL)** farming strategies using real-world data from FAOSTAT, NASA POWER, Copernicus, SMAG, and ORMVA.

## Research Question

> Does cooperative knowledge-sharing between farmers improve crop yields and profitability compared to individual decision-making?

## Key Features

- **100 paired agents** (50 SHARED + 50 INDIVIDUAL twins) across 6 agro-ecological zones
- **24 real crops** with FAOSTAT Morocco producer prices (MAD/tonne)
- **Real cost model**: SMAG labor wages (84.37 MAD/day), ORMVA irrigation tariffs, OCP fertilizer prices
- **Climate data**: NASA POWER satellite-derived temperature, precipitation, humidity per zone
- **Soil moisture**: Copernicus C3S root-zone soil moisture (RZSM) dekadal data
- **EcoCrop suitability**: Temperature and precipitation ranges from FAO EcoCrop database
- **Social network**: NetworkX-based knowledge propagation (small-world, scale-free, random)
- **Interactive dashboard**: Solara web interface with map, charts, and data explorer

## Quick Start

```bash
pip install -r requirements.txt
```

Open `simulation_v2_final.ipynb` in Jupyter or VS Code and run all cells:

| Cell | Purpose |
|------|---------|
| 1 | Imports and `config.yaml` integration |
| 2 | Data loading, classes (`Zone`, `FarmerAgent`, `FarmModel`), simulation logic |
| 3 | Run simulation and print results |
| 4 | Visualization (matplotlib/seaborn plots) and CSV export |

Optional — launch the interactive dashboard:

```bash
solara run dashboard_solara.py
```

## Project Structure

```
├── simulation_v2_final.ipynb       # Main simulation notebook
├── config.yaml                     # All simulation parameters
├── dashboard_solara.py             # Solara web dashboard
├── requirements.txt                # Python dependencies
│
├── data/                           # Processed input data (used by simulation)
│   ├── crops.json                  # 24 crops: FAOSTAT prices, EcoCrop params, cost model
│   ├── zones.json                  # 6 zones: soil, viable crops, ORMVA water tariffs
│   ├── climate_profiles.json       # NASA POWER annual/monthly climate per zone
│   └── soil_moisture_profiles.json # Copernicus RZSM statistics per zone
│
├── datasets/                       # Raw source datasets
│   └── copernicus/                 # C3S RZSM NetCDF files (2021 dekadal)
│
├── scripts/                        # Data preparation utilities
│   ├── fetch_climate_data.py       # Download NASA POWER data → climate_profiles.json
│   ├── update_crops_faostat.py     # Embed FAOSTAT prices into crops.json
│   └── extract_faostat_prices.py   # Parse FAOSTAT bulk CSV (one-time use)
│
├── Extract_morocco_data.ipynb      # Copernicus NetCDF → soil_moisture_profiles.json
│
├── utils/                          # Shared modules
│   ├── config.py                   # YAML config loader
│   └── logger.py                   # Logging setup
│
├── results/                        # Auto-generated outputs
│   ├── agents_results.csv          # Full agent-level data
│   ├── season_history.csv          # Per-season aggregates
│   ├── strategy_comparison.csv     # SHARED vs INDIVIDUAL summary
│   ├── metrics.json                # Key performance indicators
│   └── summary_report.txt          # Human-readable summary
│
└── logs/
    └── simulation.log
```

## How It Works

### 1. Crop Selection

Each farmer scores every viable crop using a weighted suitability function:

| Factor | Weight | Source |
|--------|--------|--------|
| Zone compatibility | 40% | `zones.json` — viable crops list |
| Soil type match | 25% | `zones.json` — dominant soil vs crop ideal soils |
| Climate fit | 25% | `climate_profiles.json` vs EcoCrop temp/precip ranges |
| Soil moisture | 10% | `soil_moisture_profiles.json` vs crop moisture preference |

**SHARED** farmers additionally incorporate cooperative zone-level yields and neighbor knowledge via the social network. **INDIVIDUAL** farmers rely only on their own suitability scores and personal memory.

### 2. Harvest & Economics

- **Yield**: `base_yield × zone_viability × soil_match × variability`
- **Cost**: Itemized from `crops.json` cost model (labor + water + fertilizer + seeds + mechanization)
- **Revenue**: `(yield × (1 - post_harvest_loss)) × FAOSTAT_price × price_volatility`
- **Profit**: `revenue - total_cost`

SHARED farmers get a **+20% price premium** (cooperative marketing), **30% lower costs** (bulk purchasing), and **5% post-harvest loss** (shared storage) vs 15% for individuals.

### 3. Learning

After each season, SHARED farmers update zone-level knowledge pools and propagate results through the social network. Over 30 seasons, cooperative strategies converge on better crop choices.

## Configuration

All parameters are centralized in `config.yaml`:

```yaml
simulation:
  n_agents: 100
  n_timesteps: 30
  random_seed: 42

suitability:
  zone_weight: 0.4
  soil_weight: 0.25
  climate_weight: 0.25
  moisture_weight: 0.1

finance:
  price_volatility: 0.15
  shared_price_premium: 0.20
  shared_cost_efficiency: 0.70
  shared_post_harvest_loss: 0.05
  individual_post_harvest_loss: 0.15
```

See [config.yaml](config.yaml) for the full parameter list.

## Data Sources

| Dataset | Source | License |
|---------|--------|---------|
| Crop prices (MAD/tonne) | [FAOSTAT Producer Prices](https://www.fao.org/faostat/en/#data/PP) — Morocco | CC BY-4.0 |
| Crop suitability ranges | [FAO EcoCrop](https://gaez.fao.org/pages/ecocrop) | Open |
| Climate profiles | [NASA POWER](https://power.larc.nasa.gov/) — Agroclimatology | Open |
| Soil moisture | [Copernicus C3S](https://cds.climate.copernicus.eu/) — SM2RAIN-ASCAT RZSM | Copernicus License |
| Labor wages | SMAG — Moroccan Labor Code, Decree 2.23.993 (2024) | Public |
| Water tariffs | ORMVA official tariffs — Bulletin Officiel | Public |
| Fertilizer prices | OCP Group — Morocco domestic market | Public |

## Data Preparation Scripts

These scripts were used to build the JSON files in `data/`. They do not need to be re-run unless updating source data:

```bash
# Fetch NASA POWER climate data for all 6 zones
python scripts/fetch_climate_data.py --start 1991 --end 2020

# Update crops.json with latest FAOSTAT prices + cost model
python scripts/update_crops_faostat.py
```

The Copernicus soil moisture data was processed via [`Extract_morocco_data.ipynb`](Extract_morocco_data.ipynb).

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `config.yaml not found` | Run from project root directory |
| `ModuleNotFoundError: utils` | Cell 1 adds the path automatically — restart kernel |
| Dashboard won't start | `pip install solara solara-plotly` |
| Missing data files | Ensure all `.json` files exist in `data/` |

Check `logs/simulation.log` for detailed execution logs.

## License

Research and educational use.