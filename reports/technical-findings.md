# Technical Findings Report

## Multi Stage Reconnaissance & Active Directory Penetration Testing Lab

**Lab Environment:** windomain.local
**Assessment Period:** August 2026
**Analyst:** Akpoga Dickson Ojama

---

## 1. Lab Architecture

The assessment was conducted in a controlled virtual environment consisting of five systems across two network zones:

### Network Topology

```
WAN (192.168.57.0/24)                    LAN (192.168.56.0/24)
├─ Kali Linux (192.168.57.10)            ├─ OPNsense LAN (192.168.56.254)
│   [Attacker]                           ├─ DC (192.168.56.102)
│                                        │   [Windows Server 2016]
│                                        ├─ Win10 (192.168.56.104)
└─ OPNsense WAN (192.168.57.254)         └─ Splunk (192.168.56.106)
    [Firewall/Gateway]                       [Ubuntu + Splunk Enterprise]
```

### Data Flows

| Source | Destination | Protocol | Data |
|--------|------------|----------|------|
| DC | Splunk | TCP/9997 | Windows Security Event Logs |
| OPNsense | Splunk | UDP/514 | Firewall filter logs |

---

## 2. Attack Execution Timeline

### Phase 1: Username Acquisition via Social Engineering (T+0)

Before I touched a single command, I needed a username to target. In a real world scenario, this often comes from open source intelligence (OSINT) gathering. LinkedIn profiles, company directories, or email patterns. For this lab, I assumed the role of an attacker who had already obtained a username through spear phishing or social engineering reconnaissance.

**The username acquired:** `vagrant`

This is a critical first step that many technical write ups skip. Understanding how usernames are acquired, whether through phishing, dumpster diving, or simply guessing based on naming conventions, is essential for building realistic attack simulations and effective defenses.

**MITRE Mapping:** T1566 — Phishing (pre attack intelligence gathering)

---

### Phase 2: Network Reconnaissance (T+0 to T+5 minutes)

**Tools Used:** Nmap 7.94

**Commands Executed:**
```bash
nmap -Pn -sV -p 53,389,445,3389 192.168.56.102
```

**Findings:**
* Host is alive with low latency (~0.003s)
* Port 53/tcp open: domain (Simple DNS Plus)
* Port 389/tcp open: ldap (Microsoft Windows Active Directory LDAP)
* Port 445/tcp open: microsoft ds (Microsoft Windows Server 2008 R2   2012)
* Port 3389/tcp open: ms wbt server (Microsoft Terminal Services)
* OS fingerprint: Windows, CPE: cpe:/o:microsoft:windows

**Technical Significance:**
The target is a Windows Domain Controller with LDAP, SMB, and RDP exposed. This configuration is typical for AD environments but represents significant attack surface. The service versions suggest a Windows Server 2012 era system, which may have known vulnerabilities.

---

### Phase 3: LDAP Enumeration (T+5 to T+10 minutes)

**Tools Used:** ldapsearch (OpenLDAP utilities)

**Commands Executed:**
```bash
ldapsearch -x -H ldap://192.168.56.102 -D "windomain\vagrant" -w "vagrant" -b "dc=windomain,dc=local" "(&(objectclass=user)(SAMAccountName=*))" | grep sAMAccountName
```

**Findings:**
* Successfully bound to LDAP with credentials vagrant:vagrant
* Enumerated domain user accounts:
  * Administrator
  * Guest
  * vagrant
  * krbtgt
  * Multiple service accounts

**Technical Significance:**
LDAP binding with valid (even low privilege) credentials allows full directory enumeration. This reveals:
* User account names (for password spraying targets)
* Group memberships
* Organizational structure
* Password policy information

The ability to query SAMAccountName for all users provides a complete target list for credential attacks.

---

### Phase 4: Credential Access via Password Spraying (T+10 to T+15 minutes)

**Tools Used:** THC Hydra

**Commands Executed:**
```bash
hydra -l vagrant -P /tmp/passwordlist smb://192.168.56.102
```

**Findings:**
* Tested 48 passwords against user "vagrant"
* Valid credential pair discovered: **vagrant:vagrant**
* Authentication successful via SMB (NTLM)
* Access confirmed to WINDOMAIN domain

**Technical Significance:**
Password spraying proved highly effective due to:
1. Weak password policy (common passwords like "vagrant" allowed)
2. No account lockout threshold configured
3. No multi factor authentication
4. SMB service exposed and accessible from attacker network

The successful authentication returns an NTLM hash that can be reused for Pass the Hash attacks.

---

### Phase 5: Post Compromise Enumeration (T+15 to T+20 minutes)

**Tools Used:** NetExec (nxc) with command execution

**Commands Executed:**
```bash
nxc smb 192.168.56.102 -u vagrant -p vagrant -x "whoami /priv"
```

**Findings:**
* Remote command execution confirmed
* Current user: WINDOMAIN\vagrant
* Token privileges include:
  * SeMachineAccountPrivilege
  * SeSecurityPrivilege
  * SeTakeOwnershipPrivilege
  * SeLoadDriverPrivilege
  * SeSystemtimePrivilege
  * SeBackupPrivilege
  * SeRestorePrivilege
  * SeShutdownPrivilege
  * SeRemoteShutdownPrivilege

**Technical Significance:**
The vagrant account holds numerous powerful privileges, including:
* **SeSecurityPrivilege:** Manage auditing and security log
* **SeTakeOwnershipPrivilege:** Take ownership of files
* **SeBackupPrivilege:** Bypass file ACLs for backup
* **SeRestorePrivilege:** Restore files with original permissions

These privileges indicate the account may be a member of privileged groups (Power Users, Backup Operators, or potentially Administrators).

---

## 3. Detection Engineering Results

### 3.1 Data Ingestion Verification

**Windows Event Logs:**
* Source: Domain Controller via Universal Forwarder
* Port: TCP/9997
* Sourcetype: WinEventLog
* Status: **OPERATIONAL** — 1,205+ events indexed

**Firewall Logs:**
* Source: OPNsense via Syslog
* Port: UDP/514
* Sourcetype: opnsense
* Status: **OPERATIONAL** — filterlog entries received

### 3.2 Detection Query Effectiveness

#### Brute Force Detection (EventCode 4625)

```spl
index=main sourcetype="WinEventLog" EventCode=4625
| stats count by src_ip
| where count > 5
```

**Results:**
* Query returned failed logon events
* Source IP 192.168.57.10 (Kali) generated 105 failed attempts
* Query correctly identified the attacker source

**Evaluation:** EFFECTIVE

#### Successful Authentication Detection (EventCode 4624)

```spl
index=main sourcetype="WinEventLog" EventCode=4624
| stats count by src_ip
```

**Results:**
* Multiple successful logon events from attacker IP
* Logon Type 3 (Network) confirmed SMB authentication
* Process Name: C:\Windows\System32\lsass.exe
* Authentication Package: NTLM

**Evaluation:** EFFECTIVE

#### Correlation Query (Attack Chain)

```spl
index=main host=dc (EventCode=4624 OR EventCode=4625) src_ip="192.168.57.10"
| eval attack_phase=case(...)
```

**Results:**
* Successfully correlated multi phase attack
* Identified progression from brute force to successful auth
* Grouped events by attack phase with counts

**Evaluation:** HIGHLY EFFECTIVE

### 3.3 Alert Configuration

| Alert Name | Trigger Condition | Status | Performance |
|-----------|------------------|--------|-------------|
| Brute Force | Results > 5 in 1 minute | Triggered | Correctly fired during attack |
| Failed Logon | Results > 0 in 1 minute | Triggered | Multiple triggers recorded |

### 3.4 Dashboard Panels

The "Detection Engineering1" dashboard successfully displayed:

1. **Failed Logins Panel**
   * Real time count of EventCode 4625
   * Filtered by attacker IP
   * Bar chart visualization

2. **Time Series Visualization**
   * Event frequency over time
   * Attack pattern identification
   * 1 minute time buckets

3. **Successful Login Panel**
   * Table of EventCode 4624 events
   * Source IP, account name, timestamp
   * Attacker activity confirmation

**Evaluation:** ALL PANELS OPERATIONAL

---

## 4. Network Traffic Analysis

### Packet Capture Findings

**SYN Packets (Nmap Scan):**
* Multiple SYN packets to ports 53, 389, 445, 3389
* Source: 192.168.57.10 (Kali)
* Destination: 192.168.56.102 (DC)
* Pattern consistent with port scanning

**LDAP Packets:**
* LDAP bindRequest from 192.168.57.10
* LDAP searchRequest for user enumeration
* Clear text bind credentials visible in traffic

**SMB Packets:**
* SMB2 NEGOTIATE, SESSION_SETUP, TREE_CONNECT
* NTLMSSP authentication sequence
* Command execution via SMB pipe (srvsvc)

**TCP Handshake Analysis:**
* Standard three way handshake observed
* No anomalous TCP flags
* Connection established normally

---

## 5. Findings Summary

| # | Finding | Severity | Evidence |
|---|---------|----------|----------|
| 1 | Weak password policy allows common passwords | CRITICAL | vagrant:vagrant valid |
| 2 | No account lockout threshold | HIGH | 105 failed attempts allowed |
| 3 | LDAP anonymous/authenticated enumeration possible | MEDIUM | Full user list retrieved |
| 4 | SMB accessible from attacker network | MEDIUM | NetExec successful via SMB |
| 5 | vagrant account has excessive privileges | HIGH | Multiple dangerous privileges |
| 6 | No MFA on domain accounts | CRITICAL | Single factor authentication |
| 7 | RDP exposed to attacker network | MEDIUM | Port 3389 accessible |
| 8 | Detection coverage is comprehensive | POSITIVE | All attack phases detected |
| 9 | Correlation queries work effectively | POSITIVE | Attack chain identified |
| 10 | Real time alerting functional | POSITIVE | Alerts fired within 1 minute |

---

## 6. Tools and Commands Reference

### Red Team Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Nmap | 7.94 | Port scanning, service detection |
| NetExec (nxc) | 1.x | SMB enumeration, command execution |
| Hydra | THC Hydra | Password spraying via SMB |
| ldapsearch | OpenLDAP 2.x | LDAP directory enumeration |
| Wireshark | 4.x | Packet capture and analysis |

### Blue Team Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Splunk Enterprise | 10.4.2 | SIEM, log analysis, alerting |
| Splunk Universal Forwarder | 9.x | Windows event log forwarding |
| OPNsense | 23.x+ | Firewall, routing, syslog |

---

## 7. Log Evidence Inventory

| Log Source | Location | Volume | Key Events |
|-----------|----------|--------|-----------|
| Windows Security | Splunk index=main | 1,205+ events | 4624, 4625, 4672 |
| OPNsense Firewall | Splunk index=main | Variable | filterlog entries |
| Splunk Internal | index=_internal | Standard | splunkd logs |

---

*This technical report documents findings from an authorized lab exercise. All activities were performed in an isolated virtual environment.*
