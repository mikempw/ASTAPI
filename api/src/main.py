from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from .config_handler import ConfigHandler

app = FastAPI(title="BIG-IP Receiver Config API")
config_handler = ConfigHandler()

class DataTypeConfig(BaseModel):
    enabled: bool = False

class TLSConfig(BaseModel):
    insecure_skip_verify: bool = True
    ca_file: Optional[str] = None

class BigIPConfig(BaseModel):
    endpoint: str
    username: str
    password: str
    collection_interval: str = "30s"
    timeout: str = "20s"
    data_types: Dict[str, DataTypeConfig] = Field(default_factory=lambda: {
        "f5.dns": DataTypeConfig(enabled=False),
        "f5.gtm": DataTypeConfig(enabled=False)
    })
    tls: TLSConfig = Field(default_factory=TLSConfig)

class GlobalConfig(BaseModel):
    debug: bool = False
    log_level: str = "DEBUG"
    polling_interval: int = 120

@app.get("/config")
async def get_config():
    """Get current configuration"""
    return config_handler.read_config()

@app.post("/bigip/{name}")
async def add_bigip(name: str, config: BigIPConfig):
    """Add a new BIG-IP configuration"""
    return config_handler.add_bigip(name, config.dict())

@app.put("/config/global")
async def update_global_config(config: GlobalConfig):
    """Update global configuration settings"""
    return config_handler.update_global_config(config.dict())

@app.delete("/bigip/{name}")
async def delete_bigip(name: str):
    """Delete a BIG-IP configuration"""
    return config_handler.delete_bigip(name)

@app.put("/bigip/{name}")
async def update_bigip(name: str, config: BigIPConfig):
    """Update a BIG-IP configuration"""
    return config_handler.update_bigip(name, config.dict())

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# src/config_handler.py
from collections import OrderedDict
import yaml
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

class ConfigHandler:
    def __init__(self, config_path: str = "/config/bigip_receivers.yaml"):
        self.config_path = config_path
        self.default_config = {
            "bigip_receivers": [],
            "debug": False,
            "log_level": "DEBUG",
            "polling_interval": 120
        }

    def read_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file) or self.default_config.copy()
                for key, value in self.default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except FileNotFoundError:
            return self.default_config.copy()
        except yaml.YAMLError as e:
            raise HTTPException(status_code=500, detail=f"Error parsing YAML: {str(e)}")

    def add_bigip(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new BIG-IP configuration"""
        current_config = self.read_config()
        bigip_key = f"bigip/{name}"
        
        if bigip_key in current_config:
            raise HTTPException(
                status_code=400,
                detail=f"BIG-IP configuration '{bigip_key}' already exists"
            )

        # Create ordered dictionary with specific field order
        ordered_config = OrderedDict([
            ("endpoint", config["endpoint"]),
            ("username", config["username"]),
            ("password", config["password"]),
            ("collection_interval", config["collection_interval"]),
            ("timeout", config["timeout"]),
            ("data_types", OrderedDict([
                ("f5.dns", config["data_types"]["f5.dns"]),
                ("f5.gtm", config["data_types"]["f5.gtm"])
            ])),
            ("tls", OrderedDict([
                ("insecure_skip_verify", config["tls"]["insecure_skip_verify"]),
                ("ca_file", config["tls"]["ca_file"])
            ]))
        ])
        
        current_config[bigip_key] = ordered_config
        self._save_config(current_config)
        return current_config

    def update_global_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update global configuration settings"""
        current_config = self.read_config()
        
        for key in ["debug", "log_level", "polling_interval"]:
            if key in config:
                current_config[key] = config[key]
        
        self._save_config(current_config)
        return current_config

    def delete_bigip(self, name: str) -> Dict[str, Any]:
        config = self.read_config()
        bigip_key = f"bigip/{name}"
        
        if bigip_key not in config:
            raise HTTPException(
                status_code=404,
                detail=f"BIG-IP configuration '{bigip_key}' not found"
            )
        
        del config[bigip_key]
        self._save_config(config)
        return config

    def update_bigip(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        current_config = self.read_config()
        bigip_key = f"bigip/{name}"
        
        if bigip_key not in current_config:
            raise HTTPException(
                status_code=404,
                detail=f"BIG-IP configuration '{bigip_key}' not found"
            )

        # Create ordered dictionary with specific field order
        ordered_config = OrderedDict([
            ("endpoint", config["endpoint"]),
            ("username", config["username"]),
            ("password", config["password"]),
            ("collection_interval", config["collection_interval"]),
            ("timeout", config["timeout"]),
            ("data_types", OrderedDict([
                ("f5.dns", config["data_types"]["f5.dns"]),
                ("f5.gtm", config["data_types"]["f5.gtm"])
            ])),
            ("tls", OrderedDict([
                ("insecure_skip_verify", config["tls"]["insecure_skip_verify"]),
                ("ca_file", config["tls"]["ca_file"])
            ]))
        ])
        
        current_config[bigip_key] = ordered_config
        self._save_config(current_config)
        return current_config

    def _save_config(self, config: Dict[str, Any]) -> None:
        try:
            ordered_config = OrderedDict()
            
            # Add BIG-IP configurations first
            for key in sorted(config.keys()):
                if key.startswith("bigip/"):
                    ordered_config[key] = config[key]
            
            # Add remaining global configurations
            ordered_config["bigip_receivers"] = config["bigip_receivers"]
            ordered_config["debug"] = config["debug"]
            ordered_config["log_level"] = config["log_level"]
            ordered_config["polling_interval"] = config["polling_interval"]

            class OrderedDumper(yaml.SafeDumper):
                pass

            def _dict_representer(dumper, data):
                return dumper.represent_mapping(
                    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                    data.items()
                )

            OrderedDumper.add_representer(OrderedDict, _dict_representer)

            with open(self.config_path, 'w') as file:
                yaml.dump(ordered_config, file, Dumper=OrderedDumper, default_flow_style=False, sort_keys=False)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error writing config: {str(e)}")
