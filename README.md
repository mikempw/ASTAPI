Must be installed along the Application-Study-Tool
Example folder structure
Repos
  Application-Study-Tool
  ASTAPI
  BIG-IPConversionTool
---

Just remember to use either the default environmental variable or change it, up to you. This will update the otel_collector receivers.yaml file directly.

**Example JSON to add a BIG-IP**

curl -X POST http://localhost:8000/bigip/1 \
  -H "Content-Type: application/json" \
  -d '{
    "endpoint": "https://10.0.0.1",
    "username": "SOME_OVERRIDE_ACCOUNT_NAME",
    "password": "${SOME_OTHER_ENV_VAR_WITH_ANOTHER_PASSWORD}",
    "collection_interval": "30s",
    "timeout": "20s",
    "data_types": {
      "f5.dns": {
        "enabled": false
      },
      "f5.gtm": {
        "enabled": false
      }
    },
    "tls": {
      "insecure_skip_verify": true,
      "ca_file": null
    }
  }'


**Example JSON to update a BIG-IP entry**

curl -X PUT http://localhost:8000/bigip/1 \
  -H "Content-Type: application/json" \
  -d '{
    "endpoint": "https://10.0.0.1",
    "username": "NEW_USERNAME_HERE",
    "password": "${NEW_PASSWORD_VAR_HERE}",
    "collection_interval": "30s",
    "timeout": "20s",
    "data_types": {
      "f5.dns": {
        "enabled": false
      },
      "f5.gtm": {
        "enabled": false
      }
    },
    "tls": {
      "insecure_skip_verify": true,
      "ca_file": null
    }
  }'

**Example JSON to delete a BIG-IP entry**

curl -X DELETE http://localhost:8000/bigip/1
  
