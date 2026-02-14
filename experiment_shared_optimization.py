"""
🧪 Quick Experiment: Test SHARED Strategy Optimization
Run this to find the best parameters for SHARED profit
"""
import subprocess
import pandas as pd
import json
from pathlib import Path
import yaml

# Test configurations
configs = {
    "baseline": {
        "individual_weight": 0.5,
        "shared_weight": 0.5,
        "learning_speed_shared": 0.6,
        "n_timesteps": 10
    },
    "boost_shared_70": {
        "individual_weight": 0.3,
        "shared_weight": 0.7,
        "learning_speed_shared": 0.8,
        "n_timesteps": 10
    },
    "extend_time": {
        "individual_weight": 0.5,
        "shared_weight": 0.5,
        "learning_speed_shared": 0.6,
        "n_timesteps": 20
    },
    "hybrid_boost": {
        "individual_weight": 0.3,
        "shared_weight": 0.7,
        "learning_speed_shared": 0.8,
        "n_timesteps": 20
    }
}

results = {}

for config_name, params in configs.items():
    print(f"\n[*] Running {config_name}...")
    
    # Load current config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Update params
    config['learning']['individual_weight'] = params['individual_weight']
    config['learning']['shared_weight'] = params['shared_weight']
    config['learning']['learning_speed_shared'] = params['learning_speed_shared']
    config['simulation']['n_timesteps'] = params['n_timesteps']
    
    # Save modified config
    with open("config_test.yaml", "w") as f:
        yaml.dump(config, f)
    
    # Run simulation notebook (would need to adapt for notebook execution)
    print(f"  [OK] Config: {params}")
    
    # After simulation, load results
    if (Path("results") / "metrics.json").exists():
        with open("results/metrics.json", "r") as f:
            metrics = json.load(f)
        
        results[config_name] = {
            "avg_yield_shared": metrics.get('avg_yield_shared'),
            "avg_yield_individual": metrics.get('avg_yield_individual'),
            "advantage": metrics.get('yield_advantage_shared'),
            "params": params
        }

# Compare results
print("\n" + "="*70)
print("EXPERIMENT RESULTS")
print("="*70)

results_df = pd.DataFrame([
    {
        'Config': name,
        'SHARED Yield': f"{v['avg_yield_shared']:.3f}",
        'INDIVIDUAL Yield': f"{v['avg_yield_individual']:.3f}",
        'Advantage': f"{v['advantage']:+.3f}",
        'Timesteps': v['params']['n_timesteps'],
        'Shared Weight': f"{v['params']['shared_weight']:.1f}"
    }
    for name, v in results.items()
])

print(results_df.to_string(index=False))
print("="*70)

# Recommendation
best = max(results.items(), key=lambda x: x[1]['avg_yield_shared'])
print(f"\n[OK] BEST CONFIGURATION: {best[0]}")
print(f"   SHARED Yield: {best[1]['avg_yield_shared']:.3f} t/ha")
print(f"   Settings:")
for param, value in best[1]['params'].items():
    print(f"     - {param}: {value}")
