# ApiGateway for managing BLE pereferials

Self-paced study guide implementation of [`Designing and Developing Bluetooth® Internet Gateways`](https://www.bluetooth.com/bluetooth-resources/bluetooth-internet-gateways/) course

### setup

python >= 3.11 required

```bash
git clone https://github.com/Neznakomec16/bluetooth_apigw.git && cd bluetooth_apigw
poetry shell && poetry install
```

### Run

```bash
python -m bluetooth_apigw.entrypoints.http_server
```
You can find Swagger at `/api/docs` path
