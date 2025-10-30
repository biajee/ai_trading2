"""
Configuration module for AI Trading Arena
Reads from config.json and optionally .env for API keys
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables (for backward compatibility with API keys in .env)
load_dotenv()

class Config:
    """Main configuration class - reads from config.json"""
    
    _config_data: Dict[str, Any] = {}
    _config_file = "config.json"
    
    @classmethod
    def _load_config(cls):
        """Load configuration from config.json"""
        config_path = Path(cls._config_file)
        if config_path.exists():
            with open(config_path, 'r') as f:
                cls._config_data = json.load(f)
        else:
            raise FileNotFoundError(f"{cls._config_file} not found. Please create it from config.json.example")
    
    @classmethod
    def _get(cls, *keys, default=None):
        """Get nested config value"""
        if not cls._config_data:
            cls._load_config()
        
        value = cls._config_data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key, default)
            else:
                return default
        return value if value is not None else default
    
    # Trading Mode
    @classmethod
    @property
    def MOCK_TRADING(cls) -> bool:
        return cls._get("trading", "mock_trading", default=True)
    
    # Capital Settings
    @classmethod
    @property
    def STARTING_CAPITAL(cls) -> float:
        return float(cls._get("trading", "starting_capital", default=10000))
    
    # Exchange Configuration
    @classmethod
    @property
    def EXCHANGE_API_KEY(cls) -> str:
        # Try config.json first, then .env for backward compatibility
        key = cls._get("exchange", "api_key", default="")
        return key or os.getenv("EXCHANGE_API_KEY", "")
    
    @classmethod
    @property
    def EXCHANGE_API_SECRET(cls) -> str:
        secret = cls._get("exchange", "api_secret", default="")
        return secret or os.getenv("EXCHANGE_API_SECRET", "")
    
    @classmethod
    @property
    def EXCHANGE_NAME(cls) -> str:
        return cls._get("exchange", "name", default="binance")
    
    # Generic API Key getter
    @classmethod
    def get_api_key(cls, agent_type: str) -> str:
        """Get API key for any agent type from config or env"""
        agent_config = cls.get_agent_config(agent_type)
        api_key_name = agent_config.get("api_key_name", "")
        
        if api_key_name:
            # Try from config.json ai_api_keys section
            key = cls._get("ai_api_keys", api_key_name, default="")
            if key:
                return key
            
            # Try from .env with uppercase conversion
            env_key_name = f"{api_key_name.upper()}_API_KEY"
            return os.getenv(env_key_name, "")
        
        return ""
    
    @classmethod
    def get_all_agent_types(cls) -> List[str]:
        """Get list of all configured agent types (excluding simple_agents)"""
        agents_config = cls._get("agents", default={})
        return [agent_type for agent_type in agents_config.keys() if agent_type != "simple_agents"]
    
    # Agent Configuration
    @classmethod
    def get_agent_config(cls, agent_type: str) -> Dict[str, Any]:
        """Get configuration for a specific agent type"""
        return cls._get("agents", agent_type, default={})
    
    @classmethod
    def is_agent_enabled(cls, agent_type: str) -> bool:
        """Check if an agent type is enabled"""
        return cls._get("agents", agent_type, "enabled", default=False)
    
    # Market Data
    @classmethod
    @property
    def MARKET_DATA_UPDATE_INTERVAL(cls) -> int:
        return int(cls._get("market_data", "update_interval", default=60))
    
    @classmethod
    @property
    def TRADING_PAIRS(cls) -> List[str]:
        return cls._get("trading", "trading_pairs", default=["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT"])
    
    # Risk Management
    @classmethod
    @property
    def MAX_POSITION_SIZE(cls) -> float:
        return float(cls._get("risk_management", "max_position_size", default=0.1))
    
    @classmethod
    @property
    def MAX_LEVERAGE(cls) -> float:
        return float(cls._get("risk_management", "max_leverage", default=2))
    
    @classmethod
    @property
    def MAX_DRAWDOWN(cls) -> float:
        return float(cls._get("risk_management", "max_drawdown", default=0.2))
    
    # Logging
    @classmethod
    @property
    def LOG_LEVEL(cls) -> str:
        return cls._get("logging", "level", default="INFO")
    
    @classmethod
    @property
    def LOG_FILE(cls) -> str:
        return cls._get("logging", "file", default="trading_arena.log")
    
    # Dashboard
    @classmethod
    @property
    def DASHBOARD_HOST(cls) -> str:
        return cls._get("dashboard", "host", default="127.0.0.1")
    
    @classmethod
    @property
    def DASHBOARD_PORT(cls) -> int:
        return int(cls._get("dashboard", "port", default=8050))
    
    @classmethod
    @property
    def DASHBOARD_UPDATE_INTERVAL(cls) -> int:
        return int(cls._get("dashboard", "update_interval", default=5))
    
    # Competition Settings
    @classmethod
    @property
    def COMPETITION_DURATION_DAYS(cls) -> int:
        return int(cls._get("competition", "duration_days", default=7))
    
    @classmethod
    @property
    def COMPETITION_CYCLES(cls) -> int:
        return int(cls._get("competition", "cycles", default=50))
    
    @classmethod
    @property
    def COMPETITION_CYCLE_INTERVAL(cls) -> int:
        return int(cls._get("competition", "cycle_interval", default=5))
    
    @classmethod
    def get_trading_mode_str(cls) -> str:
        """Get human-readable trading mode"""
        return "MOCK TRADING" if cls.MOCK_TRADING else "⚠️  REAL TRADING ⚠️"
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.MOCK_TRADING:
            if not cls.EXCHANGE_API_KEY or not cls.EXCHANGE_API_SECRET:
                raise ValueError("Exchange API credentials required for real trading!")
        
        if cls.STARTING_CAPITAL <= 0:
            raise ValueError("Starting capital must be positive!")
        
        if not cls.TRADING_PAIRS:
            raise ValueError("At least one trading pair must be specified!")
    
    @classmethod
    def reload(cls):
        """Reload configuration from file"""
        cls._config_data = {}
        cls._load_config()

# Validate configuration on import
Config.validate()
