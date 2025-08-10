# FamilyHub Health & Service Notes

## Manual Run
```bash
python3 main.py
```
Watch the logs for the `READY=1 sent` message.

## systemd Service
```bash
sudo systemctl start familyhub
sudo systemctl status familyhub
sudo systemctl stop familyhub
```
Logs via journalctl:
```bash
journalctl -u familyhub -e -f
```

## Health Endpoints
When running as a web app:
```bash
curl -f http://127.0.0.1:8000/healthz
curl -f http://127.0.0.1:8000/readyz
```
If running without a web server:
```bash
curl -f http://127.0.0.1:8030/healthz
```

## Failure Demonstrations
Crash test:
```bash
pkill -f main.py
```
Service restarts in ~2s.

Hang test: simulate event loop stall; watchdog restarts within 30s.

## Security
Health endpoints bind to localhost. Use a reverse proxy for remote access.
