# Zabbix User Manager

Simple CLI tooling for provisioning Zabbix users across one or more Zabbix instances through the API.

## What It Does

- Creates users from a CSV file or a single CLI-supplied user.
- Connects to one or more Zabbix instances defined in `config/zabbix_instances.yaml`.
- Supports a `--dry-run` mode for safe validation before making changes.
- Uses API credentials from environment variables.

## Requirements

- Python 3.11+
- Network access to your Zabbix API endpoints
- Valid Zabbix API credentials

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` values into your shell or environment management tool:

```bash
export ZABBIX_API_USERNAME=admin
export ZABBIX_API_PASSWORD=changeme
```

Update `config/zabbix_instances.yaml` with your real Zabbix endpoints.

Example:

```yaml
environments:
  lab:
    instances:
      - name: "lab-zabbix-1"
        url: "https://zabbix-lab-1.example.com/api_jsonrpc.php"
        verify_ssl: false
```

## CSV Format

The CSV file should contain:

```csv
username,first_name,last_name,email,is_ldap
jdoe,John,Doe,jdoe@example.com,true
```

## Usage

Single user:

```bash
python3 zabbix_user_provisioner.py \
  --env lab \
  --username jdoe \
  --first-name John \
  --last-name Doe \
  --email jdoe@example.com \
  --ldap \
  --dry-run
```

Bulk users from CSV:

```bash
python3 zabbix_user_provisioner.py \
  --env lab \
  --csv input/users.csv \
  --dry-run
```

## Notes

- The current implementation picks the first available Zabbix user group and role returned by the API.
- Existing users are skipped.
- Replace the sample URLs before running against a real environment.
