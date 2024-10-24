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
