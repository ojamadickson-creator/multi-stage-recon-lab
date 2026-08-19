# Executive Summary

## Multi Stage Reconnaissance & Active Directory Security Assessment

**Date:** August 2026
**Classification:** Internal Lab Report   Educational Purposes Only
**Scope:** windomain.local Active Directory Environment

---

## What I Did

I built a realistic cybersecurity lab to understand how attackers reconnoiter, compromise, and move through Windows Active Directory environments. I also wanted to see how security teams can detect these activities using Splunk SIEM.

Think of it like this: I put on both hats. First, the red team hat, where I mapped the network, found services, and eventually got valid credentials. Then I switched to the blue team hat, building detection rules and dashboards to catch exactly the kinds of activities I had just performed.

## What I Found

### The Attack Worked (And That's Expected)

Here is the thing. In my lab environment, a motivated attacker with network access could:

1. **Map the network** in under 5 minutes using standard tools like Nmap
2. **Enumerate all user accounts** through LDAP with just basic credentials
3. **Spray passwords** and find valid credentials (vagrant:vagrant) in minutes
4. **Execute commands remotely** via SMB, effectively owning the system

In a real environment with weak password policies and no multi factor authentication, this same chain of events happens every day.

### Detection Is Possible — If You're Looking

The good news? Every single step of the attack left breadcrumbs in the logs:

| Attack Step | Log Evidence | Detection Time |
|------------|-------------|----------------|
| Port scanning | Firewall connection logs | Real time |
| LDAP enumeration | Windows Event 4624/4625 | Real time |
| Password spraying | Multiple Event 4625s from same IP | < 1 minute |
| Successful compromise | Event 4624 with attacker IP | Real time |
| Command execution | Event 4672 (privilege assignment) | Real time |

### The Dashboard Tells the Story

My Splunk dashboard successfully visualized the entire attack chain:
* Failed login attempts spiking from a single IP
* Successful authentication shortly after
* Privileged logon events confirming access

## Risk Assessment

| Risk Factor | Rating | Justification |
|------------|--------|---------------|
| Likelihood of Real World Occurrence | **HIGH** | These techniques are commonly used by threat actors |
| Impact of Successful Attack | **CRITICAL** | Full domain compromise possible |
| Detection Difficulty | **LOW** | Well understood attack patterns with clear log evidence |
| Current Defense Maturity | **MEDIUM** | Basic logging and SIEM in place, but gaps exist |

## Key Recommendations (In Order of Priority)

### 1. Implement Multi Factor Authentication (Immediate)
Password spraying becomes largely ineffective when MFA is enforced. This is the single highest impact control.

### 2. Deploy Password Policies with Complexity and Lockout
* Minimum 14 characters
* Account lockout after 5 failed attempts
* Regular password rotation

### 3. Enable and Tune Advanced Logging
* Sysmon deployment on all Windows systems
* PowerShell script block logging
* Enhanced Windows auditing (already partially done)

### 4. Network Segmentation
* Separate management networks from user networks
* Restrict lateral movement between subnets
* Implement jump boxes for administrative access

### 5. Deploy Endpoint Detection and Response (EDR)
SIEM sees the network perspective; EDR sees the endpoint perspective. Together, they are far more effective.

### 6. Regular Penetration Testing
Run this exact lab scenario (or hire someone to) against your production environment quarterly.

## What This Means for Leadership

The techniques demonstrated in this lab are not advanced nation state tactics. They are fundamental, well documented methods that any competent attacker can employ with freely available tools. The difference between a breach and a blocked attack often comes down to:

1. **Whether you are collecting the right logs** (I am)
2. **Whether someone is watching those logs** (I built the dashboards)
3. **Whether you respond quickly enough** (my alerts fire in under a minute)

**Bottom line:** The defenses work, but only if they are maintained, monitored, and continuously improved.

---

*This report was generated as part of an authorized security lab exercise. All activities were performed in an isolated virtual environment with no production impact.*
