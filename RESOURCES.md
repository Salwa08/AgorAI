# FarmSwarm — Resources & Literature

Complete bibliography of data sources, frameworks, and literature used in this project.

---

## 1. Framework & Methodology

### Agent-Based Modeling


| Resource                                  | Description                             | Link                                                              |
| ----------------------------------------- | --------------------------------------- | ----------------------------------------------------------------- |
| **Mesa**                                  | ABM framework for Python                | [mesa.readthedocs.io](https://mesa.readthedocs.io/)               |
| Kazil, J., Masad, D., & Crooks, A. (2015) | Mesa: An Agent-Based Modeling Framework | [SciPy Proceedings](https://doi.org/10.25080/Majora-7b98e3ed-009) |


### Social Networks


| Resource     | Description                      | Link                                  |
| ------------ | -------------------------------- | ------------------------------------- |
| **NetworkX** | Graph/network library for Python | [networkx.org](https://networkx.org/) |


### Related ABM Studies (Methodology)


| Resource                   | Description                                                      | Link                                                                                                |
| -------------------------- | ---------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Alotibi, Y.S. (2025)       | AdoptAgriSim: Socio-technical ABM for smart agriculture adoption | [Nature Scientific Reports](https://www.nature.com/articles/s41598-025-27523-7)                     |
| PLOS Computational Biology | Coupled information diffusion–pest dynamics, farmer cooperation  | [journals.plos.org](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1002222) |


---

## 2. Data Sources

### Crop & Ecological Data


| Resource                    | Use in Project                                                  | Link                                                                                         |
| --------------------------- | --------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| **FAO EcoCrop Database**    | Crop suitability, ecological requirements (temp, precip, soils) | [ecocrop.fao.org](http://ecocrop.fao.org/ecocrop/srv/en/home)                                |
| **OpenCLIM/ecocrop**        | EcoCrop CSV data                                                | [github.com/OpenCLIM/ecocrop](https://github.com/OpenCLIM/ecocrop)                           |
| **FAOSTAT Crop Production** | Yield baselines (Morocco, 2018–2022)                            | [fao.org/faostat](https://www.fao.org/faostat/)                                              |
| **FAOSTAT Producer Prices** | Market prices (MAD/tonne), Morocco                              | [fao.org/faostat/en/#data/PP](https://www.fao.org/faostat/en/#data/PP)                       |
| **FAO Crop Information**    | Crop descriptions                                               | [fao.org/land-water](https://www.fao.org/land-water/databases-and-software/crop-information) |
| Allen et al. (1998)         | FAO Irrigation & Drainage Paper 56 — water requirements         | —                                                                                            |


### Climate & Environment


| Resource                         | Use in Project                                                                       | Link                                                                                     |
| -------------------------------- | ------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| **NASA POWER**                   | Temperature and precipitation per zone                                               | [power.larc.nasa.gov](https://power.larc.nasa.gov/)                                      |
| **ERA5**                         | Alternative reanalysis climate data (zones reference)                                | [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/)                      |
| **Copernicus C3S Soil Moisture** | Root-zone soil moisture → `morocco_soilmoisture.csv` → `soil_moisture_profiles.json` | [Climate Data Store](https://cds.climate.copernicus.eu/datasets/satellite-soil-moisture) |


### Morocco-Specific Data


| Resource                                      | Use in Project                                               | Link                                       |
| --------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------ |
| **SMAG (Minimum Agricultural Wage)**          | Labor costs — 84.37 MAD/day (Decree 2.23.993)                | [emploi.gov.ma](https://www.emploi.gov.ma) |
| **ORMVA**                                     | Water tariffs (Offices Régionaux de Mise en Valeur Agricole) | —                                          |
| **OCP Group**                                 | Fertilizer costs (domestic prices)                           | —                                          |
| **SONACOS**                                   | Seed costs (Morocco seed market)                             | —                                          |
| **Regional agricultural cooperatives survey** | Mechanization costs by crop category                         | —                                          |
| **Morocco Agricultural Ministry**             | Zones, agricultural data                                     | —                                          |


### Zone Classification


| Resource            | Use in Project                      | Link                                       |
| ------------------- | ----------------------------------- | ------------------------------------------ |
| Emberger, L. (1955) | Bioclimatic stages for North Africa | UNESCO, Plant Ecology: Reviews of Research |


---

## 3. Cooperative Economics Parameter Calibration

### Price Premium


| Resource                   | Finding                                                  | Range / Value                                                                                                                    |
| -------------------------- | -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| PCNS (2023)                | Cooperative price effects                                | ~7–19% (cereals, argan)                                                                                                          |
| Dugué et al. (2019)        | —                                                        | —                                                                                                                                |
| Ibourk & El Aynaoui (2023) | Cooperative sustainability in Morocco                    | [MDPI Sustainability 15(4):3460](https://www.mdpi.com/2071-1050/15/4/3460)                                                       |
| UNCTAD (2022)              | Primary producer prices and cooperatives — cross-country | [unctad.org](https://unctad.org/publication/primary-producer-sales-prices-and-cooperatives-cross-country-multi-product-analysis) |


### Cost Reduction


| Resource             | Finding                    | Range / Value |
| -------------------- | -------------------------- | ------------- |
| FAO (2019)           | Input cost savings         | ~6–20%        |
| PCNS (2023)          | Subsidies, bulk purchasing | —             |
| Kassam et al. (2017) | —                          | —             |
| Extension studies    | Bulk purchasing savings    | ~14% average  |


### Post-Harvest Loss


| Resource              | Finding                           | Range / Value                                  |
| --------------------- | --------------------------------- | ---------------------------------------------- |
| Bartali et al. (2022) | Storage/consumption losses        | 1.6–12%                                        |
| IFAD                  | Post-harvest loss reduction       | [ifad.org](https://www.ifad.org/en/v/48664157) |
| ESCWA                 | —                                 | —                                              |
| Malawi ASP study      | Stakeholder panels reduced losses | ~53%                                           |


### Knowledge Sharing Weights


| Resource                    | Finding                                                            | Use                                                                                                                  |
| --------------------------- | ------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------- |
| Lemeilleur & Allaire (2020) | Peer learning in agriculture                                       | 82–92% peer influence                                                                                                |
| Belabbes et al. (2025)      | Territorial intelligence, Morocco — extension (β=.31), ICT (β=.28) | [Research Square](https://assets-eu.researchsquare.com/files/rs-7375327/v1/730a0eea-f17c-4aa6-9208-8362d52431ed.pdf) |
| Faysse et al. (2014)        | Farmer decision-making, Morocco                                    | —                                                                                                                    |


---

## 4. Morocco Territorial & Policy Context

### Cooperatives & Governance


| Resource                   | Description                                           | Link                                                                            |
| -------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------- |
| **MOURAFAKA Programme**    | Post-creation support for cooperatives (ODCO)         | [odco.gov.ma/portfolio/mourafaka](https://www.odco.gov.ma/portfolio/mourafaka/) |
| **ODCO**                   | Office du Développement de la Coopération             | [odco.gov.ma](https://www.odco.gov.ma)                                          |
| Ibourk & Raoui (2022)      | Cooperative entrepreneurship, territorial development | [MDPI Sustainability](https://www.mdpi.com/2071-1050/14/24/16561)               |
| Fedorova & Taaricht (2020) | Agricultural cooperatives, Morocco                    | —                                                                               |


### Territorial Intelligence & Decision-Making


| Resource                   | Description                                               | Link                                                                                                                 |
| -------------------------- | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Belabbes et al. (2025)     | Territorial intelligence, farmers & policymakers, Morocco | [Research Square](https://assets-eu.researchsquare.com/files/rs-7375327/v1/730a0eea-f17c-4aa6-9208-8362d52431ed.pdf) |
| Bouchida & Azougagh (2023) | Territorial intelligence, Morocco                         | —                                                                                                                    |
| Ziadat et al. (2022)       | Participatory land planning, Souss-Massa                  | —                                                                                                                    |


### Agricultural Policy


| Resource                       | Description                    | Link                             |
| ------------------------------ | ------------------------------ | -------------------------------- |
| **Generation Green 2020–2030** | National agricultural strategy | Ministry of Agriculture, Morocco |
| **Green Morocco Plan**         | 2008–2020 strategy             | —                                |
| OECD (2016)                    | Rural development, Morocco     | —                                |


---

## 5. Software & Libraries


| Package    | Version | Use                       |
| ---------- | ------- | ------------------------- |
| Mesa       | ≥0.8.10 | Agent-based modeling      |
| Pandas     | ≥1.3.0  | Data handling             |
| NumPy      | ≥1.21.0 | Numerical computation     |
| NetworkX   | —       | Social network graphs     |
| Matplotlib | ≥3.4.0  | Plotting                  |
| Seaborn    | ≥0.11.0 | Statistical visualization |
| Plotly     | ≥5.0.0  | Interactive charts        |
| Solara     | ≥1.0.0  | Web dashboard             |


---

## 6. Scripts & Data Preparation


| Script                              | Purpose                                |
| ----------------------------------- | -------------------------------------- |
| `scripts/fetch_climate_data.py`     | Fetch NASA POWER climate data          |
| `scripts/update_crops_faostat.py`   | Update crop data from FAOSTAT          |
| `scripts/extract_faostat_prices.py` | Extract producer prices                |
| `Extract_morocco_data.ipynb`        | Copernicus NetCDF → soil moisture JSON |


---

## 7. Citation Format (BibTeX)

```bibtex
@article{mesa2015,
  author = {Kazil, Jacqueline and Masad, David and Crooks, Andrew},
  title = {Mesa: An Agent-Based Modeling Framework},
  year = {2015},
  journal = {SciPy Proceedings}
}

@article{ibourk2023,
  author = {Ibourk, Aomar and El Aynaoui, Karim},
  title = {Agricultural Cooperatives' Sustainability and the Relevance of Start-Up Support Programs: Evidence from Cooperatives' Level in Morocco},
  journal = {Sustainability},
  volume = {15},
  number = {4},
  pages = {3460},
  year = {2023}
}

@article{belabbes2025,
  author = {Belabbes, Zakaria and Ikhmim, Siham and Dkhissi, Atman},
  title = {Bridging Knowledge Gaps: Territorial Intelligence and Agricultural Decision-Making among Farmers and Policymakers in Morocco},
  year = {2025},
  note = {Research Square preprint},
  doi = {10.21203/rs.3.rs-7375327/v1}
}
```

---

*Last updated: March 2026*

