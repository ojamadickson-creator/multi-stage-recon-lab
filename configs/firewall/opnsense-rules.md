# OPNsense Firewall Rules Configuration

## Overview

The OPNsense firewall acts as the perimeter gateway between the WAN zone (attacker network) and the LAN zone (internal corporate network). Proper firewall rules are essential to:

1. Allow legitimate lab traffic for attack simulation
2. Log all cross-zone traffic for SIEM analysis
3. Maintain network segmentation principles

## Network Interfaces

| Interface | IP Address | Network | Role |
|-----------|-----------|---------|------|
| WAN | 192.168.57.254 | 192.168.57.0/24 | External / Attacker zone |
| LAN | 192.168.56.254 | 192.168.56.0/24 | Internal / Corporate zone |

## Firewall Rules

### Floating Rules (Cross-Zone)

These rules apply to traffic passing between WAN and LAN zones. They are evaluated before interface-specific rules.

| Rule # | Action | Protocol | Source | Port | Destination | Port | Description |
|--------|--------|----------|--------|------|-------------|------|-------------|
| 1 | Pass | TCP/UDP | 192.168.57.10 | * | 192.168.56.102 | domain (53) | Kali_Allow - DNS to DC |
| 2 | Pass | TCP/UDP | 192.168.57.10 | * | 192.168.56.102 | ldap (389) | Kali_Allow - LDAP to DC |
| 3 | Pass | TCP | 192.168.57.10 | * | 192.168.56.102 | microsoft-ds (445) | Kali_Allow - SMB to DC |
| 4 | Pass | TCP | 192.168.57.10 | * | 192.168.56.102 | * | Kali_Allow - RDP to DC |
| 5 | Pass | ICMP | 192.168.57.10 | * | 192.168.56.102 | * | Kali_Allow - ICMP to DC |

### Interface Rules - LAN

| Rule # | Action | Protocol | Source | Port | Destination | Port | Description |
|--------|--------|----------|--------|------|-------------|------|-------------|
| 1 | Pass | * | LAN net | * | * | * | Default allow LAN to any rule |
| 2 | Pass | IPv6 | LAN net | * | * | * | Default allow LAN IPv6 to any rule |

### Interface Rules - WAN

| Rule # | Action | Protocol | Source | Port | Destination | Port | Description |
|--------|--------|----------|--------|------|-------------|------|-------------|
| 1 | Pass | ICMP | * | * | 192.168.56.0/24 | * | Allow ping recon |

## NAT Configuration

Port forwarding is configured to allow the Kali attacker (WAN) to reach internal services:

| Protocol | WAN Port | LAN IP | LAN Port | Description |
|----------|----------|--------|----------|-------------|
| TCP | 3389 | 192.168.56.102 | 3389 | RDP to Domain Controller |
| TCP | 445 | 192.168.56.102 | 445 | SMB to Domain Controller |
| TCP | 389 | 192.168.56.102 | 389 | LDAP to Domain Controller |

## Syslog Configuration

Configure OPNsense to forward firewall logs to the Splunk server:

1. Navigate to **System > Settings > Logging / Targets**
2. Add a new remote logging target:
   - **Transport:** UDP (Legacy)
   - **Hostname:** 192.168.56.106
   - **Port:** 514
   - **Description:** Splunk SIEM
   - **Categories:** Filter, Firewall

3. Enable firewall logging on each rule:
   - Edit the floating rules
   - Check **Log packets matched by this rule**
   - Save and apply

## Verification Commands

On the OPNsense firewall (via CLI or Console):

```bash
# View active firewall rules
pfctl -sr

# View NAT rules
pfctl -sn

# View current states (connections)
pfctl -ss

# Check filter log
tcpdump -ni pflog0

# Test syslog forwarding
logger -n 192.168.56.106 -P 514 "Test syslog message from OPNsense"
```

On the Splunk server:

```bash
# Verify syslog is being received on port 514
sudo tcpdump -i any port 514 -n

# Check Splunk inputs
sudo /opt/splunk/bin/splunk show config inputs
```

## Security Recommendations

In a production environment (not this lab), you should:

1. **Deny by default** - Only explicitly allow required traffic
2. **Use least privilege** - Restrict source IPs to specific management hosts
3. **Enable logging** - Log all allowed and denied traffic
4. **Implement IDS/IPS** - Use Suricata on OPNsense for deep packet inspection
5. **Geo-blocking** - Block traffic from high-risk countries
6. **Rate limiting** - Implement connection rate limits to prevent reconnaissance
7. **VPN for management** - Require VPN for all administrative access

## Troubleshooting

**Issue:** Kali cannot reach the Domain Controller

1. Verify firewall rules are applied (Firewall > Rules > Floating > Apply)
2. Check NAT rules are correct (Firewall > NAT > Port Forward)
3. Verify routing on Kali: `ip route | grep default`
4. Test with tcpdump on OPNsense: `tcpdump -ni any host 192.168.57.10`

**Issue:** Splunk not receiving syslog

1. Verify Splunk input is configured for UDP/514
2. Check OPNsense syslog target configuration
3. Verify network connectivity: `ping 192.168.56.106` from OPNsense
4. Check Splunk's internal logs: `index=_internal source=*splunkd.log* syslog`
