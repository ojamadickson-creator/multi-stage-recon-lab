#!/usr/bin/env python3
"""
Multi-Stage Reconnaissance Lab - Complete Project Report PDF
Author: Akpoga Dickson Ojama
Email: ojamadickson@gmail.com
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, Preformatted
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

REPO_DIR = r"C:\Users\Ojama\Documents\kimi\workspace\multi-stage-recon-lab"
OUTPUT_PDF = os.path.join(REPO_DIR, "Multi-Stage-Recon-Lab-Project-Report.pdf")
SS = os.path.join(REPO_DIR, "screenshots")

doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=A4,
    topMargin=2*cm, bottomMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm)
styles = getSampleStyleSheet()

# Define styles
H1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=18, leading=22,
    textColor=HexColor('#1a1a2e'), spaceBefore=20, spaceAfter=10, fontName='Helvetica-Bold')
H2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=14, leading=18,
    textColor=HexColor('#2d2d44'), spaceBefore=16, spaceAfter=8, fontName='Helvetica-Bold')
H3 = ParagraphStyle('H3', parent=styles['Heading3'], fontSize=12, leading=16,
    textColor=HexColor('#3d3d5c'), spaceBefore=12, spaceAfter=6, fontName='Helvetica-Bold')
BODY = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, leading=14,
    textColor=HexColor('#333333'), alignment=TA_JUSTIFY, spaceAfter=8)
CODE = ParagraphStyle('Code', parent=styles['Normal'], fontName='Courier', fontSize=8,
    leading=10, textColor=HexColor('#333333'), backColor=HexColor('#f5f5f5'),
    leftIndent=8, rightIndent=8, spaceBefore=4, spaceAfter=4)
CAP = ParagraphStyle('Caption', parent=styles['Normal'], fontSize=9, leading=12,
    textColor=HexColor('#666666'), alignment=TA_CENTER, spaceAfter=10)
WARN = ParagraphStyle('Warn', parent=styles['Normal'], fontSize=10, leading=14,
    textColor=HexColor('#8B4513'), backColor=HexColor('#FFF8DC'), leftIndent=8,
    rightIndent=8, spaceBefore=8, spaceAfter=8, borderWidth=1,
    borderColor=HexColor('#DAA520'), borderPadding=6)

story = []

# Helper to add screenshots
def add_screenshot(name, max_w=16*cm):
    path = os.path.join(SS, name)
    if os.path.exists(path):
        img = Image(path, width=max_w, height=max_w*0.56)
        story.append(img)
        story.append(Paragraph(f"Figure: {name}", CAP))
    else:
        story.append(Paragraph(f"[Screenshot: {name} — file not found]", CAP))

# ============ COVER ============
story.append(Spacer(1, 4*cm))
story.append(Paragraph("<b>MULTI STAGE RECONNAISSANCE</b>", ParagraphStyle('T', fontSize=26, leading=30, alignment=TA_CENTER, textColor=HexColor('#1a1a2e'), fontName='Helvetica-Bold')))
story.append(Paragraph("<b>& ACTIVE DIRECTORY</b>", ParagraphStyle('T2', fontSize=26, leading=30, alignment=TA_CENTER, textColor=HexColor('#1a1a2e'), fontName='Helvetica-Bold')))
story.append(Paragraph("<b>PENETRATION TESTING LAB</b>", ParagraphStyle('T3', fontSize=26, leading=30, alignment=TA_CENTER, textColor=HexColor('#1a1a2e'), fontName='Helvetica-Bold', spaceAfter=20)))
story.append(Paragraph("A Hands On Red Team & Blue Team Exercise with Splunk SIEM Detection Engineering", ParagraphStyle('ST', fontSize=13, leading=16, alignment=TA_CENTER, textColor=HexColor('#555555'))))
story.append(Spacer(1, 2*cm))

meta = [
    ["Author:", "Akpoga Dickson Ojama"],
    ["Email:", "ojamadickson@gmail.com"],
    ["Project Type:", "Cybersecurity Lab Exercise"],
    ["SIEM Platform:", "Splunk Enterprise 10.4.2"],
    ["Firewall:", "OPNsense"],
    ["Attacker OS:", "Kali Linux"],
    ["Target OS:", "Windows Server 2016 (Domain Controller)"],
    ["Date:", "August 2026"],
]
mt = Table(meta, colWidths=[4*cm, 8*cm])
mt.setStyle(TableStyle([('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),10),
    ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('ALIGN',(0,0),(0,-1),'RIGHT')]))
story.append(mt)
story.append(Spacer(1, 1*cm))
story.append(Paragraph("<b>ETHICAL USE NOTICE:</b> This document describes techniques for authorized security testing and educational purposes only. All activities were performed in an isolated virtual lab.", WARN))
story.append(PageBreak())

# ============ TOC ============
story.append(Paragraph("TABLE OF CONTENTS", H1))
story.append(Spacer(1, 0.4*cm))
toc = [
    ["1. Executive Summary", "3"],
    ["2. Lab Architecture & Network Topology", "4"],
    ["3. MITRE ATT&CK Framework Mapping", "6"],
    ["4. Red Team Phase — Attack Simulation", "8"],
    ["5. Blue Team Phase — Detection & Monitoring", "16"],
    ["6. Technical Findings", "22"],
    ["7. Mitigation Roadmap", "24"],
    ["8. References", "26"],
]
story.append(Table(toc, colWidths=[14*cm, 2*cm], style=TableStyle([
    ('FONTNAME',(0,0),(-1,-1),'Helvetica'),('FONTSIZE',(0,0),(-1,-1),10),
    ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
    ('ALIGN',(1,0),(1,-1),'RIGHT')])))
story.append(PageBreak())

# ============ 1. EXECUTIVE SUMMARY ============
story.append(Paragraph("1. EXECUTIVE SUMMARY", H1))
story.append(Paragraph("This project demonstrates a realistic multi stage reconnaissance and Active Directory penetration testing exercise, coupled with comprehensive SIEM detection engineering using Splunk Enterprise. I built this lab to bridge the gap between offensive and defensive security by executing a full attack chain from the Red Team perspective, then building detection capabilities from the Blue Team perspective.", BODY))
story.append(Paragraph("The attack simulation followed a typical adversary progression: social engineering for username acquisition, network reconnaissance, service enumeration, LDAP user discovery, password spraying with Hydra, successful authentication, and post compromise privilege enumeration. Every phase was detected through carefully crafted SPL queries, real time dashboards, and automated alerts.", BODY))
story.append(Paragraph("Key Findings", H3))
fd = [["Finding","Severity","Evidence"],
    ["Weak password policy","CRITICAL","vagrant:vagrant valid"],
    ["No account lockout threshold","HIGH","105 failed attempts from 192.168.57.10"],
    ["LDAP enumeration possible","MEDIUM","Full user list retrieved"],
    ["SMB accessible from attacker","MEDIUM","Hydra successful via SMB"],
    ["Detection coverage comprehensive","POSITIVE","All attack phases detected"],
    ["Real time alerting functional","POSITIVE","Alerts fired within 1 minute"]]
ft = Table(fd, colWidths=[6*cm, 3*cm, 7*cm])
ft.setStyle(TableStyle([('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),9),
    ('LINEABOVE',(0,0),(-1,0),1.5,black),('LINEBELOW',(0,0),(-1,0),0.75,black),
    ('LINEBELOW',(0,-1),(-1,-1),1.5,black),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
    ('VALIGN',(0,0),(-1,-1),'TOP')]))
story.append(ft)
story.append(Paragraph("Table 1: Key findings from the lab exercise.", CAP))
story.append(PageBreak())

# ============ 2. LAB ARCHITECTURE ============
story.append(Paragraph("2. LAB ARCHITECTURE & NETWORK TOPOLOGY", H1))
story.append(Paragraph("The lab environment consists of five virtual machines deployed across two network zones, separated by an OPNsense perimeter firewall. All IP addresses, ports, and system roles were verified against actual screenshot evidence captured during the exercise.", BODY))
story.append(Paragraph("2.1 Network Topology", H2))
td = [["System","IP Address","OS","Role","Gateway"],
    ["Kali Linux","192.168.57.10","Kali Linux","Red Team","192.168.57.254"],
    ["OPNsense WAN","192.168.57.254","OPNsense","Perimeter GW","N/A"],
    ["OPNsense LAN","192.168.56.254","OPNsense","Internal GW","N/A"],
    ["Domain Controller","192.168.56.102","Windows Server 2016","AD DS, DNS, LDAP","192.168.56.254"],
    ["Win10 Workstation","192.168.56.104","Windows 10 Pro","Management","192.168.56.254"],
    ["Splunk Server","192.168.56.106","Ubuntu Server","SIEM","192.168.56.254"]]
tt = Table(td, colWidths=[3.5*cm, 3.5*cm, 3*cm, 4*cm, 3.5*cm])
tt.setStyle(TableStyle([('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),8),
    ('LINEABOVE',(0,0),(-1,0),1.5,black),('LINEBELOW',(0,0),(-1,0),0.75,black),
    ('LINEBELOW',(0,-1),(-1,-1),1.5,black),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
    ('VALIGN',(0,0),(-1,-1),'TOP')]))
story.append(tt)
story.append(Paragraph("Table 2: Lab system specifications — all IPs verified against screenshots.", CAP))

story.append(Paragraph("2.2 Data Collection Architecture", H2))
story.append(Paragraph("Splunk Enterprise 10.4.2 receives security telemetry from two primary sources: Windows Security Event Logs from the Domain Controller via Splunk Universal Forwarder on TCP port 9997, and firewall filter logs from OPNsense via Syslog on UDP port 514. This dual source approach provides both endpoint and network visibility.", BODY))
dd = [["Source","Destination","Protocol","Data Type"],
    ["Domain Controller","Splunk (192.168.56.106)","TCP/9997","Windows Event Logs"],
    ["OPNsense Firewall","Splunk (192.168.56.106)","UDP/514","Firewall Filter Logs"]]
dt = Table(dd, colWidths=[4.5*cm, 5*cm, 3*cm, 4*cm])
dt.setStyle(TableStyle([('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),9),
    ('LINEABOVE',(0,0),(-1,0),1.5,black),('LINEBELOW',(0,0),(-1,0),0.75,black),
    ('LINEBELOW',(0,-1),(-1,-1),1.5,black),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
story.append(dt)
story.append(Paragraph("Table 3: Data collection architecture.", CAP))

story.append(Paragraph("2.3 Firewall Configuration", H2))
story.append(Paragraph("The OPNsense firewall was configured with floating rules to allow the Kali attacker (192.168.57.10) to reach the Domain Controller (192.168.56.102) on the required ports for this lab exercise.", BODY))
add_screenshot("Firewall configuration.png", 15*cm)
story.append(Paragraph("Screenshot 1: OPNsense firewall rules showing Kali_Allow rules for cross zone traffic.", CAP))
story.append(PageBreak())

# ============ 3. MITRE ATT&CK ============
story.append(Paragraph("3. MITRE ATT&CK FRAMEWORK MAPPING", H1))
story.append(Paragraph("Every technique employed in this lab has been mapped to the MITRE ATT&CK framework (v14). This mapping ensures detection strategies align with industry standard adversary behavior taxonomy.", BODY))

# Use a wider layout with more spacing for MITRE table
md = [["Tactic","Technique ID","Technique Name","Lab Application"],
    ["Initial Access","T1566","Phishing","Username acquisition via social engineering"],
    ["Reconnaissance","T1046","Network Service Scanning","Nmap scan against DC"],
    ["Reconnaissance","T1018","Remote System Discovery","Host enumeration"],
    ["Discovery","T1087","Account Discovery","LDAP user enumeration"],
    ["Credential Access","T1110","Brute Force","Hydra password spray"],
    ["Initial Access","T1078","Valid Accounts","vagrant:vagrant auth"],
    ["Credential Access","T1003.001","LSASS Memory","LSASS NTLM handling"],
    ["Discovery","T1033","System Owner Discovery","whoami /priv"],
    ["Lateral Movement","T1021.002","SMB/Admin Shares","NetExec SMB exec"],
    ["Lateral Movement","T1021.001","Remote Desktop","RDP discovery"]]

mt = Table(md, colWidths=[3*cm, 2.5*cm, 4*cm, 6*cm])
mt.setStyle(TableStyle([('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),9),
    ('LINEABOVE',(0,0),(-1,0),1.5,black),('LINEBELOW',(0,0),(-1,0),0.75,black),
    ('LINEBELOW',(0,-1),(-1,-1),1.5,black),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
    ('VALIGN',(0,0),(-1,-1),'TOP')]))
story.append(mt)
story.append(Paragraph("Table 4: MITRE ATT&CK v14 technique mapping.", CAP))
story.append(PageBreak())

# ============ 4. RED TEAM ============
story.append(Paragraph("4. RED TEAM PHASE — ATTACK SIMULATION", H1))
story.append(Paragraph("This section documents the complete attack chain I executed from the Kali Linux attacker machine (192.168.57.10) against the windomain.local Domain Controller (192.168.56.102). Each phase includes the exact command used, explanation of parameters, and corresponding MITRE technique.", BODY))

story.append(Paragraph("4.1 Phase 1: Username Acquisition via Social Engineering", H2))
story.append(Paragraph("Before I touched a single command, I needed a username to target. In a real world scenario, this often comes from open source intelligence (OSINT) gathering. LinkedIn profiles, company directories, or email patterns. For this lab, I assumed the role of an attacker who had already obtained a username through spear phishing or social engineering reconnaissance. The username acquired was: vagrant.", BODY))
story.append(Paragraph("This is a critical first step that many technical write ups skip. Understanding how usernames are acquired, whether through phishing, dumpster diving, or simply guessing based on naming conventions, is essential for building realistic attack simulations and effective defenses.", BODY))
story.append(Paragraph("MITRE Mapping: T1566 — Phishing (pre attack intelligence gathering)", BODY))

story.append(Paragraph("4.2 Phase 2: Network Reconnaissance", H2))
story.append(Paragraph("Objective: Discover live hosts and open services on the target network. I began by verifying connectivity, then performed a targeted port scan to identify Active Directory services.", BODY))
story.append(Paragraph("Command Used:", H3))
story.append(Preformatted("nmap -Pn -sV -p 53,389,445,3389 192.168.56.102", CODE))
story.append(Paragraph("Parameter Explanation:", H3))
story.append(Paragraph("<b>-Pn</b> — Skip host discovery (no ping), treat target as online.<br/>"
    "<b>-sV</b> — Probe open ports to determine service/version information.<br/>"
    "<b>-p 53,389,445,3389</b> — Scan specific AD and remote access ports.<br/>"
    "<b>192.168.56.102</b> — Target IP: the Domain Controller.", BODY))
story.append(Paragraph("Results: Host is alive with low latency. Open ports include DNS, LDAP, SMB, and RDP. OS fingerprint indicates Windows Server.", BODY))
add_screenshot("Nmap Scan.png", 15*cm)
story.append(Paragraph("Screenshot 2: Nmap scan results showing open AD services.", CAP))

story.append(Paragraph("4.3 Phase 3: LDAP Enumeration", H2))
story.append(Paragraph("Objective: Extract user accounts and directory information using LDAP queries. LDAP is the protocol Windows uses to query Active Directory.", BODY))
story.append(Paragraph("Command Used:", H3))
story.append(Preformatted('ldapsearch -x -H ldap://192.168.56.102 -D "windomain\\vagrant" -w "vagrant" -b "dc=windomain,dc=local" "(&(objectclass=user)(SAMAccountName=*))" | grep sAMAccountName', CODE))
story.append(Paragraph("Parameter Explanation:", H3))
story.append(Paragraph("<b>-x</b> — Use simple authentication.<br/>"
    "<b>-H ldap://192.168.56.102</b> — LDAP server URI.<br/>"
    "<b>-D \"windomain\\vagrant\"</b> — Bind DN (user to authenticate as).<br/>"
    "<b>-w \"vagrant\"</b> — Password for bind user.<br/>"
    "<b>-b \"dc=windomain,dc=local\"</b> — Base DN (search root).<br/>"
    "<b>(&(objectclass=user)(SAMAccountName=*))</b> — Filter: find all users.<br/>"
    "<b>| grep sAMAccountName</b> — Filter output to usernames.", BODY))
story.append(Paragraph("Results: Successfully enumerated domain user accounts.", BODY))
add_screenshot("ldapsearch query.correct.png", 15*cm)
story.append(Paragraph("Screenshot 3: LDAP enumeration showing successful bind and user discovery.", CAP))

story.append(PageBreak())

story.append(Paragraph("4.4 Phase 4: Credential Access via Password Spraying", H2))
story.append(Paragraph("Objective: Find valid credentials by testing common passwords against the vagrant account. Password spraying differs from brute force: instead of thousands of passwords against one account, I tested a few common passwords against one account. This avoids account lockout thresholds.", BODY))
story.append(Paragraph("In this lab, I targeted one account only: vagrant.", BODY))

story.append(Paragraph("Step 1 — Create Password List:", H3))
story.append(Preformatted('cat > /tmp/passwordlist << EOF\npassword\n123456\n12345678\nqwerty\nabc123\nmonkey\nletmein\ndragon\n111111\nbaseball\niloveyou\ntrustno1\nsunshine\nprincess\nadmin\nwelcome\nshadow\nashley\nfootball\njesus\nmichael\nninja\nmustang\npassword1\n123456789\ndiamond\nadmin123\nletmein1\nphotoshop\nqwerty123\nqaz123wsx\nqwertyuiop\nlogin\nmaster\nhello\nfreedom\nwhatever\nqazxsw\ntrustno1\nbatman\npassw0rd\nhacker\nvagrant\nEOF', CODE))
add_screenshot("Passwordlist Creation.png", 15*cm)
story.append(Paragraph("Screenshot 4: Password list creation showing commonly used weak passwords.", CAP))

story.append(Paragraph("Step 2 — Verify the Password List:", H3))
story.append(Preformatted("ls -la /tmp/passwordlist\nwc -l /tmp/passwordlist", CODE))
add_screenshot("Passwordlist Check.png", 15*cm)
story.append(Paragraph("Screenshot 5: Verifying the password list file was created correctly.", CAP))

story.append(Paragraph("Step 3 — Execute Password Spray with Hydra:", H3))
story.append(Preformatted("hydra -l vagrant -P /tmp/passwordlist smb://192.168.56.102", CODE))
story.append(Paragraph("Parameter Explanation:", H3))
story.append(Paragraph("<b>hydra</b> — The THC Hydra password cracking tool.<br/>"
    "<b>-l vagrant</b> — Single username to test.<br/>"
    "<b>-P /tmp/passwordlist</b> — Path to password list file.<br/>"
    "<b>smb://192.168.56.102</b> — Target protocol and IP address.", BODY))
story.append(Paragraph("Results: Valid credential pair discovered: vagrant:vagrant. Authentication succeeded via SMB using NTLM.", BODY))
add_screenshot("Hydra-Brute-Force-Successful.png", 15*cm)
story.append(Paragraph("Screenshot 6: Hydra successful password spray showing valid credentials.", CAP))

story.append(Paragraph("4.5 Phase 5: Post Compromise Enumeration", H2))
story.append(Paragraph("Objective: Verify access level and enumerate privileges on the compromised system.", BODY))
story.append(Paragraph("Command Used:", H3))
story.append(Preformatted('nxc smb 192.168.56.102 -u vagrant -p vagrant -x "whoami /priv"', CODE))
story.append(Paragraph("Parameter Explanation:", H3))
story.append(Paragraph("<b>nxc smb</b> — NetExec SMB module.<br/>"
    "<b>192.168.56.102</b> — Target IP.<br/>"
    "<b>-u vagrant</b> — Username.<br/>"
    "<b>-p vagrant</b> — Password.<br/>"
    "<b>-x \"whoami /priv\"</b> — Execute command on target via SMB.", BODY))
story.append(Paragraph("Results: The vagrant account holds numerous privileges including SeSecurityPrivilege, SeTakeOwnershipPrivilege, SeBackupPrivilege, and SeRestorePrivilege.", BODY))
add_screenshot("smb post compromise.png", 15*cm)
story.append(Paragraph("Screenshot 7: Post compromise privilege enumeration.", CAP))
story.append(PageBreak())

# ============ 5. BLUE TEAM ============
story.append(Paragraph("5. BLUE TEAM PHASE — DETECTION & MONITORING", H1))
story.append(Paragraph("This section documents the detection engineering work I performed in Splunk Enterprise. My objective was to detect, visualize, and alert on every phase of my own attack using Windows Event Logs and firewall syslog data.", BODY))

story.append(Paragraph("5.1 Splunk Data Ingestion", H2))
story.append(Paragraph("Splunk receives data from two sources: Windows Security Event Logs via Universal Forwarder on TCP/9997, and OPNsense firewall logs via Syslog on UDP/514.", BODY))
add_screenshot("Splunk server CLi.png", 15*cm)
story.append(Paragraph("Screenshot 8: Splunk server CLI showing service status.", CAP))

story.append(Paragraph("5.2 SPL Detection Queries", H2))
story.append(Paragraph("The following SPL queries were developed to detect specific attack indicators.", BODY))

story.append(Paragraph("Query 1: Brute Force / Password Spray Detection", H3))
story.append(Preformatted('index=main host=dc EventCode=4625\n| stats count by src_ip\n| where count > 5', CODE))
story.append(Paragraph("This query counts failed logon events (EventCode 4625) grouped by source IP. Results: 105 failed attempts from 192.168.57.10.", BODY))
add_screenshot("Alert Real IP.png", 15*cm)
story.append(Paragraph("Screenshot 9: Brute force detection showing 105 failed attempts from 192.168.57.10.", CAP))

story.append(Paragraph("Query 2: Successful Authentication Detection", H3))
story.append(Preformatted('index=main sourcetype="WinEventLog" EventCode=4624\n| stats count by src_ip', CODE))
story.append(Paragraph("Monitors successful logon events. Key indicator: source IP 192.168.57.10 appearing in successful logons.", BODY))
add_screenshot("successfull logins using tools.png", 15*cm)
story.append(Paragraph("Screenshot 10: Successful authentication query showing attacker IP 192.168.57.10.", CAP))

story.append(Paragraph("Query 3: Time Series Visualization", H3))
story.append(Preformatted('index=main sourcetype="WinEventLog" EventCode=4625\n| timechart span=1m count by src_ip', CODE))
story.append(Paragraph("Creates a time based chart to visualize attack patterns over time.", BODY))
add_screenshot("Dashboard-Time Series.png", 15*cm)
story.append(Paragraph("Screenshot 11: Time series query for visualizing attack patterns.", CAP))

story.append(PageBreak())

story.append(Paragraph("5.3 Dashboards & Alerting", H2))
story.append(Paragraph("I built a multi panel Splunk dashboard called 'Detection Engineering1' (owner: ojama) that provides a holistic view of the attack. The dashboard includes panels for failed logins, time series visualization, and successful logins.", BODY))
add_screenshot("Dashboard with correct ip.png", 15*cm)
story.append(Paragraph("Screenshot 12: Detection Engineering1 dashboard with failed logins, time series, and successful login panels.", CAP))
add_screenshot("Dashboard with correct ip..png", 15*cm)
story.append(Paragraph("Screenshot 13: Extended dashboard showing successful logins with attacker IP attribution.", CAP))
add_screenshot("Detect-Dashboard-Timeseries.png", 15*cm)
story.append(Paragraph("Screenshot 14: Saving the Time Series Visualization panel to the Detection Engineering1 dashboard.", CAP))

story.append(Paragraph("Alert Configuration:", H3))
alerts = [["Alert Name","Trigger Condition","Status"],
    ["Brute Force","> 5 failed attempts in 1 minute","Triggered"],
    ["Failed Logon","> 0 failed attempts in 1 minute","Triggered"]]
at = Table(alerts, colWidths=[5*cm, 6*cm, 3*cm])
at.setStyle(TableStyle([('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),9),
    ('LINEABOVE',(0,0),(-1,0),1.5,black),('LINEBELOW',(0,0),(-1,0),0.75,black),
    ('LINEBELOW',(0,-1),(-1,-1),1.5,black),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
story.append(at)
story.append(Paragraph("Table 5: Configured Splunk alerts.", CAP))

add_screenshot("Alert.png", 15*cm)
story.append(Paragraph("Screenshot 15: Brute Force alert configuration in Splunk.", CAP))
add_screenshot("Alert-Result.png", 15*cm)
story.append(Paragraph("Screenshot 16: Alert trigger history showing fired alerts.", CAP))

story.append(PageBreak())

story.append(Paragraph("5.4 Correlation Queries", H2))
story.append(Paragraph("The most powerful detection capability comes from correlating multiple event types into a single attack narrative.", BODY))
story.append(Preformatted('index=main host=dc (EventCode=4624 OR EventCode=4625) src_ip="192.168.57.10"\n| eval attack_phase=case(\n    EventCode=4625, "Phase 1: Brute Force Attempts",\n    EventCode=4624, "Phase 2: Successful Authentication",\n    1=1, "Other")\n| where attack_phase!="Other"\n| stats count by attack_phase, src_ip\n| sort -count', CODE))
story.append(Paragraph("This correlation query combines authentication events from the attacker IP into a coherent attack timeline. Alert recommendation: trigger when Phases 1 AND 2 occur within 30 minutes from the same source IP.", BODY))
add_screenshot("correlation query.png", 15*cm)
story.append(Paragraph("Screenshot 17: Correlation query mapping attack phases to specific EventCodes.", CAP))
story.append(PageBreak())

# ============ 6. TECHNICAL FINDINGS ============
story.append(Paragraph("6. TECHNICAL FINDINGS", H1))
story.append(Paragraph("This section summarizes the technical findings from both the Red Team and Blue Team perspectives.", BODY))

findings = [
    ["#","Finding","Severity"],
    ["1","Weak password policy allows common passwords","CRITICAL"],
    ["2","No account lockout threshold configured (105 attempts)","HIGH"],
    ["3","LDAP enumeration possible with basic credentials","MEDIUM"],
    ["4","SMB accessible from attacker network","MEDIUM"],
    ["5","vagrant account has excessive privileges","HIGH"],
    ["6","No multi factor authentication on domain accounts","CRITICAL"],
    ["7","RDP exposed to attacker network","MEDIUM"],
    ["8","Detection coverage is comprehensive","POSITIVE"],
    ["9","Correlation queries work effectively","POSITIVE"],
    ["10","Real time alerting functional","POSITIVE"],
]
ft2 = Table(findings, colWidths=[1*cm, 10*cm, 3*cm])
ft2.setStyle(TableStyle([('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),9),
    ('LINEABOVE',(0,0),(-1,0),1.5,black),('LINEBELOW',(0,0),(-1,0),0.75,black),
    ('LINEBELOW',(0,-1),(-1,-1),1.5,black),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
    ('VALIGN',(0,0),(-1,-1),'TOP')]))
story.append(ft2)
story.append(Paragraph("Table 6: Complete technical findings register.", CAP))

story.append(Paragraph("6.1 Network Traffic Analysis", H2))
story.append(Paragraph("Packet captures confirmed the following traffic patterns during the attack:", BODY))
story.append(Paragraph("<b>SYN Packets (Nmap Scan):</b> Multiple SYN packets to ports 53, 389, 445, 3389 from 192.168.57.10 to 192.168.56.102. Pattern consistent with port scanning.", BODY))
story.append(Paragraph("<b>LDAP Packets:</b> LDAP bindRequest from attacker, followed by searchRequest for user enumeration.", BODY))
story.append(Paragraph("<b>SMB Packets:</b> SMB2 NEGOTIATE, SESSION_SETUP, TREE_CONNECT sequence. NTLMSSP authentication followed by command execution via srvsvc pipe.", BODY))

add_screenshot("SYN packets.png", 15*cm)
story.append(Paragraph("Screenshot 18: Wireshark capture showing SYN scan packets.", CAP))
add_screenshot("ldap packets.png", 15*cm)
story.append(Paragraph("Screenshot 19: Wireshark capture showing LDAP query packets.", CAP))

story.append(PageBreak())

# ============ 7. MITIGATION ============
story.append(Paragraph("7. MITIGATION ROADMAP", H1))
story.append(Paragraph("Based on findings from the lab exercise, the following remediation actions are recommended, prioritized by impact and effort.", BODY))

story.append(Paragraph("7.1 Critical Priority (Immediate)", H2))
story.append(Paragraph("<b>Deploy Multi Factor Authentication (MFA):</b> Password spraying becomes largely ineffective when MFA is enforced. This is the single highest impact control. Deploy Azure AD MFA, Duo, or similar solution for all user accounts.", BODY))
story.append(Paragraph("<b>Implement Account Lockout Policy:</b> Configure Group Policy to lock accounts after 5 failed attempts for 30 minutes. Monitor Event ID 4740 for lockout notifications.", BODY))
story.append(Paragraph("<b>Strengthen Password Policy:</b> Enforce minimum 14 characters, complexity requirements, and banned password lists.", BODY))

story.append(Paragraph("7.2 High Priority (30 Days)", H2))
story.append(Paragraph("<b>Deploy Local Administrator Password Solution (LAPS):</b> Automatically manage local admin passwords with unique, complex passwords per system.", BODY))
story.append(Paragraph("<b>Implement Privileged Access Management (PAM):</b> Create separate admin accounts, implement just in time access, and use privileged access workstations (PAWs).", BODY))
story.append(Paragraph("<b>Deploy Sysmon for Enhanced Logging:</b> Sysmon provides detailed process creation, network connection, and file change telemetry.", BODY))
story.append(Paragraph("<b>Enable Windows Defender Credential Guard:</b> Uses virtualization based security to isolate LSASS, preventing credential theft attacks.", BODY))

story.append(Paragraph("7.3 Medium Priority (90 Days)", H2))
story.append(Paragraph("<b>Network Segmentation:</b> Separate management networks from user networks. Implement VLANs and restrict SMB/RDP to management subnets only.", BODY))
story.append(Paragraph("<b>Deploy Endpoint Detection and Response (EDR):</b> EDR provides real time behavioral analysis beyond what SIEM alone offers.", BODY))
story.append(Paragraph("<b>Implement PowerShell Logging:</b> Enable Module Logging, Script Block Logging, and Transcription.", BODY))

story.append(PageBreak())

# ============ 8. REFERENCES ============
story.append(Paragraph("8. REFERENCES", H1))
refs = [
    "[1] MITRE ATT&CK Framework. https://attack.mitre.org/",
    "[2] Splunk Documentation. https://docs.splunk.com/",
    "[3] Nmap Reference Guide. https://nmap.org/book/man.html",
    "[4] Hydra Documentation. https://github.com/vanhauser-thc/thc-hydra",
    "[5] NetExec Documentation. https://www.netexec.wiki/",
    "[6] OPNsense Documentation. https://docs.opnsense.org/",
    "[7] Microsoft Windows Security Log Events. https://www.ultimatewindowssecurity.com/securitylog/encyclopedia/",
    "[8] Multi Stage Recon & AD Penetration Testing Lab Walkthrough. https://www.youtube.com/watch?v=NHnI9oP_xTY",
]
for r in refs:
    story.append(Paragraph(r, BODY))

story.append(Spacer(1, 2*cm))
story.append(Paragraph("<i>Built with curiosity, caffeine, and a healthy dose of paranoia.</i>", ParagraphStyle('Footer', fontSize=10, alignment=TA_CENTER, textColor=HexColor('#666666'))))
story.append(Paragraph("<b>Happy Hunting! </b>", ParagraphStyle('Footer2', fontSize=12, alignment=TA_CENTER, textColor=HexColor('#1a1a2e'), fontName='Helvetica-Bold')))
story.append(Paragraph("Akpoga Dickson Ojama | ojamadickson@gmail.com", ParagraphStyle('Author', fontSize=9, alignment=TA_CENTER, textColor=HexColor('#888888'))))

# Build PDF
doc.build(story)
print(f"PDF generated successfully: {OUTPUT_PDF}")
print(f"File size: {os.path.getsize(OUTPUT_PDF) / 1024 / 1024:.2f} MB")
