"""
Configuration loader for the agricultural simulation.
Loads YAML config and provides convenient access to parameters.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for the simulation."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Load and parse configuration file.
        
        Args:
            config_path: Path to YAML configuration file
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If YAML is malformed
        """
        self.config_path = Path(config_path)
        
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(self.config_path, "r") as f:
            self._data = yaml.safe_load(f)
        
        logger.info(f"✓ Loaded config from {config_path}")
    
    def get(self, key: str, default=None) -> Any:
        """
        Get config value using dot notation.
        
        Example:
            >>> config.get("simulation.n_agents")
            100
            >>> config.get("nonexistent.key", default=42)
            42
        """
        keys = key.split(".")
        value = self._data
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def __getitem__(self, key: str) -> Any:
        """Dict-like access to config."""
        return self._data[key]
    
    @property
    def simulation(self) -> Dict:
        return self._data.get("simulation", {})
    
    @property
    def suitability(self) -> Dict:
        return self._data.get("suitability", {})
    
    @property
    def learning(self) -> Dict:
        return self._data.get("learning", {})
    
    @property
    def yield_params(self) -> Dict:
        return self._data.get("yield", {})
    
    @property
    def finance(self) -> Dict:
        return self._data.get("finance", {})
    
    @property
    def visualization(self) -> Dict:
        return self._data.get("visualization", {})
    
    @property
    def data_paths(self) -> Dict:
        return self._data.get("data", {})
    
    @property
    def analysis(self) -> Dict:
        return self._data.get("analysis", {})
    
    @property
    def logging_config(self) -> Dict:
        return self._data.get("logging", {})
    
    @property
    def experiment(self) -> Dict:
        return self._data.get("experiment", {})
    
    def to_dict(self) -> Dict:
        """Export entire config as dictionary."""
        return self._data.copy()
    
    def summary(self) -> str:
        """Get human-readable config summary."""
        summary = "=== Simulation Configuration ===\n"
        summary += f"Agents: {self.simulation.get('n_agents')}\n"
        summary += f"Timesteps: {self.simulation.get('n_timesteps')}\n"
        summary += f"Random Seed: {self.simulation.get('random_seed')}\n"
        summary += f"Experiment: {self._data.get('experiment', {}).get('name', 'unnamed')}\n"
        return summary


# Global config instance
_config_instance = None


def load_config(config_path: str = "config.yaml") -> Config:
    """
    Load configuration (with caching).
    
    Args:
        config_path: Path to YAML config file
        
    Returns:
        Config instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_path)
    return _config_instance


def get_config() -> Config:
    """Get the current config instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
