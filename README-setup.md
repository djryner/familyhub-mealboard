# Raspberry Pi Setup

## Quick start
```bash
cd /home/pi && git clone <YOUR_REPO_URL> familyhub
cd familyhub
sudo bash scripts/setup_pi.sh
```

## Re-run or upgrade
```bash
# safe to re-run anytime; handles existing service/files
sudo bash scripts/setup_pi.sh
```

## Reconfigure environment or secrets
```bash
sudo bash scripts/configure_env.sh
sudo systemctl restart familyhub
```

## Manual run
```bash
bash scripts/run_local.sh
```

## Acceptance tests
```bash
systemctl is-active familyhub
journalctl -u familyhub -n 50
sudo test -f /etc/default/familyhub
sudo test -f /etc/familyhub/service_account.json
```
Ensure the app responds on HOST:PORT.

## Troubleshooting
- Service fails to start → `journalctl -u familyhub -e -f`
- Wrong paths in unit → run setup again (migrates unit)
- Python upgraded → setup auto-recreates venv
- Dry run: `DRY_RUN=1 sudo -E bash scripts/setup_pi.sh`
