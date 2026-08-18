#!/bin/bash
# Health Check Script for SOC Lab
# Verifies all services and data flows are operational

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

SPLUNK_HOME="/opt/splunk"
FAILED=0

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  SOC Lab Health Check                  ${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Function to check service
check_service() {
    local name=$1
    local check_cmd=$2
    
    echo -n "Checking $name... "
    if eval "$check_cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}OK${NC}"
        return 0
    else
        echo -e "${RED}FAILED${NC}"
        return 1
    fi
}

echo -e "${YELLOW}System Services:${NC}"
echo "----------------------------------------"

# Check Splunk
check_service "Splunk Daemon" "$SPLUNK_HOME/bin/splunk status | grep -q running" || FAILED=$((FAILED+1))

# Check SSH
check_service "SSH Service" "systemctl is-active sshd" || FAILED=$((FAILED+1))

# Check UFW
check_service "UFW Firewall" "ufw status | grep -q active" || FAILED=$((FAILED+1))

echo ""
echo -e "${YELLOW}Network Ports:${NC}"
echo "----------------------------------------"

# Check Splunk Web (8000)
check_service "Splunk Web (8000)" "netstat -tulpn 2>/dev/null | grep -q ':8000' || ss -tulpn | grep -q ':8000'" || FAILED=$((FAILED+1))

# Check Splunk Management (8089)
check_service "Splunk Mgmt (8089)" "netstat -tulpn 2>/dev/null | grep -q ':8089' || ss -tulpn | grep -q ':8089'" || FAILED=$((FAILED+1))

# Check Forwarder Input (9997)
check_service "Splunk UF (9997)" "netstat -tulpn 2>/dev/null | grep -q ':9997' || ss -tulpn | grep -q ':9997'" || FAILED=$((FAILED+1))

# Check Syslog Input (514/udp)
check_service "Syslog (514/udp)" "netstat -ulpn 2>/dev/null | grep -q ':514' || ss -ulpn | grep -q ':514'" || FAILED=$((FAILED+1))

echo ""
echo -e "${YELLOW}Data Ingestion:${NC}"
echo "----------------------------------------"

# Check disk space
DISK_USAGE=$(df -h /opt | awk 'NR==2 {print $5}' | sed 's/%//')
echo -n "Disk Usage: ${DISK_USAGE}%... "
if [ "$DISK_USAGE" -lt 80 ]; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${YELLOW}WARNING${NC}"
fi

# Check Splunk indexing (last 1 hour)
echo -n "Recent Windows Events (last 1h)... "
EVENT_COUNT=$($SPLUNK_HOME/bin/splunk search "index=main sourcetype=WinEventLog earliest=-1h" -auth admin:changeme 2>/dev/null | grep -c "_time" || echo "0")
if [ "$EVENT_COUNT" -gt 0 ]; then
    echo -e "${GREEN}OK ($EVENT_COUNT events)${NC}"
else
    echo -e "${RED}FAILED (0 events)${NC}"
    FAILED=$((FAILED+1))
fi

# Check firewall logs
echo -n "Recent Firewall Logs (last 1h)... "
FW_COUNT=$($SPLUNK_HOME/bin/splunk search "index=main sourcetype=opnsense earliest=-1h" -auth admin:changeme 2>/dev/null | grep -c "_time" || echo "0")
if [ "$FW_COUNT" -gt 0 ]; then
    echo -e "${GREEN}OK ($FW_COUNT events)${NC}"
else
    echo -e "${YELLOW}WARNING (0 events - may be normal if no traffic)${NC}"
fi

echo ""
echo -e "${YELLOW}Splunk Internal Status:${NC}"
echo "----------------------------------------"

# Check Splunk license
$SPLUNK_HOME/bin/splunk list licenser-groups -auth admin:changeme 2>/dev/null | head -3 || echo "License status: Unable to check"

# Check index sizes
echo ""
echo -e "${CYAN}Index Sizes:${NC}"
$SPLUNK_HOME/bin/splunk list index -auth admin:changeme 2>/dev/null | grep -E "Index|Current|Max" | head -10 || echo "Unable to retrieve index info"

echo ""
echo -e "${CYAN}========================================${NC}"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}  All checks passed! Lab is healthy.    ${NC}"
elif [ $FAILED -lt 3 ]; then
    echo -e "${YELLOW}  $FAILED check(s) failed. Review above.${NC}"
else
    echo -e "${RED}  $FAILED checks failed. Lab needs attention.${NC}"
fi
echo -e "${CYAN}========================================${NC}"

exit $FAILED
