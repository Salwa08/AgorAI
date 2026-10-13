"""Isolated EXP002 instrumentation and one-factor diagnostic interventions."""
from dataclasses import dataclass
from collections import Counter
import pandas as pd
from experiments.exp001 import model as v1


@dataclass
class Config(v1.SIM_CONFIG):
    epsilon: float = 0.0
    deduplicate: bool = False
    own_memory_only: bool = False
    profit_per_ha: bool = False
    context_filter: str = 'same_zone'
    zone_yield_fraction: float = .6


@dataclass(frozen=True)
class Observation:
    seed: int
    farmer: int
    season: int
    zone: str
    crop: str
    land: float
    yield_: float
    cost: float
    water: float
    profit: float

    @property
    def identity(self):
        return (self.seed, self.farmer, self.season)

    @property
    def values(self):
        return (self.yield_, self.cost, self.water)


def unique(observations):
    seen=set()
    return [o for o in observations if not (o.identity in seen or seen.add(o.identity))]


def compatible(receiver, source, mode):
    if mode == 'unrestricted' or receiver.id == source.id:
        return True
    if mode == 'same_zone':
        return False
    if mode != 'ecological':
        raise ValueError('Unknown context filter')
    def climate(z, key, fallback):
        return z.climate_profile.get('annual_summary',{}).get(key,{}).get('mean',fallback)
    return (receiver.dominant_soil == source.dominant_soil
            and abs(climate(receiver,'T2M_annual_mean',20)-climate(source,'T2M_annual_mean',20)) <= 3
            and abs(climate(receiver,'PRECTOTCORR_annual_total_mm',400)-climate(source,'PRECTOTCORR_annual_total_mm',400)) <= 200)


class DiagnosticModel(v1.FarmModel):
    def __init__(self, cfg, tracing=True):
        if not 0 <= cfg.epsilon <= 1 or not 0 <= cfg.zone_yield_fraction <= 1:
            raise ValueError('Probability outside [0,1]')
        if cfg.epsilon and cfg.social_information_enabled:
            raise ValueError('EXP002 exploration is restricted to information-off agents')
        if cfg.context_filter not in ('same_zone','unrestricted','ecological'):
            raise ValueError('Invalid context filter')
        if cfg.knowledge_filter_mode != 'filter':
            raise ValueError('Use context_filter for EXP002; inherited filter must remain default')
        super().__init__(cfg)
        self.tracing=tracing
        self.traces=[]
        self.ledger=[]
        self.zone_observations={z:{} for z in self.zones}
        self.last_details={}
        for f in self.farmers:
            f.provenance={}

    def pool_stats(self, observations, farmer):
        n=len(observations)
        ids={o.identity for o in observations}
        ages=[self.season-o.season for o in observations]
        if ages and min(ages)<1:
            raise AssertionError('Future/current season information in decision')
        return dict(count=n,unique=len(ids),duplicates=n-len(ids),
            received=sum(o.farmer!=farmer.unique_id for o in observations),
            cross_zone=sum(o.zone!=farmer.zone.id for o in observations),
            origin_zones=dict(Counter(o.zone for o in observations)),
            origin_farmers=sorted({o.farmer for o in observations}),
            age_min=min(ages) if ages else None,age_max=max(ages) if ages else None,
            age_mean=sum(ages)/n if n else None,
            source_land_mean=sum(o.land for o in observations)/n if n else None)

    def pools(self, farmer):
        cfg=self.cfg
        own={c:list(obs) for c,obs in farmer.provenance.items()}
        if cfg.own_memory_only:
            own={c:[o for o in obs if o.farmer==farmer.unique_id] for c,obs in own.items()}
        neighbor={}
        if cfg.social_information_enabled and cfg.shared_strategy in ('neighbor','both'):
            for nb in farmer.neighbor_agents:
                if not compatible(farmer.zone,nb.zone,cfg.context_filter):
                    continue
                for crop,observations in nb.provenance.items():
                    neighbor.setdefault(crop,[]).extend(
                        o for o in observations if compatible(farmer.zone,self.zones[o.zone],cfg.context_filter))
        if cfg.deduplicate:
            own={c:unique(obs) for c,obs in own.items()}
            neighbor={c:unique(obs) for c,obs in neighbor.items()}
        return own,neighbor

    def decide(self, f):
        cfg=self.cfg
        available=[c for c in f.zone.viable_crops if c in v1.crops_data['crops']]
        if not available: available=list(v1.crops_data['crops'])
        scores={c:f.compute_suitability(c,cfg) for c in available}
        components={c:dict(suitability=s,zone=0.,neighbor=0.,experience=0.) for c,s in scores.items()}
        own,neighbor=self.pools(f)
        zone={}
        if cfg.social_information_enabled:
            zone_shared=f.zone.shared_crop_yield
            zone_profit=f.zone.shared_crop_profit
            if cfg.shared_strategy in ('zone','both') and zone_shared:
                zone=self.zone_observations[f.zone.id]
                max_zy=max(zone_shared.values())
                for crop in available:
                    before=scores[crop]
                    if crop in zone_shared and max_zy>0:
                        yield_bonus=zone_shared[crop]/max_zy
                        if cfg.use_profit and zone_profit:
                            max_zp=max(abs(v) for v in zone_profit.values())
                            profit_bonus=zone_profit.get(crop,0)/max_zp if max_zp>0 else 0
                            bonus=cfg.zone_yield_fraction*yield_bonus+(1-cfg.zone_yield_fraction)*max(0,profit_bonus)
                        else:
                            bonus=yield_bonus
                        scores[crop]+=cfg.shared_weight*bonus
                    else:
                        scores[crop]*=(1-cfg.shared_weight*.3)
                    components[crop]['zone']=scores[crop]-before
            nb_scores={c:f._score_from_knowledge([o.values for o in obs])
                       for c,obs in neighbor.items() if len(obs)>=cfg.min_neighbor_obs}
            if nb_scores:
                nb_max=max(nb_scores.values()); nb_min=min(nb_scores.values())
                span=nb_max-nb_min if nb_max!=nb_min else 1.
                for c in available:
                    if c in nb_scores:
                        before=scores[c]
                        scores[c]+=cfg.neighbor_weight*((nb_scores[c]-nb_min)/span)
                        components[c]['neighbor']=scores[c]-before
        own_scores={c:f._score_from_knowledge([o.values for o in obs]) for c,obs in own.items() if obs}
        if own_scores:
            own_max=max(own_scores.values()); own_min=min(own_scores.values())
            span=own_max-own_min if own_max!=own_min else 1.
            for c in available:
                if c in own_scores:
                    before=scores[c]
                    scores[c]+=cfg.experience_weight*((own_scores[c]-own_min)/span)
                    components[c]['experience']=scores[c]-before
        greedy=max(scores,key=scores.get)
        explored=cfg.epsilon>0 and self.stream('explore',self.season,f.unique_id).random()<cfg.epsilon
        previous=f.chosen_crop
        f.chosen_crop=self.stream('explore_choice',self.season,f.unique_id).choice(available) if explored else greedy
        if self.tracing:
            candidates={}
            for c in available:
                candidates[c]=dict(**components[c],total_score=scores[c],
                    experience_info=self.pool_stats(own.get(c,[]),f),
                    neighbor_info=self.pool_stats(neighbor.get(c,[]),f),
                    zone_info=self.pool_stats(zone.get(c,[]),f))
            all_own=[o for obs in own.values() for o in obs]
            all_neighbor=[o for obs in neighbor.values() for o in obs]
            all_zone=[o for obs in zone.values() for o in obs]
            self.last_details[f.unique_id]=dict(
                seed=cfg.random_seed,season=self.season,agent=f.unique_id,zone=f.zone.id,
                crop=f.chosen_crop,previous_crop=previous,switched=previous is not None and previous!=f.chosen_crop,
                explored=explored,greedy_crop=greedy,chosen_score=scores[f.chosen_crop],
                candidates=candidates,experience_info=self.pool_stats(all_own,f),
                neighbor_info=self.pool_stats(all_neighbor,f),zone_info=self.pool_stats(all_zone,f),
                all_channels_info=self.pool_stats(all_own+all_neighbor+all_zone,f),
                goal=f.goal_profile,land_ha=f.land_size)

    def counterfactual(self, f, crop_id, weather):
        """Analyst-only realized same-shock potential outcome; called after decisions."""
        cfg=self.cfg
        crop=v1.crops_data['crops'][crop_id]
        y,cost,water=v1.calculate_season_outcome(crop_id,crop,f.zone.raw_zone_data,
            f.zone.climate_profile,{'weather_type':weather[f.zone.id]},f.irrigation_level,cfg,
            farmer_cost_noise=f.cost_noise_factor,rng=self.stream('harvest',self.season,f.unique_id))
        price=v1.get_crop_price(crop_id)*(1+cfg.shared_price_premium if cfg.cooperative_economics_enabled else 1)
        cost*=cfg.shared_cost_efficiency if cfg.cooperative_economics_enabled else cfg.indiv_cost_efficiency
        loss=cfg.shared_post_harvest_loss if cfg.cooperative_economics_enabled else cfg.indiv_post_harvest_loss
        return (y*(1-loss)*price-cost)*f.land_size

    def step(self):
        self.season+=1
        cfg=self.cfg
        weather={z:v1.generate_weather(z,self.stream('weather',self.season,z)) for z in self.zones}
        self.weather_history.append(weather)
        farmers=list(self.farmers)
        self.stream('order',self.season).shuffle(farmers)
        for f in farmers:
            f.set_weather(weather[f.zone.id]); f.react_to_drought(); self.decide(f)
        latest={}
        for f in farmers:
            f.harvest(weather,cfg)
            obs=Observation(cfg.random_seed,f.unique_id,self.season,f.zone.id,f.chosen_crop,
                            f.land_size,f.yield_t_ha,f.cost_per_ha,f.water_use_mm,f.profit)
            f.provenance.setdefault(f.chosen_crop,[]).append(obs)
            latest[f.unique_id]=obs
            self.ledger.append(obs)
            row=dict(seed=cfg.random_seed,season=self.season,agent=f.unique_id,zone=f.zone.id,
                land_ha=f.land_size,crop=f.chosen_crop,weather=weather[f.zone.id],yield_t_ha=f.yield_t_ha,
                effective_yield_t_ha=f.effective_yield,production_t=f.yield_t_ha*f.land_size,
                cost_mad_ha=f.cost_per_ha,price_mad_t=f.price,water_proxy_mm=f.water_use_mm,
                profit_mad=f.profit,profit_mad_ha=f.profit/f.land_size,cost_noise=f.cost_noise_factor)
            self.records.append(row)
            if self.tracing:
                trace=self.last_details[f.unique_id]
                trace.update(row)
                potentials={c:self.counterfactual(f,c,weather) for c in trace['candidates']}
                for c,profit in potentials.items():
                    trace['candidates'][c]['analyst_only_same_shock_profit']=profit
                trace['analyst_only_profit_regret']=max(potentials.values())-f.profit
                trace['analyst_only_best_profit_crop']=max(potentials,key=potentials.get)
                self.traces.append(trace)
        if cfg.social_information_enabled:
            # Inherit aggregation order to preserve exact EXP001 floating arithmetic.
            super().update_shared_knowledge()
            for zid,zone in self.zones.items():
                by_crop={}
                for f in self.farmers:
                    if f.zone.id==zid:
                        by_crop.setdefault(f.chosen_crop,[]).append(latest[f.unique_id])
                self.zone_observations[zid]=by_crop
                if cfg.profit_per_ha and cfg.use_profit:
                    zone.shared_crop_profit={c:sum(o.profit/o.land for o in obs)/len(obs) for c,obs in by_crop.items()}
            if cfg.use_neighbor_graph and cfg.shared_strategy in ('neighbor','both'):
                for f in farmers:
                    obs=latest[f.unique_id]
                    for nb in f.neighbor_agents:
                        if compatible(nb.zone,f.zone,cfg.context_filter):
                            nb.knowledge_base.setdefault(obs.crop,[]).append(obs.values)
                            nb.provenance.setdefault(obs.crop,[]).append(obs)


def run_sim(cfg,tracing=True):
    model=DiagnosticModel(cfg,tracing)
    for _ in range(cfg.n_seasons): model.step()
    return model,pd.DataFrame(model.records).sort_values(['season','agent']).reset_index(drop=True)
