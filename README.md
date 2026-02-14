# 🌾 FarmSwarm: Network-based Collective Intelligence for Smart Agriculture

A professional, production-ready agent-based model (ABM) for simulating farmer decision-making strategies in Morocco's agricultural system.

## 📋 Overview

This project models **100 farmers** making crop choices over **multiple seasons**, comparing two learning strategies:
- **INDIVIDUAL**: Farmers make decisions based solely on ecological suitability
- **SHARED**: Farmers adapt based on both ecology AND community yields

The simulation answers: **Does knowledge-sharing improve farming outcomes?**

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Simulation (Jupyter)

```bash
jupyter notebook simulation.ipynb
```

Execute cells in order:
1. **Load Data & Config** - Initializes system from `config.yaml`
2. **Define Classes** - Zone, FarmerAgent, FarmModel
3. **Run Simulation** - 10 timesteps × 100 farmers
4. **Analyze Results** - Generate plots and metrics

### 3. (Optional) Launch Interactive Dashboard

After running the simulation, start the Solara web dashboard:

```bash
solara run dashboard_solara.py
```

Then open: `http://localhost:8000`

## 📁 Project Structure

```
AgroAI/
├── simulation.ipynb              # Main simulation notebook
├── config.yaml                   # Configuration parameters
├── dashboard_solara.py           # Interactive web dashboard
├── requirements.txt              # Python dependencies
├── README.md                     # This file
│
├── data/                         # Input data
│   ├── zones.json               # Geographic zones (5 zones)
│   ├── crops.json               # Crop parameters (23 crops)
│   ├── climate_profiles.json    # Monthly climate data per zone
│   ├── soil_moisture_profiles.json
│   └── morocco_soilmoisture.csv
│
├── utils/                        # Utility modules
│   ├── config.py                # Configuration loader
│   ├── logger.py                # Logging setup
│   └── __init__.py
│
├── results/                      # Output files (auto-generated)
│   ├── agents_results.csv       # All agent data
│   ├── metrics.json             # Key metrics
│   ├── summary_report.txt       # Text summary
│   ├── simulation_config.yaml   # Configuration backup
│   └── *.png                    # Visualization plots
│
└── logs/                         # Log files (auto-generated)
    └── simulation.log
```

## ⚙️ Configuration

Edit `config.yaml` to customize simulation parameters:

```yaml
simulation:
  n_agents: 100              # Number of farmers
  n_timesteps: 10            # Simulation steps
  random_seed: 42            # For reproducibility

suitability:
  zone_weight: 0.4           # Importance of zone match
  soil_weight: 0.25          # Importance of soil type
  climate_weight: 0.25       # Importance of climate

learning:
  individual_weight: 0.5     # Personal knowledge weight
  shared_weight: 0.5         # Community knowledge weight

yield:
  variability_min: 0.8       # Min yield multiplier
  variability_max: 1.2       # Max yield multiplier
```

## 📊 Output & Results

### Generated Files

**Automatic outputs in `./results/`:**

| File | Description |
|------|-------------|
| `agents_results.csv` | Complete agent data (yield, profit, strategy, zone) |
| `metrics.json` | Key performance indicators |
| `summary_report.txt` | Human-readable summary |
| `01_strategy_comparison.png` | Boxplots comparing strategies |
| `02_distribution_analysis.png` | Violin plots of distributions |
| `03_zone_performance.png` | Yield by geographic zone |
| `04_strategy_by_zone.png` | Strategy adoption patterns |
| `simulation_config.yaml` | Config used for run |

## 🔍 How It Works

### Farmer Decision Process

1. **Evaluate suitability** for each viable crop:
   - Zone compatibility (40%)
   - Soil type match (25%)
   - Climate fit: temperature & rainfall (25%)

2. **Choose best crop** based on strategy:
   - **INDIVIDUAL**: Trust own calculation
   - **SHARED**: Blend personal score (50%) + community results (50%)

3. **Harvest & Learn**:
   - Produce yield based on suitability
   - SHARED farmers update community knowledge
   - Next season uses updated knowledge

### Key Features

✅ **Configuration-Driven** - All parameters in YAML  
✅ **Reproducible** - Fixed random seed  
✅ **Logged** - Complete audit trail  
✅ **Professional** - Production-ready code structure  
✅ **Real Data** - Based on FAO/GAEZ sources  
✅ **Beautiful Plots** - Publication-quality visualizations  
✅ **Interactive Dashboard** - Solara web interface  
✅ **Persistent Results** - Automatic saving  

## 🎯 Interpreting Results

**SHARED > INDIVIDUAL:**
- Knowledge-sharing improves farming outcomes
- Community learning accelerates adaptation
- Recommendation: Strengthen farmer networks

**INDIVIDUAL > SHARED:**
- Local conditions are most important
- Farmers learn best through personal experience
- Recommendation: Personalize extension services

**SHARED ≈ INDIVIDUAL:**
- Both strategies valuable in different contexts
- Benefits depend on geography, crop type
- Recommendation: Hybrid approach

## 📚 Data Sources

- **Crops Data**: FAO EcoCrop Database + FAOSTAT (2018-2022)
- **Climate**: Copernicus Climate Data Store
- **Zones**: Agricultural zones of Morocco
- **Soil**: Global soil databases + local surveys

## 🔧 Extending

### Add New Parameters

1. Update `config.yaml`
2. Access via: `config.suitability.get("zone_weight")`
3. No code changes needed!

### Add Environmental Stressors

```yaml
yield:
  drought_probability: 0.15
  flood_probability: 0.08
  pest_pressure: 0.4
```

### Run Scenarios

Create multiple config files and run simulations:
```bash
# baseline
jupyter notebook simulation.ipynb

# drought scenario
cp config.yaml config_drought.yaml
# Edit config_drought.yaml
# Then load: config = load_config("config_drought.yaml")
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `config.yaml not found` | Run from AgroAI directory: `cd d:\AgroAI\AgorAI` |
| `No module utils` | Cell 1 adds utils to path (already done) |
| Dashboard won't start | Install: `pip install solara solara-plotly` |
| Missing climate data | Verify all `.json` files in `./data/` |

## 📞 Support

- Check logs: `logs/simulation.log`
- Review results: `results/summary_report.txt`
- Adjust config and re-run

## 📄 License

Research & Educational Use

---

**Created 2026 | Agricultural Simulation Project** 🌾
