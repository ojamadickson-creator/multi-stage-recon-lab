# Syslog Forwarding Configuration

## OPNsense to Splunk Syslog Setup

This document describes how to configure OPNsense to forward firewall logs to Splunk for centralized analysis.

## OPNsense Configuration

### Step 1: Configure Remote Logging Target

1. Log in to the OPNsense web interface
2. Navigate to **System > Settings > Logging / Targets**
3. Click **+** to add a new target

### Step 2: Remote Target Settings

| Setting | Value |
|---------|-------|
| Enabled | Checked |
| Transport | UDP (4) Legacy Syslog |
| Hostname | 192.168.56.106 |
| Port | 514 |
| Application Facilities | Firewall (filter) |
| Description | Splunk SIEM Ingestion |

### Step 3: Enable Logging on Firewall Rules

For each floating rule that allows Kali traffic:

1. Navigate to **Firewall > Rules > Floating**
2. Edit the rule
3. Scroll to **Advanced Options**
4. Check **Log packets that are handled by this rule**
5. Save and apply

## Splunk Configuration

### inputs.conf

Add the following to `$SPLUNK_HOME/etc/apps/search/local/inputs.conf`:

```ini
[udp://514]
disabled = 0
sourcetype = opnsense
index = main
connection_host = ip
no_appending_timestamp = true
```

### props.conf

Add the following to `$SPLUNK_HOME/etc/apps/search/local/props.conf`:

```ini
[opnsense]
SHOULD_LINEMERGE = false
TIME_PREFIX = ^
TIME_FORMAT = %b %d %H:%M:%S
EXTRACT-src_ip = rule.*?\[(\d+\.\d+\.\d+\.\d+)\]
EXTRACT-dst_ip = rule.*?\[.*?\].*?\[(\d+\.\d+\.\d+\.\d+)\]
EXTRACT-action = (pass|block)\s+in
EXTRACT-interface = on\s+(\w+)
EXTRACT-rule_id = \(.*?\)\s+rule\s+(\d+.*?)
FIELDALIAS-src_ip = src_ip AS src
FIELDALIAS-dst_ip = dst_ip AS dest_ip
```

### transforms.conf

```ini
[opnsense_filter]
REGEX = filterlog
DEST_KEY = MetaData:Sourcetype
FORMAT = sourcetype::opnsense
```

## Verification

### On OPNsense

```bash
# Test syslog connectivity
echo "<14>Test message from OPNsense" | nc -u -w1 192.168.56.106 514

# View filter logs in real-time
tail -f /var/log/filter.log
```

### On Splunk Server

```bash
# Listen for incoming syslog
sudo tcpdump -i any port 514 -nn -A

# Search for OPNsense logs in Splunk
index=main sourcetype=opnsense | head 20
```

### Sample OPNsense Filter Log Entry

```
<134>Aug 16 22:21:34 OPNsense filterlog[12345]: 5,,,1000000103,eth1,match,pass,in,4,0x0,,64,0,0,DF,6,tcp,60,192.168.57.10,192.168.56.102,54321,445,0,S,123456789,0,64240,,mss;sackOK;TS;nop;wscale
```

**Field breakdown:**
- `Aug 16 22:21:34` — Timestamp
- `OPNsense` — Hostname
- `filterlog` — Process name
- `pass` — Action (pass/block)
- `in` — Direction (inbound/outbound)
- `192.168.57.10` — Source IP (Kali attacker)
- `192.168.56.102` — Destination IP (Domain Controller)
- `54321` — Source port
- `445` — Destination port (SMB)
- `S` — TCP flags (SYN)

## Useful Splunk Searches

### Cross-Zone Traffic Overview

```spl
index=main sourcetype=opnsense
| stats count by src_ip, dest_ip, dest_port, action
| sort -count
```

### Kali Attacker Traffic Only

```spl
index=main sourcetype=opnsense src_ip="192.168.57.10"
| timechart span=1m count by dest_port
```

### Blocked Connection Attempts

```spl
index=main sourcetype=opnsense action="block"
| stats count by src_ip, dest_ip, dest_port
| where count > 10
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No logs in Splunk | Verify UDP port 514 is open on Splunk server firewall |
| Logs show wrong timestamp | Check timezone settings on both systems |
| Missing src_ip field | Verify props.conf extraction regex |
| Duplicate events | Ensure only one syslog target is configured |
