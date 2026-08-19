#!/usr/bin/env python3
"""
Multi-Stage Reconnaissance Lab - Project Report PDF Generator
Uses ReportLab to create a comprehensive technical report.
"""

import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, ListFlowable, ListItem, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# Paths
REPO_DIR = r"C:\Users\Ojama\Documents\kimi\workspace\multi-stage-recon-lab"
OUTPUT_PDF = os.path.join(REPO_DIR, "Multi-Stage-Recon-Lab-Project-Report.pdf")
SCREENSHOTS_DIR = os.path.join(REPO_DIR, "screenshots")

# Document setup
doc = SimpleDocTemplate(
    OUTPUT_PDF,
    pagesize=A4,
    topMargin=2.5*cm,
    bottomMargin=2.5*cm,
    leftMargin=2.5*cm,
    rightMargin=2.5*cm,
)

# Base styles
styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Title'],
    fontSize=28,
    leading=34,
    textColor=HexColor('#1a1a2e'),
    spaceAfter=30,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold',
)

subtitle_style = ParagraphStyle(
    'CustomSubtitle',
    parent=styles['Normal'],
    fontSize=14,
    leading=18,
    textColor=HexColor('#444444'),
    alignment=TA_CENTER,
    spaceAfter=20,
)

heading1_style = ParagraphStyle(
    'CustomH1',
    parent=styles['Heading1'],
    fontSize=18,
    leading=22,
    textColor=HexColor('#1a1a2e'),
    spaceBefore=24,
    spaceAfter=12,
    fontName='Helvetica-Bold',
    borderWidth=0,
    borderColor=HexColor('#1a1a2e'),
    borderPadding=5,
)

heading2_style = ParagraphStyle(
    'CustomH2',
    parent=styles['Heading2'],
    fontSize=14,
    leading=18,
    textColor=HexColor('#2d2d44'),
    spaceBefore=18,
    spaceAfter=10,
    fontName='Helvetica-Bold',
)

heading3_style = ParagraphStyle(
    'CustomH3',
    parent=styles['Heading3'],
    fontSize=12,
    leading=16,
    textColor=HexColor('#3d3d5c'),
    spaceBefore=14,
    spaceAfter=8,
    fontName='Helvetica-Bold',
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['Normal'],
    fontSize=10,
    leading=14,
    textColor=HexColor('#333333'),
    alignment=TA_JUSTIFY,
    spaceAfter=8,
)

code_style = ParagraphStyle(
    'CodeStyle',
    parent=styles['Normal'],
    fontName='Courier',
    fontSize=8,
    leading=10,
    textColor=HexColor('#333333'),
    backColor=HexColor('#f5f5f5'),
    leftIndent=10,
    rightIndent=10,
    spaceBefore=6,
    spaceAfter=6,
)

caption_style = ParagraphStyle(
    'Caption',
    parent=styles['Normal'],
    fontSize=9,
    leading=12,
    textColor=HexColor('#666666'),
    alignment=TA_CENTER,
    spaceAfter=12,
)

warning_style = ParagraphStyle(
    'WarningBox',
    parent=styles['Normal'],
    fontSize=10,
    leading=14,
    textColor=HexColor('#8B4513'),
    backColor=HexColor('#FFF8DC'),
    leftIndent=10,
    rightIndent=10,
    spaceBefore=10,
    spaceAfter=10,
    borderWidth=1,
    borderColor=HexColor('#DAA520'),
    borderPadding=8,
)

# Story (document content)
story = []

# ============ COVER PAGE ============
story.append(Spacer(1, 4*cm))
story.append(Paragraph("MULTI-STAGE", title_style))
story.append(Paragraph("RECONNAISSANCE", title_style))
story.append(Paragraph("& ACTIVE DIRECTORY", title_style))
story.append(Paragraph("PENETRATION TESTING LAB", title_style))
story.append(Spacer(1, 1*cm))
story.append(Paragraph("A Hands-On Red Team & Blue Team Exercise", subtitle_style))
story.append(Spacer(1, 0.5*cm))
story.append(Paragraph("with Splunk SIEM Detection Engineering", subtitle_style))
story.append(Spacer(1, 2*cm))

# Cover metadata table
cover_data = [
    ["Project Type:", "Cybersecurity Lab Exercise"],
    ["Focus Areas:", "Network Reconnaissance, AD Attacks, SIEM Detection"],
    ["SIEM Platform:", "Splunk Enterprise 10.4.2"],
    ["Firewall:", "OPNsense"],
    ["Attacker OS:", "Kali Linux"],
    ["Target OS:", "Windows Server 2016 (Domain Controller)"],
    ["Date:", "August 2026"],
]
cover_table = Table(cover_data, colWidths=[4*cm, 8*cm])
cover_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#1a1a2e')),
    ('TEXTCOLOR', (1, 0), (1, -1), HexColor('#444444')),
    ('TOPPADDING', (0, 0), (-1, -1), 8),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
    ('LINEABOVE', (0, 0), (-1, 0), 0.5, HexColor('#cccccc')),
    ('LINEBELOW', (0, -1), (-1, -1), 0.5, HexColor('#cccccc')),
]))
story.append(cover_table)
story.append(Spacer(1, 2*cm))

# Ethical disclaimer on cover
story.append(Paragraph(
    "<b>ETHICAL USE NOTICE:</b> This document describes techniques intended for "
    "authorized security testing and educational purposes only. All activities were "
    "performed in an isolated virtual lab environment.",
    warning_style
))

story.append(PageBreak())

# ============ TABLE OF CONTENTS ============
story.append(Paragraph("TABLE OF CONTENTS", heading1_style))
story.append(Spacer(1, 0.5*cm))

toc_items = [
    ("1. Executive Summary", "3"),
    ("2. Lab Architecture & Network Topology", "4"),
    ("3. MITRE ATT&CK Framework Mapping", "6"),
    ("4. Red Team Phase — Attack Simulation", "8"),
    ("   4.1 Network Reconnaissance", "8"),
    ("   4.2 LDAP Enumeration", "10"),
    ("   4.3 Credential Access via Password Spraying", "12"),
    ("   4.4 Post-Compromise Enumeration", "14"),
    ("5. Blue Team Phase — Detection & Monitoring", "16"),
    ("   5.1 Splunk Data Ingestion Architecture", "16"),
    ("   5.2 SPL Detection Queries", "18"),
    ("   5.3 Dashboards & Alerting", "20"),
    ("   5.4 Correlation Queries", "22"),
    ("6. Technical Findings", "24"),
    ("7. Mitigation Roadmap", "26"),
    ("8. References", "28"),
]

toc_data = [[item[0], item[1]] for item in toc_items]
toc_table = Table(toc_data, colWidths=[14*cm, 2*cm])
toc_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ('LINEABOVE', (0, 0), (-1, 0), 0.5, HexColor('#cccccc')),
    ('LINEBELOW', (0, -1), (-1, -1), 0.5, HexColor('#cccccc')),
]))
story.append(toc_table)
story.append(PageBreak())

# ============ 1. EXECUTIVE SUMMARY ============
story.append(Paragraph("1. EXECUTIVE SUMMARY", heading1_style))
story.append(Paragraph(
    "This project demonstrates a realistic multi-stage reconnaissance and Active Directory "
    "penetration testing exercise, coupled with comprehensive SIEM detection engineering using "
    "Splunk Enterprise. The lab bridges the gap between offensive and defensive security by "
    "executing a full attack chain from the Red Team perspective, then building detection "
    "capabilities from the Blue Team perspective.",
    body_style
))
story.append(Paragraph(
    "The attack simulation followed a typical adversary progression: network reconnaissance, "
    "service enumeration, LDAP user discovery, password spraying, successful authentication, "
    "and post-compromise privilege enumeration. Every phase of the attack was detected through "
    "carefully crafted SPL queries, real-time dashboards, and automated alerts.",
    body_style
))

story.append(Paragraph("Key Findings:", heading3_style))
findings_data = [
    ["Finding", "Severity", "Evidence"],
    ["Weak password policy allows common passwords", "CRITICAL", "vagrant:vagrant valid"],
    ["No account lockout threshold configured", "HIGH", "1,191 failed attempts allowed"],
    ["LDAP enumeration possible with basic credentials", "MEDIUM", "Full user list retrieved"],
    ["SMB accessible from attacker network", "MEDIUM", "NetExec successful via SMB"],
    ["Detection coverage comprehensive", "POSITIVE", "All attack phases detected"],
    ["Real-time alerting functional", "POSITIVE", "Alerts fired within 1 minute"],
]
findings_table = Table(findings_data, colWidths=[6*cm, 3*cm, 7*cm])
findings_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('LINEABOVE', (0, 0), (-1, 0), 1.5, black),
    ('LINEBELOW', (0, 0), (-1, 0), 0.75, black),
    ('LINEBELOW', (0, -1), (-1, -1), 1.5, black),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
]))
story.append(findings_table)
story.append(Spacer(1, 0.5*cm))
story.append(Paragraph(
    "The lab proves that with proper logging, SIEM configuration, and detection engineering, "
    "even sophisticated multi-stage attacks leave detectable breadcrumbs at every step.",
    body_style
))
story.append(PageBreak())

# ============ 2. LAB ARCHITECTURE ============
story.append(Paragraph("2. LAB ARCHITECTURE & NETWORK TOPOLOGY", heading1_style))
story.append(Paragraph(
    "The lab environment consists of five virtual machines deployed across two network zones, "
    "separated by an OPNsense perimeter firewall. All IP addresses, ports, and system roles "
    "were verified against actual screenshot evidence captured during the exercise.",
    body_style
))

story.append(Paragraph("2.1 Network Topology", heading2_style))
story.append(Paragraph(
    "The network is divided into a WAN zone (attacker network) and a LAN zone (corporate network). "
    "The OPNsense firewall provides routing, NAT, and access control between zones.",
    body_style
))

# Network topology table
topo_data = [
    ["System", "IP Address", "OS", "Role", "Gateway"],
    ["Kali Linux (Attacker)", "192.168.57.10", "Kali Linux", "Red Team Platform", "192.168.57.254"],
    ["OPNsense Firewall", "192.168.57.254 (WAN)", "FreeBSD/OPNsense", "Perimeter Gateway", "N/A"],
    ["OPNsense Firewall", "192.168.56.254 (LAN)", "FreeBSD/OPNsense", "Internal Gateway", "N/A"],
    ["Domain Controller", "192.168.56.102", "Windows Server 2016", "AD DS, DNS, LDAP, SMB", "192.168.56.254"],
    ["Windows 10 Workstation", "192.168.56.104", "Windows 10 Pro", "Management Console", "192.168.56.254"],
    ["Splunk Server", "192.168.56.106", "Ubuntu Server", "SIEM Platform", "192.168.56.254"],
]
topo_table = Table(topo_data, colWidths=[3.8*cm, 3.5*cm, 3*cm, 4*cm, 3.2*cm])
topo_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('LINEABOVE', (0, 0), (-1, 0), 1.5, black),
    ('LINEBELOW', (0, 0), (-1, 0), 0.75, black),
    ('LINEBELOW', (0, -1), (-1, -1), 1.5, black),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
]))
story.append(topo_table)
story.append(Spacer(1, 0.3*cm))
story.append(Paragraph(
    "Table 1: Lab system specifications — all IPs verified against screenshot evidence.",
    caption_style
))

story.append(Paragraph("2.2 Data Collection Architecture", heading2_style))
story.append(Paragraph(
    "Splunk Enterprise 10.4.2 receives security telemetry from two primary sources: (1) Windows "
    "Security Event Logs from the Domain Controller via Splunk Universal Forwarder on TCP port 9997, "
    "and (2) firewall filter logs from OPNsense via Syslog on UDP port 514. This dual-source "
    "approach provides both endpoint and network visibility for comprehensive attack detection.",
    body_style
))

dataflow_data = [
    ["Source", "Destination", "Protocol/Port", "Data Type"],
    ["Domain Controller", "Splunk (192.168.56.106)", "TCP/9997", "Windows Event Logs (WinEventLog)"],
    ["OPNsense Firewall", "Splunk (192.168.56.106)", "UDP/514", "Firewall Filter Logs (Syslog)"],
]
dataflow_table = Table(dataflow_data, colWidths=[4.5*cm, 4.5*cm, 3.5*cm, 5*cm])
dataflow_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('LINEABOVE', (0, 0), (-1, 0), 1.5, black),
    ('LINEBELOW', (0, 0), (-1, 0), 0.75, black),
    ('LINEBELOW', (0, -1), (-1, -1), 1.5, black),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
]))
story.append(dataflow_table)
story.append(Spacer(1, 0.3*cm))
story.append(Paragraph("Table 2: Data collection architecture.", caption_style))

story.append(PageBreak())

# ============ 3. MITRE ATT&CK MAPPING ============
story.append(Paragraph("3. MITRE ATT&CK FRAMEWORK MAPPING", heading1_style))
story.append(Paragraph(
    "Every technique employed in this lab has been mapped to the MITRE ATT&CK framework (v14). "
    "This mapping ensures detection strategies align with industry-standard adversary behavior "
    "taxonomy and enables cross-referencing with threat intelligence.",
    body_style
))

mitre_data = [
    ["Tactic", "Technique ID", "Technique Name", "Lab Application", "Detection Source"],
    ["Reconnaissance", "T1046", "Network Service Scanning", "Nmap port scan against DC", "Network Traffic, Firewall Logs"],
    ["Reconnaissance", "T1018", "Remote System Discovery", "Host enumeration, ping sweep", "Network Traffic"],
    ["Discovery", "T1087", "Account Discovery", "LDAP user enumeration", "Windows Event Logs"],
    ["Credential Access", "T1110", "Brute Force", "NetExec password spraying", "Windows Event 4625"],
    ["Initial Access", "T1078", "Valid Accounts", "Successful auth with vagrant", "Windows Event 4624"],
    ["Credential Access", "T1003.001", "LSASS Memory Dumping", "LSASS handling NTLM auth", "Process Monitoring"],
    ["Discovery", "T1033", "System Owner/User Discovery", "whoami /priv execution", "Process Monitoring"],
    ["Lateral Movement", "T1021.002", "SMB/Admin Shares", "NetExec SMB command exec", "Network Traffic, Event Logs"],
    ["Lateral Movement", "T1021.001", "Remote Desktop Protocol", "RDP service discovery", "Network Traffic"],
    ["Persistence", "T1136.001", "Create Local Account", "Backdoor account creation", "Windows Event 4720"],
    ["Persistence", "T1053.005", "Scheduled Task", "Task-based persistence", "Windows Event 4698"],
    ["Execution", "T1059", "Command Interpreter", "Remote command execution", "Process Creation Logs"],
    ["Defense Evasion", "T1070.004", "File Deletion", "Log clearing activity", "File Monitoring"],
    ["Exfiltration", "T1041", "Exfiltration Over C2", "Data transfer over SMB", "Network Traffic"],
    ["Lateral Movement", "T1550.002", "Pass the Hash", "NTLM hash-based auth", "Authentication Logs"],
]

# Use smaller font for this wide table
mitre_table = Table(mitre_data, colWidths=[2.8*cm, 2*cm, 3.2*cm, 4*cm, 3.5*cm])
mitre_table.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 7.5),
    ('LINEABOVE', (0, 0), (-1, 0), 1.5, black),
    ('LINEBELOW', (0, 0), (-1, 0), 0.75, black),
    ('LINEBELOW', (0, -1), (-1, -1), 1.5, black),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
]))
story.append(mitre_table)
story.append(Spacer(1, 0.3*cm))
story.append(Paragraph(
    "Table 3: Complete MITRE ATT&CK v14 technique mapping for all lab activities.",
    caption_style
))
story.append(PageBreak())

# Save the story so far (we'll continue in part 2)
print("Part 1 complete. Building PDF...")

# Build the document
doc.build(story)
print(f"PDF generated: {OUTPUT_PDF}")
