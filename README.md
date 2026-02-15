# AgroAI — Agent-Based Agricultural Simulation for Morocco

An agent-based model (ABM) built with [Mesa](https://mesa.readthedocs.io/) that simulates farmer decision-making across Morocco's agro-ecological zones. The simulation compares **cooperative (SHARED)** and **individual (INDIVIDUAL)** farming strategies using real-world data from FAO, Copernicus, and NASA POWER.

## Research Question

> Does cooperative knowledge-sharing between farmers improve crop yields and profitability compared to individual decision-making?

## Key Features

- **100 paired agents** (50 SHARED + 50 INDIVIDUAL) across 6 agro-ecological zones
- **24 crops** with FAO EcoCrop suitability and category-based pricing
- **Real cost model**: zone-specific water tariffs, crop water needs, labor
- **Climate data**: NASA POWER temperature and precipitation per zone
- **Soil moisture**: Copernicus C3S root-zone soil moisture
- **Social network**: NetworkX-based knowledge propagation (small-world, random, scale-free)
- **Interactive dashboard**: Solara web interface

## Quick Start

```bash
pip install -r requirements.txt
```

Open `simulation.ipynb` in Jupyter or VS Code and run all cells:

| Cell | Purpose |
|------|---------|
| 0 | Imports |
| 1 | SIM_CONFIG, data loading, model classes (Zone, FarmerAgent, FarmModel) |
| 2 | Run simulation and print results |
| 3 | Visualization and CSV export |

Optional — launch the interactive dashboard:

```bash
solara run dashboard_solara.py
```

## Project Structure

```
├── simulation.ipynb              # Main simulation notebook
├── simulation_v2.ipynb           # Extended version (same core logic)
├── dashboard_solara.py           # Solara web dashboard
├── requirements.txt
│
├── data/                         # Input data
│   ├── crops.json
│   ├── zones.json
│   ├── climate_profiles.json
│   └── soil_moisture_profiles.json
│
├── scripts/                      # Data preparation utilities
│   ├── fetch_climate_data.py
│   ├── update_crops_faostat.py
│   └── extract_faostat_prices.py
│
├── Extract_morocco_data.ipynb   # Copernicus NetCDF → soil moisture JSON
├── results/                      # Auto-generated outputs
└── logs/
```

## How It Works

### Crop Selection

Each farmer scores viable crops using ecological suitability (zone, soil, climate, moisture) plus optional bonuses:

- **SHARED**: zone-level yields, neighbor knowledge, own experience
- **INDIVIDUAL**: own suitability and experience only

### Economics

SHARED farmers get +20% price premium, 30% cost reduction, and 5% post-harvest loss vs 15% for individuals. Profit = `(yield × price − cost) × land_size`.

### Learning

After each season, SHARED farmers update zone-level knowledge and propagate results through the social network. Over 30 seasons, cooperative strategies converge on better crop choices.

## Configuration

Parameters are defined in the `SIM_CONFIG` dataclass inside the notebook. Key settings: `n_agents`, `n_seasons`, `shared_strategy`, `use_neighbor_graph`, suitability weights, and cooperative economics.

## Data Sources

| Dataset | Source |
|---------|--------|
| Crop suitability | FAO EcoCrop |
| Climate | NASA POWER |
| Soil moisture | Copernicus C3S |
| Zones, water tariffs | Morocco agricultural data |

## Data Preparation

Scripts in `scripts/` were used to build the JSON files in `data/`. Re-run only when updating source data:

```bash
python scripts/fetch_climate_data.py --start 1991 --end 2020
python scripts/update_crops_faostat.py
```

Copernicus soil moisture: see `Extract_morocco_data.ipynb`.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run from project root; restart kernel |
| Dashboard won't start | `pip install solara solara-plotly` |
| Missing data | Ensure all `.json` files exist in `data/` |

## License

Research and educational use.
