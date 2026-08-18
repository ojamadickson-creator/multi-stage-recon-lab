#!/bin/bash
# Automated Lab Provisioning Script
# Sets up the SOC lab environment on Ubuntu/Debian systems

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
SPLUNK_VERSION="9.1.2"
SPLUNK_BUILD="b6b9c8185839"
SPLUNK_URL="https://download.splunk.com/products/splunk/releases/${SPLUNK_VERSION}/linux/splunk-${SPLUNK_VERSION}-${SPLUNK_BUILD}-Linux-x86_64.tgz"
SPLUNK_HOME="/opt/splunk"

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  SOC Lab Provisioning Script           ${NC}"
echo -e "${CYAN}  Target: Splunk Server (192.168.56.106)${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[!] Please run as root (use sudo)${NC}"
    exit 1
fi

# Update system
echo -e "${YELLOW}[1/8] Updating system packages...${NC}"
apt-get update && apt-get upgrade -y

# Install dependencies
echo -e "${YELLOW}[2/8] Installing dependencies...${NC}"
apt-get install -y \
    wget \
    curl \
    net-tools \
    tcpdump \
    python3 \
    python3-pip \
    openssh-server \
    ufw \
    jq

# Configure firewall
echo -e "${YELLOW}[3/8] Configuring UFW firewall...${NC}"
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 8000/tcp    # Splunk Web
ufw allow 8089/tcp    # Splunk Management
ufw allow 9997/tcp    # Splunk Forwarder
ufw allow 514/udp     # Syslog
ufw --force enable

# Download and install Splunk
echo -e "${YELLOW}[4/8] Installing Splunk Enterprise...${NC}"
if [ ! -d "$SPLUNK_HOME" ]; then
    cd /tmp
    wget -q "$SPLUNK_URL" -O splunk.tgz
    tar -xzf splunk.tgz -C /opt
    rm splunk.tgz
    
    # Accept license and start Splunk
    $SPLUNK_HOME/bin/splunk start --accept-license --answer-yes --no-prompt
    
    # Enable boot start
    $SPLUNK_HOME/bin/splunk enable boot-start
else
    echo -e "${GREEN}[+] Splunk already installed at $SPLUNK_HOME${NC}"
fi

# Create Splunk app structure for lab
echo -e "${YELLOW}[5/8] Creating lab app configuration...${NC}"
APP_DIR="$SPLUNK_HOME/etc/apps/soc_lab"
mkdir -p "$APP_DIR"/{local,default,lookups,static}

# Create inputs.conf
cat > "$APP_DIR/local/inputs.conf" << 'EOF'
[splunktcp://9997]
disabled = 0

[udp://514]
disabled = 0
sourcetype = opnsense
index = main
connection_host = ip
no_appending_timestamp = true
EOF

# Create props.conf
cat > "$APP_DIR/local/props.conf" << 'EOF'
[WinEventLog:Security]
SHOULD_LINEMERGE = true
TRUNCATE = 999999
KV_MODE = auto
EXTRACT-src_ip = Source Network Address:\s+(?<src_ip>\d+\.\d+\.\d+\.\d+)
EXTRACT-src_port = Source Port:\s+(?<src_port>\d+)
EXTRACT-workstation = Workstation Name:\s+(?<workstation>\w+)

[opnsense]
SHOULD_LINEMERGE = false
TIME_FORMAT = %b %d %H:%M:%S
EXTRACT-src_ip = \b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b.*?\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b
EOF

# Create indexes.conf
cat > "$APP_DIR/local/indexes.conf" << 'EOF'
[main]
coldPath = $SPLUNK_DB/main/colddb
homePath = $SPLUNK_DB/main/db
thawedPath = $SPLUNK_DB/main/thaweddb
maxTotalDataSizeMB = 512000
EOF

# Set permissions
echo -e "${YELLOW}[6/8] Setting permissions...${NC}"
chown -R splunk:splunk "$SPLUNK_HOME"

# Restart Splunk
echo -e "${YELLOW}[7/8] Restarting Splunk...${NC}"
$SPLUNK_HOME/bin/splunk restart

# Health check
echo -e "${YELLOW}[8/8] Running health check...${NC}"
sleep 10

# Check Splunk status
if $SPLUNK_HOME/bin/splunk status | grep -q "running"; then
    echo -e "${GREEN}[+] Splunk is running${NC}"
else
    echo -e "${RED}[!] Splunk failed to start${NC}"
    exit 1
fi

# Check ports
echo -e "${CYAN}[*] Listening ports:${NC}"
netstat -tulpn | grep splunk || ss -tulpn | grep splunk

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Lab Provisioning Complete!             ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Splunk Web UI: ${CYAN}http://192.168.56.106:8000${NC}"
echo -e "Default credentials: ${CYAN}admin / changeme${NC}"
echo -e "Universal Forwarder port: ${CYAN}9997${NC}"
echo -e "Syslog port: ${CYAN}514/udp${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Access Splunk Web UI and change default password"
echo "  2. Install and configure Universal Forwarder on Domain Controller"
echo "  3. Configure OPNsense to send syslog to 192.168.56.106:514"
echo "  4. Import SPL queries from spl-queries/ directory"
echo ""
