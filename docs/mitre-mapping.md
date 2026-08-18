# MITRE ATT&CK Framework Mapping

## Complete Technique Mapping for Multi-Stage Recon Lab

This document provides a comprehensive mapping of all attack techniques used in the lab to the MITRE ATT&CK framework (v14).

---

## Summary Table

| Technique ID | Tactic | Technique Name | Lab Application | Detection Data Source |
|-------------|--------|----------------|-----------------|----------------------|
| T1566 | Initial Access | Phishing | Username acquisition via social engineering | Email Logs, User Training |
| T1046 | Reconnaissance | Network Service Scanning | Nmap scan against DC ports 53, 389, 445, 3389 | Network Traffic, Firewall Logs |
| T1018 | Reconnaissance | Remote System Discovery | Host enumeration and ping sweep | Network Traffic |
| T1087 | Discovery | Account Discovery | LDAP enumeration of domain users | Windows Event Logs, LDAP Logs |
| T1087.002 | Discovery | Domain Account | Querying all AD user accounts via LDAP | Windows Event Logs |
| T1110 | Credential Access | Brute Force | Hydra password spraying attack | Windows Event Code 4625 |
| T1110.003 | Credential Access | Password Spraying | Testing common passwords against user account | Windows Event Code 4625 |
| T1078 | Initial Access, Persistence, Privilege Escalation, Defense Evasion | Valid Accounts | Successful authentication with vagrant account | Windows Event Code 4624 |
| T1003.001 | Credential Access | OS Credential Dumping: LSASS Memory | LSASS handling NTLM authentication | Windows Event Code 4624, Process Monitoring |
| T1033 | Discovery | System Owner/User Discovery | whoami /priv for privilege enumeration | Windows Event Logs, Process Monitoring |
| T1021.002 | Lateral Movement | Remote Services: SMB/Windows Admin Shares | NetExec SMB command execution | Network Traffic, Windows Event Logs |
| T1021.001 | Lateral Movement | Remote Desktop Protocol | RDP service discovery and potential access | Network Traffic, Windows Event Logs |

---

## Detection Mapping

| Attack Phase | MITRE Technique | Splunk Detection | Alert Threshold |
|-------------|-----------------|-----------------|-----------------|
| Reconnaissance | T1046 | Firewall traffic spike from 192.168.57.10 | > 100 connections in 5 min |
| Enumeration | T1087 | LDAP query volume | > 50 queries from single IP |
| Password Spray | T1110 | Event 4625 count by src_ip | > 5 failures in 1 min |
| Compromise | T1078 | Event 4624 from attacker IP | Any successful auth |

---

## References

- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [MITRE ATT&CK v14 Release Notes](https://attack.mitre.org/resources/updates/)
- [Windows Security Log Encyclopedia](https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/)
