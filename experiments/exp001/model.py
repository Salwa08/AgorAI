"""V1 equations extracted from notebook cells 0–1; EXP001 changes documented in AUDIT.md."""
import hashlib
import json
import random
import time
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
from mesa import Agent, Model

try:
    import networkx as nx
    HAS_NX = True
except ImportError:
    HAS_NX = False
@dataclass
class SIM_CONFIG:
    social_information_enabled: bool = False
    cooperative_economics_enabled: bool = False
    n_agents: int = 100
    n_seasons: int = 30
    random_seed: int = 42
    noise_std: float = 0.10
    suitability_noise_std: float = 0.08 # per-farmer
    use_neighbor_graph: bool = True
    network_topology: str = "small_world" # small_world | random | scale_free
    network_k: int = 4
    knowledge_filter_mode: str = "filter" # filter (zone-only) | weighted | none
    shared_strategy: str = "both" # zone | neighbor | both  (zone aggregate + neighbor propagation)
    use_profit: bool = True
    zone_weight: float = 0.30
    soil_weight: float = 0.25
    climate_weight: float = 0.25
    moisture_weight: float = 0.10
    shared_weight: float = 0.45
    neighbor_weight: float = 0.30
    experience_weight: float = 0.25
    min_neighbor_obs: int = 3   # Minimum observations before trusting neighbor data and sharing it
    variability_min: float = 0.85
    variability_max: float = 1.15
    cost_noise_std: float = 0.15
    shared_price_premium: float = 0.10 # Shared farmers get a price premium
    shared_cost_efficiency: float = 0.80 # Shared farmers have lower costs
    shared_post_harvest_loss: float = 0.06 # Shared farmers have lower post-harvest loss
    indiv_cost_efficiency: float = 0.90 # Individual farmers have higher costs
    indiv_post_harvest_loss: float = 0.12

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

def _load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

zones_data     = _load_json(DATA_DIR / "zones.json")
crops_data     = _load_json(DATA_DIR / "crops.json")
climate_data   = _load_json(DATA_DIR / "climate_profiles.json")
soil_moisture  = _load_json(DATA_DIR / "soil_moisture_profiles.json")

ZONE_IDS = list(zones_data["zones"].keys())
CROP_IDS = list(crops_data["crops"].keys())



def _get_water_use_mm(crop, irrigation_level, cfg):
    need = crop.get("water_need", "medium")
    base_mm = crops_data.get("water_need_mm", {}).get(need, 500)
    return base_mm * irrigation_level

def _get_cost_per_ha(crop, zone, cfg, farmer_noise = 0.0):
    # Get cost model parameters from crops.json
    cost_model = crops_data.get("cost_model", {})
    smag_per_day = cost_model.get("smag_mad_per_day", 84.37)
    fertilizer_costs = cost_model.get("fertilizer_npk_mad_per_ha", {})
    seeds_costs = cost_model.get("seeds_mad_per_ha", {})
    mechanization_costs = cost_model.get("mechanization_mad_per_ha", {})

    # Get crop-specific parameters
    labor_days = crop.get("labor_days_per_ha", 25)
    cost_category = crop.get("cost_category", "cereal")

    # Calculate component costs
    labor_cost = labor_days * smag_per_day
    fertilizer_cost = fertilizer_costs.get(cost_category, 1800)
    seeds_cost = seeds_costs.get(cost_category, 800)
    mechanization_cost = mechanization_costs.get(cost_category, 1200)

    # Water cost (already data-driven)
    water_price = zone.get("water_price", 0.2)
    need = crop.get("water_need", "medium")
    water_mm = crops_data.get("water_need_mm", {}).get(need, 500)
    water_cost = water_mm * water_price * 10  # Convert mm to m3/ha (1mm = 10 m3/ha)

    # Total cost
    raw_cost = labor_cost + fertilizer_cost + seeds_cost + mechanization_cost + water_cost

    return raw_cost * max(0.5, 1.0 + farmer_noise)

def calculate_yield(
    crop_id, crop, zone,
    climate_profile, season_weather,
    noise_std = 0.1, rng=None,
):
    if rng is None:
        raise ValueError("Explicit yield RNG required")
    base_yield = crop.get("base_yield_t_ha", 1.0)
    viable = zone.get("viable_crops", [])
    zone_viability = 1.0 if crop_id in viable else 0.2

    dominant_soil = zone.get("dominant_soil", "")
    ideal_soils = crop.get("ideal_soils", [])
    soil_match = 1.0 if dominant_soil in ideal_soils else 0.4

    ecocrop = crop.get("ecocrop", {})
    temp_min = ecocrop.get("temp_opt_min_C", 10)
    temp_max = ecocrop.get("temp_opt_max_C", 30)
    precip_min = ecocrop.get("precip_opt_min_mm", 300)
    precip_max = ecocrop.get("precip_opt_max_mm", 800)

    annual = climate_profile.get("annual_summary", {})
    zone_temp = annual.get("T2M_annual_mean", {}).get("mean", 20)
    zone_precip = annual.get("PRECTOTCORR_annual_total_mm", {}).get("mean", 400)

    temp_ok = temp_min <= zone_temp <= temp_max
    precip_ok = precip_min <= zone_precip <= precip_max
    if temp_ok and precip_ok:
        climate_match = 1.0
    elif temp_ok or precip_ok:
        climate_match = 0.7
    else:
        climate_match = 0.4

    wt = season_weather.get("weather_type", "normal")
    if wt == "drought":
        weather_factor = rng.uniform(0.3, 0.6)
    elif wt == "wet":
        weather_factor = rng.uniform(1.0, 1.2)
    else:
        weather_factor = rng.uniform(0.8, 1.1)

    noise = max(0.1, rng.gauss(1.0, noise_std))
    return base_yield * zone_viability * soil_match * climate_match * weather_factor * noise

def calculate_season_outcome(
    crop_id, crop, zone,
    climate_profile, season_weather,
    irrigation_level, cfg,
    farmer_cost_noise = 0.0, rng=None,
):
    y = calculate_yield(crop_id, crop, zone, climate_profile, season_weather, cfg.noise_std, rng=rng)
    cost = _get_cost_per_ha(crop, zone, cfg, farmer_noise=farmer_cost_noise)
    water = _get_water_use_mm(crop, irrigation_level, cfg)
    return y, cost, water

def get_crop_price(crop_id):
    return crops_data["crops"].get(crop_id, {}).get("faostat_price_mad_per_ton", 4000)

def generate_weather(zone_id, rng):

    zone_climate = climate_data.get("zones", {}).get(zone_id, {})
    variability = zone_climate.get("climate_profile", {}).get("variability", {})
    precip_var = variability.get("precipitation", {})
    drought_freq = precip_var.get("drought_frequency", 0.2)
    wet_freq = precip_var.get("wet_frequency", 0.15)
    r = rng.random()
    if r < drought_freq:
        return "drought"
    if r < drought_freq + wet_freq:
        return "wet"
    return "normal"

def build_graph(farmers, topology="small_world", k=4, seed=None):
    if not HAS_NX:
        print("WARNING: networkx not installed — skipping neighbor graph")
        return None
    n = len(farmers)
    if n < 2:
        return nx.Graph()
    k = min(k, (n - 1) // 2)
    if topology == "small_world":
        g = nx.watts_strogatz_graph(n, max(k, 2), p=0.3, seed=seed)
    elif topology == "random":
        p = min(1.0, max(0.01, 2 * k / n))
        g = nx.erdos_renyi_graph(n, p, seed=seed)
    elif topology == "scale_free":
        m = min(k, n - 1)
        g = nx.barabasi_albert_graph(n, max(m, 1), seed=seed)
    else:
        g = nx.watts_strogatz_graph(n, max(k, 2), p=0.3, seed=seed)
    for i, farmer in enumerate(farmers):
        farmer.neighbor_agents = [farmers[j] for j in g.neighbors(i)]
    return g

def propagate_knowledge(farmer, crop_id, yield_val, cost, water, filter_mode="filter"):
    for nb in farmer.neighbor_agents:

        if not farmer.model.cfg.social_information_enabled or not nb.model.cfg.social_information_enabled:
            continue
        if filter_mode == "filter" and nb.zone.id != farmer.zone.id:
            continue
        nb.knowledge_base.setdefault(crop_id, []).append((yield_val, cost, water))

class Zone:
    def __init__(self, zone_id, data, climate_profile, soil_moisture_data):
        self.id = zone_id
        self.name = data["name"]
        self.soil_types = data["soil_types"]
        self.dominant_soil = data["dominant_soil"]
        self.viable_crops = data["viable_crops"]
        self.agriculture_type = data["agriculture_type"]
        self.climate_profile = climate_profile
        self.raw_zone_data = data

        sm = soil_moisture_data["zones"].get(zone_id, {})
        self.mean_sm = sm.get("mean", 0.15)
        self.std_sm = sm.get("std", 0.05)

        self.shared_crop_yield = {}
        self.shared_crop_profit = {}

GOAL_PROFILES = [
    {"yield": 1.0, "budget": 0.0, "water": 0.0},
    {"yield": 0.0, "budget": 1.0, "water": 0.0},
    {"yield": 0.0, "budget": 0.0, "water": 1.0},
    {"yield": 0.5, "budget": 0.3, "water": 0.2},
]

class FarmerAgent(Agent):
    def __init__(
        self, model, unique_id, zone,
        land_size, strategy_type,
        goal_profile, budget, irrigation_type,
    ):
        super().__init__(model)
        self.unique_id = unique_id
        self.zone = zone
        self.land_size = land_size
        self.strategy_type = strategy_type

        self.goal_profile = goal_profile
        self.budget = budget
        self.irrigation_type = irrigation_type
        self.irrigation_level = 1.0
        self.weather_type = "normal"

        self.cost_noise_factor = model.stream("cost", unique_id).gauss(0, model.cfg.cost_noise_std)

        self.knowledge_base = {}
        self.neighbor_agents = []

        self.chosen_crop = None
        self.yield_t_ha = 0.0
        self.cost_per_ha = 0.0
        self.water_use_mm = 0.0
        self.profit = 0.0
        self.memory = []

    def set_weather(self, weather_type):
        self.weather_type = weather_type

    def react_to_drought(self):
        if self.weather_type == "drought":
            self.irrigation_level = 0.6
        else:
            self.irrigation_level = 0.9

    def compute_suitability(self, crop_name, cfg):
        crop = crops_data["crops"][crop_name]
        ecocrop = crop.get("ecocrop", {})
        zone = self.zone
        score = 0.0
        wt_total = 0.0

        ideal_zones = crop.get("ideal_zones", [])
        if zone.id in ideal_zones:
            score += 1.0 * cfg.zone_weight
        elif crop_name in zone.viable_crops:
            score += 0.7 * cfg.zone_weight
        else:
            score += 0.15 * cfg.zone_weight
        wt_total += cfg.zone_weight

        ideal_soils = crop.get("ideal_soils", [])
        if zone.dominant_soil in ideal_soils:
            score += 1.0 * cfg.soil_weight
        else:
            score += 0.3 * cfg.soil_weight
        wt_total += cfg.soil_weight

        cp = zone.climate_profile
        annual = cp.get("annual_summary", {})
        zone_temp = annual.get("T2M_annual_mean", {}).get("mean", 20)
        zone_precip = annual.get("PRECTOTCORR_annual_total_mm", {}).get("mean", 400)

        t_opt_min = ecocrop.get("temp_opt_min_C", 15)
        t_opt_max = ecocrop.get("temp_opt_max_C", 30)
        t_abs_min = ecocrop.get("temp_abs_min_C", 5)
        t_abs_max = ecocrop.get("temp_abs_max_C", 40)
        if t_opt_min <= zone_temp <= t_opt_max:
            temp_score = 1.0
        elif t_abs_min <= zone_temp <= t_abs_max:
            temp_score = 0.5
        else:
            temp_score = 0.0

        p_opt_min = ecocrop.get("precip_opt_min_mm", 400)
        p_opt_max = ecocrop.get("precip_opt_max_mm", 1200)
        p_abs_min = ecocrop.get("precip_abs_min_mm", 200)
        p_abs_max = ecocrop.get("precip_abs_max_mm", 2000)
        if p_opt_min <= zone_precip <= p_opt_max:
            precip_score = 1.0
        elif p_abs_min <= zone_precip <= p_abs_max:
            precip_score = 0.5
        else:
            precip_score = 0.0

        climate_score = 0.5 * temp_score + 0.5 * precip_score
        score += climate_score * cfg.climate_weight
        wt_total += cfg.climate_weight

        sm_norm = zone.mean_sm
        moisture_pref = crop.get("moisture_preference", "medium")
        if moisture_pref == "high":
            moisture_score = sm_norm
        elif moisture_pref == "low":
            moisture_score = 1.0 - sm_norm
        else:
            moisture_score = 1.0 - abs(sm_norm - 0.5) * 2
        score += max(0, moisture_score) * cfg.moisture_weight
        wt_total += cfg.moisture_weight

        base_suit = score / wt_total if wt_total > 0 else 0.0

        rng_noise = self.model.stream("suit", self.unique_id, crop_name)
        noise = rng_noise.gauss(0, cfg.suitability_noise_std)
        return max(0.0, base_suit + noise)

    def _score_from_knowledge(self, obs_list):
        if not obs_list:
            return -1e9
        avg_y = sum(o[0] for o in obs_list) / len(obs_list)
        avg_c = sum(o[1] for o in obs_list) / len(obs_list)
        avg_w = sum(o[2] for o in obs_list) / len(obs_list)
        yield_norm = avg_y / 10.0
        cost_score = 1.0 - min(1.0, avg_c / 50000)
        water_score = 1.0 - min(1.0, avg_w / 1000)
        gp = self.goal_profile
        return (gp.get("yield", 0) * yield_norm
                + gp.get("budget", 0) * cost_score
                + gp.get("water", 0) * water_score)

    def decide_crop(self, cfg):

        available = [c for c in self.zone.viable_crops if c in crops_data["crops"]]
        if not available:
            available = list(crops_data["crops"].keys())
        scores = {}

        for crop in available:
            scores[crop] = self.compute_suitability(crop, cfg)

        if cfg.social_information_enabled:
            zone_shared = self.zone.shared_crop_yield
            zone_profit = self.zone.shared_crop_profit

            if cfg.shared_strategy in ("zone", "both") and zone_shared:
                max_zy = max(zone_shared.values()) if zone_shared else 1.0
                for crop in available:
                    if crop in zone_shared and max_zy > 0:
                        yield_bonus = zone_shared[crop] / max_zy
                        if cfg.use_profit and zone_profit:
                            max_zp = max(abs(v) for v in zone_profit.values()) if zone_profit else 1.0
                            profit_bonus = zone_profit.get(crop, 0) / max_zp if max_zp > 0 else 0
                            bonus = 0.6 * yield_bonus + 0.4 * max(0, profit_bonus)
                        else:
                            bonus = yield_bonus
                        scores[crop] += cfg.shared_weight * bonus
                    else:

                        scores[crop] *= (1.0 - cfg.shared_weight * 0.3)

            if cfg.shared_strategy in ("neighbor", "both") and self.neighbor_agents:
                merged = {}
                for nb in self.neighbor_agents:
                    if cfg.knowledge_filter_mode == "filter" and nb.zone.id != self.zone.id:
                        continue
                    for cid, obs_list in nb.knowledge_base.items():
                        merged.setdefault(cid, []).extend(obs_list)
                if merged:

                    nb_scores = {
                        c: self._score_from_knowledge(obs)
                        for c, obs in merged.items()
                        if len(obs) >= cfg.min_neighbor_obs
                    }
                    if nb_scores:
                        nb_max = max(nb_scores.values())
                        nb_min = min(nb_scores.values())
                        rng = nb_max - nb_min if nb_max != nb_min else 1.0
                        for crop in available:
                            if crop in nb_scores:
                                norm_nb = (nb_scores[crop] - nb_min) / rng
                                scores[crop] += cfg.neighbor_weight * norm_nb

        if self.knowledge_base:
            own_scores = {
                c: self._score_from_knowledge(obs)
                for c, obs in self.knowledge_base.items()
                if obs
            }
            if own_scores:
                own_max = max(own_scores.values())
                own_min = min(own_scores.values())
                rng_own = own_max - own_min if own_max != own_min else 1.0
                for crop in available:
                    if crop in own_scores:
                        norm_own = (own_scores[crop] - own_min) / rng_own
                        scores[crop] += cfg.experience_weight * norm_own

        self.chosen_crop = max(scores, key=scores.get)

    def harvest(self, zone_weather, cfg):
        crop_id = self.chosen_crop
        crop = crops_data["crops"][crop_id]
        zone_dict = self.zone.raw_zone_data
        cp_inner = self.zone.climate_profile
        sw = {"weather_type": zone_weather.get(self.zone.id, "normal")}

        y, cost, water = calculate_season_outcome(
            crop_id, crop, zone_dict, cp_inner, sw,
            self.irrigation_level, cfg,
            farmer_cost_noise=self.cost_noise_factor,
            rng=self.model.stream("harvest", self.model.season, self.unique_id),
        )

        price = get_crop_price(crop_id)
        if cfg.cooperative_economics_enabled:
            price *= (1.0 + cfg.shared_price_premium)
            cost *= cfg.shared_cost_efficiency
            post_harvest_loss = cfg.shared_post_harvest_loss
        else:
            cost *= cfg.indiv_cost_efficiency
            post_harvest_loss = cfg.indiv_post_harvest_loss

        effective_yield = y * (1.0 - post_harvest_loss)

        self.yield_t_ha = y
        self.cost_per_ha = cost
        self.water_use_mm = water
        self.effective_yield = effective_yield
        self.price = price
        self.profit = (effective_yield * price - cost) * self.land_size

        self.knowledge_base.setdefault(crop_id, []).append((y, cost, water))
        self.memory.append({
            "crop": crop_id, "yield": y, "cost": cost,
            "water": water, "profit": self.profit,
        })

    def step(self):
        pass # actual logic in FarmModel.step()



class FarmModel(Model):
    """A homogeneous treatment population paired by identity across four worlds."""

    def __init__(self, cfg):
        from dataclasses import replace
        from copy import deepcopy
        if cfg.n_agents < 2 or cfg.n_seasons < 1:
            raise ValueError("n_agents >= 2 and n_seasons >= 1 required")
        if cfg.shared_strategy not in ("zone", "neighbor", "both"):
            raise ValueError("Invalid shared_strategy")
        if cfg.knowledge_filter_mode not in ("filter", "weighted", "none"):
            raise ValueError("Invalid knowledge_filter_mode")
        if cfg.network_topology not in ("small_world", "random", "scale_free"):
            raise ValueError("Invalid network_topology")
        if cfg.use_neighbor_graph and not HAS_NX:
            raise RuntimeError("networkx required; refusing silent treatment degradation")
        super().__init__(seed=cfg.random_seed)
        self.cfg = replace(cfg)
        self.season = 0
        self.zones = {
            zid: Zone(zid, deepcopy(info),
                      deepcopy(climate_data["zones"][zid]["climate_profile"]),
                      deepcopy(soil_moisture))
            for zid, info in zones_data["zones"].items()
        }
        self.farmers = []
        for aid in range(cfg.n_agents):
            rng = self.stream("population", aid)
            zone = rng.choice(list(self.zones.values()))
            land = rng.uniform(1, 10)
            budget_range = zone.raw_zone_data.get("budget_range", [5000, 15000])
            farmer = FarmerAgent(
                self, aid, zone, land, "EXPERIMENT",
                GOAL_PROFILES[aid % len(GOAL_PROFILES)].copy(),
                rng.uniform(*budget_range),
                zone.raw_zone_data.get("irrigation_type", "rainfed"),
            )
            self.farmers.append(farmer)
        self.graph = build_graph(self.farmers, cfg.network_topology,
                                 cfg.network_k, cfg.random_seed) if cfg.use_neighbor_graph else None
        self.records = []
        self.weather_history = []

    def stream(self, *keys):
        payload = json.dumps([self.cfg.random_seed, *keys], separators=(",", ":"))
        return random.Random(int.from_bytes(hashlib.sha256(payload.encode()).digest(), "big"))

    def step(self):
        self.season += 1
        cfg = self.cfg
        weather = {z: generate_weather(z, self.stream("weather", self.season, z)) for z in self.zones}
        self.weather_history.append(weather)
        farmers = list(self.farmers)
        self.stream("order", self.season).shuffle(farmers)
        for f in farmers:
            f.set_weather(weather[f.zone.id])
            f.react_to_drought()
            f.decide_crop(cfg)
        for f in farmers:
            f.harvest(weather, cfg)
            self.records.append({
                "seed": cfg.random_seed, "season": self.season, "agent": f.unique_id,
                "zone": f.zone.id, "land_ha": f.land_size, "crop": f.chosen_crop,
                "weather": weather[f.zone.id], "yield_t_ha": f.yield_t_ha,
                "effective_yield_t_ha": f.effective_yield,
                "production_t": f.yield_t_ha * f.land_size,
                "cost_mad_ha": f.cost_per_ha, "price_mad_t": f.price,
                "water_proxy_mm": f.water_use_mm, "profit_mad": f.profit,
                "profit_mad_ha": f.profit / f.land_size,
                "cost_noise": f.cost_noise_factor,
            })
        if cfg.social_information_enabled:
            self.update_shared_knowledge()
            if cfg.use_neighbor_graph and cfg.shared_strategy in ("neighbor", "both"):
                for f in farmers:
                    propagate_knowledge(f, f.chosen_crop, f.yield_t_ha,
                                        f.cost_per_ha, f.water_use_mm, cfg.knowledge_filter_mode)

    def update_shared_knowledge(self):
        if not self.cfg.social_information_enabled:
            return
        for zone in self.zones.values():
            by_crop = {}
            for f in self.farmers:
                if f.zone is zone:
                    by_crop.setdefault(f.chosen_crop, []).append(f)
            zone.shared_crop_yield = {c: sum(f.yield_t_ha for f in fs) / len(fs)
                                      for c, fs in by_crop.items()}
            zone.shared_crop_profit = {
                c: sum(f.profit for f in fs) / len(fs) for c, fs in by_crop.items()
            } if self.cfg.use_profit else {}


def run_sim(cfg):
    model = FarmModel(cfg)
    for _ in range(cfg.n_seasons):
        model.step()
    return model, pd.DataFrame(model.records).sort_values(["season", "agent"]).reset_index(drop=True)
