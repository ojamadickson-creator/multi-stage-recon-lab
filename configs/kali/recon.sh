#!/bin/bash
# Automated Reconnaissance Script for AD Penetration Testing Lab
# Target: windomain.local Domain Controller at 192.168.56.102
# Author: Akpoga Dickson Ojama
# DISCLAIMER: For authorized testing only!

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
TARGET_IP="192.168.56.102"
TARGET_DOMAIN="windomain.local"
LDAP_USER="vagrant"
LDAP_PASS="vagrant"
OUTPUT_DIR="./recon-output"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create output directory
mkdir -p "$OUTPUT_DIR/$TIMESTAMP"

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  Multi Stage Reconnaissance Script     ${NC}"
echo -e "${CYAN}  Target: $TARGET_IP                   ${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Phase 1: Social Engineering (assumed)
echo -e "${YELLOW}[Phase 0] Username Acquisition (Assumed via Social Engineering)${NC}"
echo "----------------------------------------"
echo -e "${CYAN}[*] Username acquired: $LDAP_USER${NC}"
echo ""

# Phase 2: Host Discovery
echo -e "${YELLOW}[Phase 1] Host Discovery${NC}"
echo "----------------------------------------"

echo -e "${CYAN}[*] Ping sweep to verify target is alive...${NC}"
ping -c 3 "$TARGET_IP" | tee "$OUTPUT_DIR/$TIMESTAMP/ping_results.txt"
echo ""

# Phase 3: Port Scanning
echo -e "${YELLOW}[Phase 2] Port Scanning${NC}"
echo "----------------------------------------"

echo -e "${CYAN}[*] Running Nmap service detection scan...${NC}"
echo -e "${CYAN}    Ports: DNS(53), LDAP(389), SMB(445), RDP(3389)${NC}"
nmap -Pn -sV -p 53,389,445,3389 "$TARGET_IP" -oN "$OUTPUT_DIR/$TIMESTAMP/nmap_scan.txt"
echo ""

echo -e "${CYAN}[*] Running full TCP port scan (top 1000)...${NC}"
nmap -Pn -sT --top-ports 1000 "$TARGET_IP" -oN "$OUTPUT_DIR/$TIMESTAMP/nmap_top1000.txt"
echo ""

# Phase 4: Service Enumeration
echo -e "${YELLOW}[Phase 3] Service Enumeration${NC}"
echo "----------------------------------------"

echo -e "${CYAN}[*] Enumerating SMB shares and users...${NC}"
echo "Attempting SMB enumeration..."
python3 -c "
import subprocess
import sys

try:
    result = subprocess.run(['smbclient', '-L', '//$TARGET_IP', '-N'], 
                          capture_output=True, text=True, timeout=10)
    print(result.stdout)
    print(result.stderr)
except Exception as e:
    print(f'SMB null session failed: {e}')
" 2>/dev/null || echo "SMB null session enumeration failed (expected in hardened environments)"
echo ""

echo -e "${CYAN}[*] LDAP anonymous bind check...${NC}"
ldapsearch -x -H "ldap://$TARGET_IP" -b "$TARGET_DOMAIN" "(objectClass=*)" 2>&1 | head -20 | tee "$OUTPUT_DIR/$TIMESTAMP/ldap_anon.txt" || true
echo ""

# Phase 5: User Enumeration (if credentials available)
echo -e "${YELLOW}[Phase 4] Directory Enumeration${NC}"
echo "----------------------------------------"

echo -e "${CYAN}[*] Attempting authenticated LDAP query...${NC}"
if command -v ldapsearch &> /dev/null; then
    ldapsearch -x -H "ldap://$TARGET_IP" \
        -D "$TARGET_DOMAIN\\$LDAP_USER" -w "$LDAP_PASS" \
        -b "dc=${TARGET_DOMAIN%%.*},dc=${TARGET_DOMAIN#*.}" \
        "(&(objectclass=user)(SAMAccountName=*))" \
        sAMAccountName | grep "sAMAccountName:" | tee "$OUTPUT_DIR/$TIMESTAMP/ldap_users.txt" || true
else
    echo -e "${RED}[!] ldapsearch not found. Install ldap-utils package.${NC}"
fi
echo ""

# Phase 6: Summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Reconnaissance Complete!               ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Results saved to: ${CYAN}$OUTPUT_DIR/$TIMESTAMP/${NC}"
echo ""
echo "Files generated:"
ls -la "$OUTPUT_DIR/$TIMESTAMP/"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Review nmap_scan.txt for open services"
echo "  2. Check ldap_users.txt for valid accounts"
echo "  3. Use findings to build password spray target list"
echo "  4. Run ./password-spray.sh to test credentials"
echo ""
