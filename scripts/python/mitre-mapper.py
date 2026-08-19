#!/usr/bin/env python3
"""
MITRE ATT&CK Mapper for SOC Lab
Generates MITRE ATT&CK technique mapping reports from attack data.

Usage:
    python mitre-mapper.py --events events.json --output mitre-report.md
"""

import argparse
import json
from datetime import datetime


MITRE_TECHNIQUES = {
    "T1046": {
        "name": "Network Service Scanning",
        "tactic": "Reconnaissance",
        "description": "Adversaries may attempt to get a listing of services running on remote hosts and local network infrastructure devices.",
        "platforms": ["Linux", "macOS", "Windows", "Network"],
        "data_sources": ["Network Traffic", "Firewall Logs"],
        "lab_evidence": "Nmap scan against DC (192.168.56.102) ports 53, 389, 445, 3389"
    },
    "T1018": {
        "name": "Remote System Discovery",
        "tactic": "Reconnaissance",
        "description": "Adversaries may attempt to get a listing of other systems by IP address, hostname, or other logical identifier on a network.",
        "platforms": ["Linux", "macOS", "Windows"],
        "data_sources": ["Network Traffic", "Process Monitoring"],
        "lab_evidence": "Ping sweep and host enumeration of 192.168.56.0/24"
    },
    "T1087": {
        "name": "Account Discovery",
        "tactic": "Discovery",
        "description": "Adversaries may attempt to get a listing of accounts on a system or within an environment.",
        "platforms": ["Linux", "macOS", "Windows"],
        "data_sources": ["Command Execution", "Process Monitoring", "Windows Event Logs"],
        "lab_evidence": "LDAP query enumerating all user accounts in windomain.local"
    },
    "T1110": {
        "name": "Brute Force",
        "tactic": "Credential Access",
        "description": "Adversaries may use brute force techniques to gain access to accounts when passwords are unknown or when password hashes are obtained.",
        "platforms": ["Linux", "macOS", "Windows", "Network"],
        "data_sources": ["Authentication Logs", "Windows Event Logs"],
        "lab_evidence": "NetExec password spraying from 192.168.57.10 against SMB service"
    },
    "T1078": {
        "name": "Valid Accounts",
        "tactic": "Initial Access, Persistence, Privilege Escalation, Defense Evasion",
        "description": "Adversaries may obtain and abuse credentials of existing accounts as a means of gaining Initial Access, Persistence, Privilege Escalation, or Defense Evasion.",
        "platforms": ["Linux", "macOS", "Windows", "Network"],
        "data_sources": ["Authentication Logs", "Windows Event Logs"],
        "lab_evidence": "Successful authentication with vagrant:vagrant credentials"
    },
    "T1003.001": {
        "name": "OS Credential Dumping: LSASS Memory",
        "tactic": "Credential Access",
        "description": "Adversaries may attempt to access credential material stored in the process memory of the Local Security Authority Subsystem Service (LSASS).",
        "platforms": ["Windows"],
        "data_sources": ["Process Monitoring", "Windows Event Logs"],
        "lab_evidence": "LSASS process (pid 0x224) handling NTLM authentication in Event 4624"
    },
    "T1033": {
        "name": "System Owner/User Discovery",
        "tactic": "Discovery",
        "description": "Adversaries may attempt to identify the primary user, currently logged in user, set of users that commonly uses a system, or whether a user is actively using the system.",
        "platforms": ["Linux", "macOS", "Windows"],
        "data_sources": ["Command Execution", "Process Monitoring"],
        "lab_evidence": "whoami /priv command execution via SMB remote command"
    },
    "T1021.002": {
        "name": "Remote Services: SMB/Windows Admin Shares",
        "tactic": "Lateral Movement",
        "description": "Adversaries may use Valid Accounts to interact with a remote network share using Server Message Block (SMB).",
        "platforms": ["Windows"],
        "data_sources": ["Network Traffic", "Windows Event Logs"],
        "lab_evidence": "NetExec SMB command execution (whoami /priv) on 192.168.56.102"
    },
    "T1021.001": {
        "name": "Remote Desktop Protocol",
        "tactic": "Lateral Movement",
        "description": "Adversaries may use Valid Accounts to log into a computer using the Remote Desktop Protocol (RDP).",
        "platforms": ["Windows"],
        "data_sources": ["Authentication Logs", "Network Traffic"],
        "lab_evidence": "RDP service discovered on port 3389 during Nmap scan"
    },
    "T1136.001": {
        "name": "Create Account: Local Account",
        "tactic": "Persistence",
        "description": "Adversaries may create a local account to maintain access to victim systems.",
        "platforms": ["Linux", "macOS", "Windows"],
        "data_sources": ["Windows Event Logs", "Command Execution"],
        "lab_evidence": "Event 4720 - User account creation detection"
    },
    "T1053.005": {
        "name": "Scheduled Task/Job: Scheduled Task",
        "tactic": "Execution, Persistence, Privilege Escalation",
        "description": "Adversaries may abuse the Windows Task Scheduler to execute programs at system startup or on a scheduled basis for persistence.",
        "platforms": ["Windows"],
        "data_sources": ["Windows Event Logs", "File Monitoring"],
        "lab_evidence": "Event 4698 - Scheduled task creation detection"
    },
    "T1059": {
        "name": "Command and Scripting Interpreter",
        "tactic": "Execution",
        "description": "Adversaries may abuse command and script interpreters to execute commands, scripts, or binaries.",
        "platforms": ["Linux", "macOS", "Windows"],
        "data_sources": ["Process Monitoring", "Command Execution"],
        "lab_evidence": "Remote command execution via NetExec SMB module"
    },
    "T1098": {
        "name": "Account Manipulation",
        "tactic": "Persistence",
        "description": "Adversaries may manipulate accounts to maintain access to victim systems.",
        "platforms": ["Linux", "macOS", "Windows", "Network"],
        "data_sources": ["Windows Event Logs", "Authentication Logs"],
        "lab_evidence": "Group membership changes (Event 4732, 4756)"
    },
    "T1070.004": {
        "name": "Indicator Removal: File Deletion",
        "tactic": "Defense Evasion",
        "description": "Adversaries may delete files left behind by the actions of their intrusion activity.",
        "platforms": ["Linux", "macOS", "Windows"],
        "data_sources": ["File Monitoring", "Process Monitoring"],
        "lab_evidence": "Detection of file deletion post-compromise"
    },
    "T1027": {
        "name": "Obfuscated Files or Information",
        "tactic": "Defense Evasion",
        "description": "Adversaries may attempt to make an executable or file difficult to discover or analyze by encrypting, encoding, or otherwise obfuscating its contents.",
        "platforms": ["Linux", "macOS", "Windows"],
        "data_sources": ["File Monitoring", "Process Monitoring"],
        "lab_evidence": "Encoded or obfuscated payloads in attack tools"
    },
    "T1041": {
        "name": "Exfiltration Over C2 Channel",
        "tactic": "Exfiltration",
        "description": "Adversaries may steal data by exfiltrating it over an existing command and control channel.",
        "platforms": ["Linux", "macOS", "Windows"],
        "data_sources": ["Network Traffic", "Process Monitoring"],
        "lab_evidence": "Data transfer over established SMB/NTLM session"
    },
    "T1550.002": {
        "name": "Use Alternate Authentication Material: Pass the Hash",
        "tactic": "Lateral Movement, Defense Evasion",
        "description": "Adversaries may pass the hash using stolen password hashes to move laterally without knowing the actual password.",
        "platforms": ["Windows"],
        "data_sources": ["Authentication Logs", "Network Traffic"],
        "lab_evidence": "NTLM authentication without password (hash-based)"
    }
}


def generate_report(output_format="markdown"):
    """Generate MITRE ATT&CK mapping report."""
    
    report_lines = []
    
    if output_format == "markdown":
        report_lines.append("# MITRE ATT&CK Mapping Report")
        report_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("\n## Lab: Multi-Stage Reconnaissance & AD Penetration Testing")
        report_lines.append("\n---\n")
        
        report_lines.append("## Summary Table\n")
        report_lines.append("| Technique ID | Tactic | Technique Name | Lab Application | Detection Source |")
        report_lines.append("|-------------|--------|----------------|-----------------|------------------|")
        
        for tech_id, tech_data in sorted(MITRE_TECHNIQUES.items()):
            report_lines.append(
                f"| {tech_id} | {tech_data['tactic']} | {tech_data['name']} | "
                f"{tech_data['lab_evidence']} | {', '.join(tech_data['data_sources'])} |"
            )
        
        report_lines.append("\n---\n")
        report_lines.append("## Detailed Technique Descriptions\n")
        
        for tech_id, tech_data in sorted(MITRE_TECHNIQUES.items()):
            report_lines.append(f"### {tech_id}: {tech_data['name']}\n")
            report_lines.append(f"**Tactic:** {tech_data['tactic']}\n")
            report_lines.append(f"**Platforms:** {', '.join(tech_data['platforms'])}\n")
            report_lines.append(f"**Detection Sources:** {', '.join(tech_data['data_sources'])}\n")
            report_lines.append(f"**Lab Evidence:** {tech_data['lab_evidence']}\n")
            report_lines.append(f"**Description:** {tech_data['description']}\n")
            report_lines.append("\n---\n")
    
    elif output_format == "csv":
        report_lines.append("Technique_ID,Tactic,Technique_Name,Platforms,Data_Sources,Lab_Evidence")
        for tech_id, tech_data in sorted(MITRE_TECHNIQUES.items()):
            platforms = "|".join(tech_data['platforms'])
            sources = "|".join(tech_data['data_sources'])
            report_lines.append(
                f'"{tech_id}","{tech_data["tactic"]}","{tech_data["name"]}",'
                f'"{platforms}","{sources}","{tech_data["lab_evidence"]}"'
            )
    
    elif output_format == "json":
        return json.dumps({
            "generated_at": datetime.now().isoformat(),
            "lab_name": "Multi-Stage Reconnaissance & AD Penetration Testing",
            "techniques": MITRE_TECHNIQUES
        }, indent=2)
    
    return "\n".join(report_lines)


def main():
    parser = argparse.ArgumentParser(description="MITRE ATT&CK Mapper for SOC Lab")
    parser.add_argument("--output", "-o", default="mitre-mapping.md", help="Output file")
    parser.add_argument("--format", choices=["markdown", "csv", "json"], default="markdown", help="Output format")
    
    args = parser.parse_args()
    
    report = generate_report(args.format)
    
    with open(args.output, 'w') as f:
        f.write(report)
    
    print(f"MITRE ATT&CK mapping report generated: {args.output}")
    print(f"Total techniques mapped: {len(MITRE_TECHNIQUES)}")


if __name__ == "__main__":
    main()
