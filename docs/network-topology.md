# Network Topology and Specifications

## Lab Network Architecture

This document provides detailed specifications for the SOC lab network topology used in the Multi-Stage Reconnaissance project.

## Physical / Virtual Setup

All systems are deployed as virtual machines using **Oracle VirtualBox** (or VMware Workstation). The host machine should have:

- **CPU:** 4+ cores (8+ recommended)
- **RAM:** 16GB minimum (32GB recommended)
- **Storage:** 100GB+ free space
- **Network:** Host-only and NAT networks configured

## VirtualBox Network Configuration

### Host-Only Network (LAN Zone)

```
Name: VirtualBox Host-Only Ethernet Adapter
IPv4 Address: 192.168.56.1
IPv4 Network Mask: 255.255.255.0
DHCP: Disabled (all VMs use static IPs)
```

### NAT Network (WAN Zone)

```
Name: NAT Network
IPv4 Address: 192.168.57.1
IPv4 Network Mask: 255.255.255.0
DHCP: Enabled (Kali gets IP via DHCP, but we set static)
```

## System Specifications

### 1. OPNsense Firewall

| Property | Value |
|----------|-------|
| **VM Name** | OPNsense-Firewall |
| **OS** | OPNsense (FreeBSD-based) |
| **Version** | 23.x or later |
| **vCPUs** | 1 |
| **RAM** | 1GB |
| **Disk** | 8GB |
| **Adapter 1 (WAN)** | NAT Network (192.168.57.0/24) |
| **Adapter 2 (LAN)** | Host-Only (192.168.56.0/24) |
| **WAN IP** | 192.168.57.254/24 |
| **LAN IP** | 192.168.56.254/24 |
| **Role** | Gateway, NAT, Firewall, DHCP (optional) |

### 2. Domain Controller

| Property | Value |
|----------|-------|
| **VM Name** | WIN2016-DC |
| **OS** | Windows Server 2016/2019 Standard |
| **vCPUs** | 2 |
| **RAM** | 4GB |
| **Disk** | 60GB |
| **Network Adapter** | Host-Only |
| **IP Address** | 192.168.56.102/24 |
| **Default Gateway** | 192.168.56.254 |
| **DNS Server** | 127.0.0.1 (itself) |
| **Domain** | windomain.local |
| **Hostname** | DC |
| **Installed Roles** | AD DS, DNS, File Services |
| **Windows Defender** | Enabled |
| **Firewall** | Configured for lab traffic |

### 3. Windows 10 Workstation

| Property | Value |
|----------|-------|
| **VM Name** | WIN10-Mgmt |
| **OS** | Windows 10 Pro |
| **vCPUs** | 2 |
| **RAM** | 4GB |
| **Disk** | 60GB |
| **Network Adapter** | Host-Only |
| **IP Address** | 192.168.56.104/24 |
| **Default Gateway** | 192.168.56.254 |
| **DNS Server** | 192.168.56.102 |
| **Domain** | windomain.local |
| **Hostname** | WIN10 |
| **Purpose** | Management console for Splunk & Firewall web UIs |

### 4. Splunk Server

| Property | Value |
|----------|-------|
| **VM Name** | Splunk-SIEM |
| **OS** | Ubuntu Server 20.04/22.04 LTS |
| **vCPUs** | 2 |
| **RAM** | 4GB |
| **Disk** | 80GB |
| **Network Adapter** | Host-Only |
| **IP Address** | 192.168.56.106/24 |
| **Default Gateway** | 192.168.56.254 |
| **DNS Server** | 192.168.56.102 |
| **Hostname** | splunk |
| **Installed Software** | Splunk Enterprise 9.x |
| **Web Port** | 8000/TCP |
| **Management Port** | 8089/TCP |
| **Forwarder Port** | 9997/TCP |
| **Syslog Port** | 514/UDP |

### 5. Kali Linux (Attacker)

| Property | Value |
|----------|-------|
| **VM Name** | Kali-Attacker |
| **OS** | Kali Linux (Rolling) |
| **vCPUs** | 2 |
| **RAM** | 4GB |
| **Disk** | 60GB |
| **Network Adapter** | NAT Network |
| **IP Address** | 192.168.57.10/24 |
| **Default Gateway** | 192.168.57.254 |
| **DNS Server** | 192.168.57.254 |
| **Hostname** | kali |
| **Installed Tools** | nmap, netexec, ldap-utils, wireshark |

## Routing Configuration

### OPNsense Firewall Routes

```
Static Routes:
  (None required - directly connected networks)

NAT Rules:
  Outbound NAT (Automatic):
    - LAN to WAN: Masquerade all traffic
  
  Port Forwards (for lab access):
    - WAN:3389 -> 192.168.56.102:3389 (RDP to DC)
    - WAN:445  -> 192.168.56.102:445  (SMB to DC)
    - WAN:389  -> 192.168.56.102:389  (LDAP to DC)
```

### Windows Systems Routing

```powershell
# Domain Controller
route print
# Expected: 0.0.0.0 -> 192.168.56.254

# Windows 10
route print
# Expected: 0.0.0.0 -> 192.168.56.254
```

### Kali Linux Routing

```bash
# Verify default route
ip route | grep default
# Expected: default via 192.168.57.254

# Verify DNS resolution
nslookup windomain.local 192.168.56.102
```

### Splunk Server Routing

```bash
# Verify default route
ip route | grep default
# Expected: default via 192.168.56.254

# Verify connectivity to DC
ping -c 3 192.168.56.102
```

## Firewall Rules Detail

### Floating Rules (Cross-Zone)

| # | Action | Proto | Source | Dest | Port | Desc |
|---|--------|-------|--------|------|------|------|
| 1 | Pass | TCP/UDP | 192.168.57.10 | 192.168.56.102 | 53 | DNS |
| 2 | Pass | TCP/UDP | 192.168.57.10 | 192.168.56.102 | 389 | LDAP |
| 3 | Pass | TCP | 192.168.57.10 | 192.168.56.102 | 445 | SMB |
| 4 | Pass | TCP | 192.168.57.10 | 192.168.56.102 | 3389 | RDP |
| 5 | Pass | ICMP | 192.168.57.10 | 192.168.56.102 | * | Ping |

### LAN Interface Rules

| # | Action | Proto | Source | Dest | Port | Desc |
|---|--------|-------|--------|------|------|------|
| 1 | Pass | * | LAN net | * | * | Default allow |

### WAN Interface Rules

| # | Action | Proto | Source | Dest | Port | Desc |
|---|--------|-------|--------|------|------|------|
| 1 | Pass | ICMP | * | 192.168.56.0/24 | * | Allow ping recon |

## Verification Commands

### From Kali Linux

```bash
# Test connectivity to DC through firewall
ping -c 4 192.168.56.102

# Test specific ports
nc -zv 192.168.56.102 53    # DNS
nc -zv 192.168.56.102 389   # LDAP
nc -zv 192.168.56.102 445   # SMB
nc -zv 192.168.56.102 3389  # RDP

# Full port scan
nmap -Pn -sV 192.168.56.102
```

### From Windows 10 Workstation

```powershell
# Test Splunk web access
Invoke-WebRequest -Uri "http://192.168.56.106:8000" -UseBasicParsing

# Test DC connectivity
Test-NetConnection -ComputerName 192.168.56.102 -Port 445
Test-NetConnection -ComputerName 192.168.56.102 -Port 389

# Verify domain membership
Get-ComputerInfo | Select CsDomain, CsName
```

### From Splunk Server

```bash
# Test Universal Forwarder listener
nc -zv 192.168.56.106 9997

# Test Syslog listener
nc -u -zv 192.168.56.106 514

# Verify Windows events are arriving
/opt/splunk/bin/splunk search "index=main sourcetype=WinEventLog | head 5" -auth admin:changeme
```

## Troubleshooting

### Issue: Kali cannot reach DC

1. Verify OPNsense floating rules are applied
2. Check Kali default gateway: `ip route`
3. Test OPNsense WAN interface: `ping 192.168.57.254`
4. Check OPNsense filter logs: Diagnostics > Logs > Firewall

### Issue: Splunk not receiving Windows events

1. Verify Universal Forwarder is running on DC
2. Check outputs.conf on DC points to 192.168.56.106:9997
3. Test connectivity: `Test-NetConnection -ComputerName 192.168.56.106 -Port 9997`
4. Check Splunk internal logs: `index=_internal source=*splunkd.log* error`

### Issue: No firewall logs in Splunk

1. Verify syslog target in OPNsense: System > Settings > Logging
2. Check Splunk UDP input: Settings > Data Inputs > UDP
3. Test with: `echo "test" | nc -u 192.168.56.106 514`
4. Verify no firewall blocking syslog on Splunk server
