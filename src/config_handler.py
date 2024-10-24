# src/config_handler.py
from collections import OrderedDict
import yaml
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
import os

class ConfigHandler:
    def __init__(self, config_dir: str = "/config", config_file: str = "receivers.yaml"):
        # Allow overriding through environment variables
        self.config_dir = os.getenv('CONFIG_DIR', config_dir)
        self.config_file = os.getenv('CONFIG_FILE', config_file)
        self.config_path = os.path.join(self.config_dir, self.config_file)
        
        # Create directory if it doesn't exist
        os.makedirs(self.config_dir, exist_ok=True)

    def read_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'r') as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            return {}
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

    def delete_bigip(self, name: str) -> Dict[str, Any]:
        """Delete a BIG-IP configuration"""
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
        """Update a BIG-IP configuration"""
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
        """Save configuration to file while maintaining order"""
        try:
            ordered_config = OrderedDict()
            
            # Only add BIG-IP configurations in sorted order
            for key in sorted(config.keys()):
                if key.startswith("bigip/"):
                    ordered_config[key] = config[key]

            class OrderedDumper(yaml.SafeDumper):
                pass

            def _dict_representer(dumper, data):
                return dumper.represent_mapping(
                    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                    data.items()
                )

            OrderedDumper.add_representer(OrderedDict, _dict_representer)

            # Ensure directory exists before writing
            os.makedirs(self.config_dir, exist_ok=True)

            with open(self.config_path, 'w') as file:
                yaml.dump(ordered_config, file, Dumper=OrderedDumper, default_flow_style=False, sort_keys=False)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error writing config: {str(e)}")

    def get_config_path(self) -> str:
        """Get the current configuration file path"""
        return self.config_path
