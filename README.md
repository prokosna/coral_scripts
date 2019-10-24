# IoT Hands-on Scripts

A set of scripts for IoT hands-on.

| File | Description |
|:---|:---|
| gstreamer.py | Capturing an image from a camera |
| input.py | Monitoring Enter key or a physical switch |
| install_requirements.sh | Installing all dependencies |
| led.py | Handling GPIO connected RGB LED |
| mqtt.py | Handling a MQTT connection |
| upload.py | Uploading an image to GCS |
| run_capture.py | Capturing images and uploading them to GCS (for dev) |
| run_cloud.py | Main script that executes cloud prediction |
| run_edge.py | Main script that executes edge prediction |


## Prerequisite

### GCP

Setup following services:
- IoT Core (Registry, Device w/ generating public/private keys)
- GCS (Bucket)
- AutoML Vision (Train and deploy a model, download an edge model)
- GCF (Deploy a function using iot-hands-on-gcf repository)
- GCF trigger

### Install dependencies

```
# if needed
$ chmod +x install.requirements.sh
$ ./install_requirements.sh
```

### Prepare service account key

1. Create a service account with appropriate roles
2. Download a JSON key file
3. Set an environment value

```
$ export GOOGLE_APPLICATION_CREDENTIALS="PATH_TO_JSON_KEY_FILE.json"
```

### Download roots.pem

```
$ wget https://pki.goog/roots.pem
```

### Modify GPIO pin numbers

There is a line that initializes **LED** instance in both run_cloud.py and run_edge.py.

Please replace arguments with correct GPIO pin numbers.

## Run "UME"

Please run **python3 run_cloud.py --help** to see parameters description.

```
$ sudo -E python3 run_cloud.py --project="PROJECT" --region="REGION" --registry_id="REGISTRY_ID" --device_id="DEVICE_ID" --private_key="PATH_TO_PRIVATE_KEY" --bucket="GCS_BUCKET" --path="GCS_PATH"
```

## Run "Take"

Please run **python3 run_edge.py --help** to see parameters description.

```
$ sudo -E python3 run_edge.py --model="MODEL" --labels="LABELS"
```
