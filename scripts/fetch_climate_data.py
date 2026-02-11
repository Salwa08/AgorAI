"""
Fetch real climate data from NASA POWER API for Morocco's agro-ecological zones.

NASA POWER provides satellite-derived climate parameters at any lat/lon point.
Source: https://power.larc.nasa.gov/
Community: Agroclimatology (AG)

Parameters fetched:
  - T2M:           Temperature at 2m - monthly mean (°C)
  - T2M_MAX:       Temperature at 2m - monthly max (°C)
  - T2M_MIN:       Temperature at 2m - monthly min (°C)
  - PRECTOTCORR:   Precipitation corrected - monthly total (mm/day)
  - T2M_RANGE:     Temperature range at 2m (°C)
  - RH2M:          Relative humidity at 2m (%)
  - WS2M:          Wind speed at 2m (m/s)
  - ALLSKY_SFC_SW_DWN: Solar radiation (kW-hr/m²/day)

Usage:
    python scripts/fetch_climate_data.py
    python scripts/fetch_climate_data.py --start 2000 --end 2023
    python scripts/fetch_climate_data.py --start 1991 --end 2020  # WMO standard normal
"""

import json
import time
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime


# NASA POWER API base URL
API_BASE = "https://power.larc.nasa.gov/api/temporal/monthly/point"

# Parameters to fetch (agroclimatology community)
PARAMETERS = [
    "T2M",              # Mean temperature at 2m (°C)
    "T2M_MAX",          # Max temperature at 2m (°C)
    "T2M_MIN",          # Min temperature at 2m (°C)
    "PRECTOTCORR",      # Precipitation corrected (mm/day)
    "T2M_RANGE",        # Diurnal temperature range (°C)
    "RH2M",             # Relative humidity at 2m (%)
    "WS2M",             # Wind speed at 2m (m/s)
    "ALLSKY_SFC_SW_DWN" # Solar radiation (kW-hr/m²/day)
]

MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]


def load_zones(zones_path: str) -> dict:
    """Load zone definitions from zones.json."""
    with open(zones_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["zones"]


def fetch_nasa_power(lat: float, lon: float, start_year: int, end_year: int) -> dict:
    """
    Fetch monthly climate data from NASA POWER API for a single point.
    Returns the raw API response as a dict.
    """
    params = ",".join(PARAMETERS)
    url = (
        f"{API_BASE}"
        f"?parameters={params}"
        f"&community=AG"
        f"&longitude={lon}"
        f"&latitude={lat}"
        f"&start={start_year}"
        f"&end={end_year}"
        f"&format=JSON"
    )

    print(f"  Fetching: lat={lat}, lon={lon}, {start_year}-{end_year}")
    print(f"  URL: {url}")

    req = urllib.request.Request(url)
    req.add_header("User-Agent", "AgorAI-ClimateProfiler/1.0")

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        print(f"  HTTP Error {e.code}: {e.reason}")
        raise
    except urllib.error.URLError as e:
        print(f"  URL Error: {e.reason}")
        raise


def process_monthly_data(api_response: dict, start_year: int, end_year: int) -> dict:
    """
    Process NASA POWER API response into a structured climate profile.

    Returns:
        {
            "monthly_climatology": { "Jan": {...}, ... },
            "annual_summary": {...},
            "yearly_data": { "2000": {...}, ... },
            "variability": {...}
        }
    """
    params_data = api_response["properties"]["parameter"]
    num_years = end_year - start_year + 1

    # --- Monthly climatology (average across all years) ---
    monthly_clim = {}
    for m_idx, month_name in enumerate(MONTH_NAMES):
        month_num = m_idx + 1
        month_values = {}

        for param in PARAMETERS:
            if param not in params_data:
                continue
            values = []
            for year in range(start_year, end_year + 1):
                key = f"{year}{month_num:02d}"
                val = params_data[param].get(key, -999)
                if val != -999 and val is not None:
                    values.append(val)

            if values:
                month_values[param] = {
                    "mean": round(sum(values) / len(values), 2),
                    "min": round(min(values), 2),
                    "max": round(max(values), 2),
                    "std": round(_std(values), 2),
                    "n_years": len(values)
                }

        monthly_clim[month_name] = month_values

    # --- Annual summary ---
    annual = {}
    for param in PARAMETERS:
        if param not in params_data:
            continue
        yearly_means = []
        for year in range(start_year, end_year + 1):
            year_vals = []
            for month in range(1, 13):
                key = f"{year}{month:02d}"
                val = params_data[param].get(key, -999)
                if val != -999 and val is not None:
                    year_vals.append(val)

            if len(year_vals) == 12:
                if param == "PRECTOTCORR":
                    # Convert mm/day to mm/year (sum of monthly mm/day * days in month)
                    days_per_month = [31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                    yearly_total = sum(v * d for v, d in zip(year_vals, days_per_month))
                    yearly_means.append(yearly_total)
                else:
                    yearly_means.append(sum(year_vals) / 12)

        if yearly_means:
            label = f"{param}_annual_total_mm" if param == "PRECTOTCORR" else f"{param}_annual_mean"
            annual[label] = {
                "mean": round(sum(yearly_means) / len(yearly_means), 2),
                "min": round(min(yearly_means), 2),
                "max": round(max(yearly_means), 2),
                "std": round(_std(yearly_means), 2)
            }

    # --- Year-by-year data (for variability analysis) ---
    yearly_data = {}
    for year in range(start_year, end_year + 1):
        year_record = {}
        for param in PARAMETERS:
            if param not in params_data:
                continue
            vals = []
            for month in range(1, 13):
                key = f"{year}{month:02d}"
                val = params_data[param].get(key, -999)
                if val != -999 and val is not None:
                    vals.append(val)
            if vals:
                if param == "PRECTOTCORR":
                    days_per_month = [31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                    year_record[f"{param}_annual_total_mm"] = round(
                        sum(v * d for v, d in zip(vals, days_per_month)), 1
                    )
                year_record[f"{param}_monthly_mean"] = round(sum(vals) / len(vals), 2)

        yearly_data[str(year)] = year_record

    # --- Variability metrics (for simulation weather events) ---
    variability = _compute_variability(params_data, start_year, end_year)

    return {
        "monthly_climatology": monthly_clim,
        "annual_summary": annual,
        "yearly_data": yearly_data,
        "variability": variability
    }


def _compute_variability(params_data: dict, start_year: int, end_year: int) -> dict:
    """Compute inter-annual variability metrics useful for simulation."""
    variability = {}

    # Precipitation variability
    if "PRECTOTCORR" in params_data:
        days_per_month = [31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        annual_precip = []
        for year in range(start_year, end_year + 1):
            year_vals = []
            for month in range(1, 13):
                key = f"{year}{month:02d}"
                val = params_data["PRECTOTCORR"].get(key, -999)
                if val != -999 and val is not None:
                    year_vals.append(val)
            if len(year_vals) == 12:
                total = sum(v * d for v, d in zip(year_vals, days_per_month))
                annual_precip.append(total)

        if annual_precip:
            mean_p = sum(annual_precip) / len(annual_precip)
            std_p = _std(annual_precip)
            # Coefficient of variation
            cv = round(std_p / mean_p, 3) if mean_p > 0 else None
            # Drought years: < mean - 1*std
            drought_threshold = mean_p - std_p
            drought_years = sum(1 for p in annual_precip if p < drought_threshold)
            drought_freq = round(drought_years / len(annual_precip), 3)
            # Wet years: > mean + 1*std
            wet_threshold = mean_p + std_p
            wet_years = sum(1 for p in annual_precip if p > wet_threshold)
            wet_freq = round(wet_years / len(annual_precip), 3)

            variability["precipitation"] = {
                "cv": cv,
                "drought_frequency": drought_freq,
                "drought_threshold_mm": round(drought_threshold, 1),
                "wet_frequency": wet_freq,
                "wet_threshold_mm": round(wet_threshold, 1)
            }

    # Temperature variability
    if "T2M" in params_data:
        # Hottest month max across years
        jul_temps = []
        jan_temps = []
        for year in range(start_year, end_year + 1):
            jul_key = f"{year}07"
            jan_key = f"{year}01"
            jul_val = params_data["T2M"].get(jul_key, -999)
            jan_val = params_data["T2M"].get(jan_key, -999)
            if jul_val != -999:
                jul_temps.append(jul_val)
            if jan_val != -999:
                jan_temps.append(jan_val)

        if jul_temps and jan_temps:
            variability["temperature"] = {
                "jan_mean_std": round(_std(jan_temps), 2),
                "jul_mean_std": round(_std(jul_temps), 2),
                "thermal_amplitude_mean": round(
                    sum(jul_temps) / len(jul_temps) - sum(jan_temps) / len(jan_temps), 2
                )
            }

    return variability


def _std(values: list) -> float:
    """Compute sample standard deviation."""
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return variance ** 0.5


def main():
    parser = argparse.ArgumentParser(description="Fetch NASA POWER climate data for Morocco zones")
    parser.add_argument("--start", type=int, default=2021, help="Start year (default: 2001)")
    parser.add_argument("--end", type=int, default=2024, help="End year (default: 2024)")
    parser.add_argument("--zones", type=str, default=None, help="Path to zones.json")
    parser.add_argument("--output", type=str, default=None, help="Path to output climate_profiles.json")
    args = parser.parse_args()

    # Resolve paths
    project_root = Path(__file__).parent.parent
    zones_path = args.zones or str(project_root / "data" / "zones.json")
    output_path = args.output or str(project_root / "data" / "climate_profiles.json")

    print(f"=== NASA POWER Climate Data Fetcher ===")
    print(f"Period: {args.start} - {args.end}")
    print(f"Zones file: {zones_path}")
    print(f"Output: {output_path}")
    print()

    # Load zones
    zones = load_zones(zones_path)
    print(f"Loaded {len(zones)} zones\n")

    # Fetch data for each zone
    climate_profiles = {
        "metadata": {
            "source": "NASA POWER API v2.0 (https://power.larc.nasa.gov/)",
            "community": "Agroclimatology (AG)",
            "temporal_resolution": "monthly",
            "period": f"{args.start}-{args.end}",
            "parameters": {
                "T2M": "Temperature at 2 Meters (°C) - monthly mean",
                "T2M_MAX": "Temperature at 2 Meters Maximum (°C)",
                "T2M_MIN": "Temperature at 2 Meters Minimum (°C)",
                "PRECTOTCORR": "Precipitation Corrected (mm/day)",
                "T2M_RANGE": "Temperature Range at 2 Meters (°C)",
                "RH2M": "Relative Humidity at 2 Meters (%)",
                "WS2M": "Wind Speed at 2 Meters (m/s)",
                "ALLSKY_SFC_SW_DWN": "All Sky Surface Shortwave Downward Irradiance (kW-hr/m²/day)"
            },
            "generated_at": datetime.now().isoformat(),
            "notes": "PRECTOTCORR annual totals are converted from mm/day to mm/year using days-per-month weighting."
        },
        "zones": {}
    }

    for zone_id, zone_data in zones.items():
        pt = zone_data["representative_point"]
        print(f"[{zone_id}] {pt['label']}")

        try:
            raw = fetch_nasa_power(pt["lat"], pt["lon"], args.start, args.end)
            profile = process_monthly_data(raw, args.start, args.end)

            climate_profiles["zones"][zone_id] = {
                "zone_name": zone_data["name"],
                "representative_point": pt,
                "climate_profile": profile
            }
            print(f"  OK - {len(profile['yearly_data'])} years of data\n")

        except Exception as e:
            print(f"  FAILED: {e}\n")
            climate_profiles["zones"][zone_id] = {
                "zone_name": zone_data["name"],
                "representative_point": pt,
                "error": str(e)
            }

        # Be polite to the API
        time.sleep(2)

    # Save output
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(climate_profiles, f, indent=2, ensure_ascii=False)

    print(f"\n=== Done ===")
    print(f"Saved to: {output_path}")

    # Print quick summary
    print(f"\n--- Quick Summary ---")
    for zone_id, zdata in climate_profiles["zones"].items():
        if "error" in zdata:
            print(f"  {zone_id}: ERROR - {zdata['error']}")
            continue
        profile = zdata["climate_profile"]
        annual = profile.get("annual_summary", {})
        precip = annual.get("PRECTOTCORR_annual_total_mm", {})
        temp = annual.get("T2M_annual_mean", {})
        var = profile.get("variability", {}).get("precipitation", {})
        print(
            f"  {zone_id}: "
            f"precip={precip.get('mean', '?'):.0f}mm/yr "
            f"[{precip.get('min', '?'):.0f}-{precip.get('max', '?'):.0f}], "
            f"temp={temp.get('mean', '?'):.1f}°C, "
            f"drought_freq={var.get('drought_frequency', '?')}"
        )


if __name__ == "__main__":
    main()
