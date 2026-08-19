# Mitigation Roadmap

## Remediation Priorities for Active Directory Environment

This document outlines specific, actionable remediation steps based on findings from the Multi Stage Reconnaissance lab exercise. Items are prioritized by risk reduction impact and implementation effort.

---

## Priority 1: Critical (Implement Immediately)

### 1.1 Deploy Multi Factor Authentication (MFA)

**Risk Addressed:** T1078 (Valid Accounts), T1110 (Brute Force)

**Description:**
Password spraying and brute force attacks become significantly less effective when MFA is enforced. Even with valid credentials, an attacker cannot authenticate without the second factor.

**Implementation:**
* Deploy Azure AD MFA or on premises MFA solution (Duo, Okta, Microsoft Authenticator)
* Enforce MFA for all user accounts, especially privileged accounts
* Consider hardware tokens for Domain Admins

**Effort:** Medium
**Impact:** Very High

---

### 1.2 Implement Account Lockout Policy

**Risk Addressed:** T1110 (Brute Force)

**Description:**
The lab demonstrated that 105 failed logon attempts were possible without triggering any account lockout. This allows unlimited password guessing.

**Recommended Policy:**
```
Account lockout threshold: 5 invalid attempts
Account lockout duration: 30 minutes
Reset account lockout counter after: 30 minutes
```

**Implementation:**
* Configure via Group Policy: Computer Configuration > Windows Settings > Security Settings > Account Policies > Account Lockout Policy
* Apply to all domain users
* Monitor for lockout events (Event ID 4740)

**Effort:** Low
**Impact:** High

---

### 1.3 Strengthen Password Policy

**Risk Addressed:** T1110 (Brute Force), T1078 (Valid Accounts)

**Description:**
The password "vagrant" is a weak, dictionary based password that was quickly discovered through password spraying.

**Recommended Policy:**
```
Minimum password length: 14 characters
Password must meet complexity requirements: Enabled
Maximum password age: 90 days
Minimum password age: 1 day
Enforce password history: 24 passwords remembered
```

**Additional Measures:**
* Implement banned password list (Azure AD Password Protection or custom)
* Block common passwords and keyboard walks
* Consider passphrase policy instead of complex passwords

**Effort:** Low
**Impact:** High

---

## Priority 2: High (Implement Within 30 Days)

### 2.1 Deploy Local Administrator Password Solution (LAPS)

**Risk Addressed:** T1078 (Valid Accounts), T1110 (Brute Force)

**Description:**
LAPS automatically manages local administrator passwords, ensuring each system has a unique, complex password that changes regularly.

**Implementation:**
1. Download LAPS from Microsoft
2. Install on Domain Controller
3. Extend AD schema for LAPS attributes
4. Deploy LAPS client to all domain joined systems
5. Configure GPO for password complexity and rotation

**Effort:** Medium
**Impact:** High

---

### 2.2 Implement Privileged Access Management (PAM)

**Risk Addressed:** T1078 (Valid Accounts), T1071 (Application Layer Protocol)

**Description:**
Restrict privileged account usage with just in time (JIT) access and privileged access workstations (PAWs).

**Implementation:**
* Create separate admin accounts (not daily use accounts)
* Implement time bound privileged access
* Use jump servers for all administrative tasks
* Monitor privileged account usage with enhanced logging

**Effort:** High
**Impact:** Very High

---

### 2.3 Deploy Sysmon for Enhanced Logging

**Risk Addressed:** T1059 (Command and Scripting Interpreter), T1053 (Scheduled Task), T1055 (Process Injection)

**Description:**
Sysmon provides detailed information about process creations, network connections, and file changes that standard Windows logging misses.

**Implementation:**
1. Download Sysmon from Sysinternals
2. Deploy with SwiftOnSecurity or custom configuration
3. Forward Sysmon logs to Splunk alongside Security logs
4. Create alerts for suspicious process patterns

**Recommended Sysmon Rules:**
* Detect Mimikatz execution
* Detect encoded PowerShell commands
* Detect suspicious WMI usage
* Detect LSASS access from non system processes

**Effort:** Medium
**Impact:** High

---

### 2.4 Enable Windows Defender Credential Guard

**Risk Addressed:** T1003.001 (LSASS Memory Dumping)

**Description:**
Credential Guard uses virtualization based security to isolate the LSASS process, preventing credential theft attacks.

**Implementation:**
1. Verify hardware requirements (TPM 2.0, UEFI 2.3.1c, Secure Boot)
2. Enable via Group Policy or MDM
3. Path: Computer Configuration > Administrative Templates > System > Device Guard > Turn On Virtualization Based Security

**Effort:** Medium
**Impact:** High

---

## Priority 3: Medium (Implement Within 90 Days)

### 3.1 Network Segmentation Improvements

**Risk Addressed:** T1021 (Remote Services), T1041 (Exfiltration)

**Description:**
Implement proper network segmentation to contain lateral movement and limit attacker access.

**Recommendations:**
* Separate management network from user network
* Implement VLANs for different system tiers
* Restrict SMB/RDP to management network only
* Deploy host based firewalls on all systems

**Implementation:**
* Redesign network architecture with tiered security zones
* Implement firewall rules restricting east west traffic
* Use jump boxes for cross zone access

**Effort:** High
**Impact:** High

---

### 3.2 Deploy Endpoint Detection and Response (EDR)

**Risk Addressed:** All execution and persistence techniques

**Description:**
EDR provides real time behavioral analysis and automated response capabilities beyond what SIEM alone can offer.

**Options:**
* Microsoft Defender for Endpoint
* CrowdStrike Falcon
* SentinelOne
* Carbon Black

**Integration with Splunk:**
* Forward EDR alerts to Splunk
* Correlate EDR and SIEM data
* Create unified detection rules

**Effort:** High
**Impact:** Very High

---

### 3.3 Implement PowerShell Logging and Constrained Language Mode

**Risk Addressed:** T1059.001 (PowerShell)

**Description:**
PowerShell is heavily abused by attackers. Comprehensive logging and constrained language mode significantly reduce attack surface.

**Implementation:**
1. Enable Module Logging, Script Block Logging, and Transcription
2. Deploy via Group Policy
3. Consider AppLocker or WDAC for constrained language mode
4. Forward PowerShell logs to Splunk

**Effort:** Medium
**Impact:** Medium

---

### 3.4 Regular Penetration Testing and Red Team Exercises

**Risk Addressed:** All

**Description:**
Regular testing validates that controls are effective and identifies new vulnerabilities.

**Recommendations:**
* Quarterly internal penetration tests
* Annual external penetration tests
* Continuous purple team exercises
* Attack simulation with tools like Atomic Red Team

**Effort:** Medium (ongoing)
**Impact:** High

---

## Priority 4: Ongoing (Continuous Improvement)

### 4.1 Security Awareness Training

**Risk Addressed:** T1078 (Valid Accounts — social engineering)

**Description:**
Users are often the weakest link. Regular training reduces susceptibility to phishing and social engineering.

**Program Components:**
* Monthly phishing simulations
* Quarterly security awareness training
* Incident reporting procedures
* Password hygiene education

---

### 4.2 Vulnerability Management Program

**Risk Addressed:** All exploitation techniques

**Description:**
Regular patching and vulnerability scanning reduces the attack surface.

**Recommendations:**
* Monthly vulnerability scans
* Quarterly patch cycles
* Emergency patching for critical vulnerabilities
* Asset inventory and lifecycle management

---

### 4.3 SIEM Rule Tuning and Maintenance

**Risk Addressed:** Detection gaps

**Description:**
Detection rules require continuous tuning to reduce false positives and catch evolving threats.

**Activities:**
* Weekly alert review and tuning
* Monthly detection engineering sprints
* Quarterly MITRE ATT&CK coverage assessment
* Annual purple team validation

---

## Implementation Timeline

| Quarter | Critical Actions | High Priority | Medium Priority |
|---------|-----------------|---------------|-----------------|
| Q1 | MFA, Lockout Policy, Password Policy | LAPS, PAM | Segmentation |
| Q2 | — | Sysmon, Credential Guard | EDR evaluation |
| Q3 | — | — | EDR deployment |
| Q4 | — | — | Penetration testing |

---

## Metrics for Success

| Metric | Current State | Target |
|--------|--------------|--------|
| Mean Time to Detect (MTTD) | < 1 minute (lab) | < 5 minutes (production) |
| Mean Time to Respond (MTTR) | N/A | < 1 hour |
| Password spray success rate | 100% (vagrant) | 0% |
| Critical alerts without response | N/A | 0 |
| Vulnerability scan coverage | Unknown | 100% |
| MFA enrollment rate | 0% | 100% |

---

*This roadmap is a living document and should be reviewed and updated quarterly based on threat landscape changes and organizational priorities.*
