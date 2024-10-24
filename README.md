
# Application Study Tool BIG-IP API



## Getting started
```bash
1.) cd Mike\Home\Github\MikesRepos

2.) Start by downloading the container
git clone https://github.com/mikempw/ASTAPI.git

Example folder structure - Must sit along side the Application-Study-Tool

Mike\Home\Github\MikesRepos
  Application-Study-Tool
  ASTAPI
  BIG-IPConversionTool
  Sodatestapi
  Twisterapi

3.) docker compose up

4.) send desired commands

5.) after commands have been sent, you can review your receivers file by doing to application-study-tool/services/otel_collector
cat receivers.yaml

6.) docker restart your ghcr.io/f5devcentral/application-study-tool/otel_custom_collector image 
    Example command to find the image - docker ps -a
```
![image](https://github.com/user-attachments/assets/48d4003c-6746-4237-946b-f5a8affa524b)
![image](https://github.com/user-attachments/assets/85da4d38-9aba-415a-9ff7-8a113352aeb6)



## Usage/Example for Adding a BIG-IP

```JSON
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
```

## Usage/Example for Modifying a BIG-IP entry

```JSON
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
```
## Usage/Example for Deleting a BIG-IP entry

```JSON
curl -X DELETE http://localhost:8000/bigip/1
```
