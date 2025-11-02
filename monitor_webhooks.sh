#!/bin/bash

# Insurance SOA Webhook Monitor
# This script monitors the webhook server and checks for incoming forms

echo "=========================================="
echo "  Insurance SOA Webhook Monitor"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SERVER_URL="http://localhost:5001"
CHECK_INTERVAL=5  # seconds between checks

# Function to check if server is running
check_server() {
    if curl -s "$SERVER_URL/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Server is running${NC}"
        return 0
    else
        echo -e "${RED}✗ Server is not running${NC}"
        echo "  Start it with: python3 src/webhook_server.py"
        return 1
    fi
}

# Function to get server statistics
get_stats() {
    local stats=$(curl -s "$SERVER_URL/status" 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo -e "\n${YELLOW}Current Statistics:${NC}"
        echo "$stats" | python3 -m json.tool | grep -E '"total_fact_finds"|"total_automation_forms"|"total_matches"|"confident_matches"' | sed 's/,$//'
    fi
}

# Function to count files
count_files() {
    local fact_finds=$(find data/forms/fact_finds -name "*.json" 2>/dev/null | wc -l)
    local automation=$(find data/forms/automation_forms -name "*.json" 2>/dev/null | wc -l)
    local reports=$(find data/reports -name "*.txt" 2>/dev/null | wc -l)

    echo -e "\n${YELLOW}File Counts:${NC}"
    echo "  Fact Find Forms:       $fact_finds"
    echo "  Automation Forms:      $automation"
    echo "  Generated Reports:     $reports"
}

# Function to show recent files
show_recent() {
    echo -e "\n${YELLOW}Recent Activity (last 5):${NC}"

    echo -e "\n  ${GREEN}Recent Fact Finds:${NC}"
    find data/forms/fact_finds -name "*.json" -type f 2>/dev/null | xargs ls -lt 2>/dev/null | head -5 | awk '{print "    "$6" "$7" "$8" - "$9}'

    echo -e "\n  ${GREEN}Recent Automation Forms:${NC}"
    find data/forms/automation_forms -name "*.json" -type f 2>/dev/null | xargs ls -lt 2>/dev/null | head -5 | awk '{print "    "$6" "$7" "$8" - "$9}'

    echo -e "\n  ${GREEN}Recent Reports:${NC}"
    find data/reports -name "*.txt" -type f 2>/dev/null | xargs ls -lt 2>/dev/null | head -5 | awk '{print "    "$6" "$7" "$8" - "$9}'
}

# Function to test webhook endpoints
test_endpoints() {
    echo -e "\n${YELLOW}Testing Endpoints:${NC}"

    # Test health endpoint
    if curl -s "$SERVER_URL/health" > /dev/null 2>&1; then
        echo -e "  /health              ${GREEN}✓${NC}"
    else
        echo -e "  /health              ${RED}✗${NC}"
    fi

    # Test status endpoint
    if curl -s "$SERVER_URL/status" > /dev/null 2>&1; then
        echo -e "  /status              ${GREEN}✓${NC}"
    else
        echo -e "  /status              ${RED}✗${NC}"
    fi

    # Test matches endpoint
    if curl -s "$SERVER_URL/matches" > /dev/null 2>&1; then
        echo -e "  /matches             ${GREEN}✓${NC}"
    else
        echo -e "  /matches             ${RED}✗${NC}"
    fi
}

# Main monitoring loop
main() {
    clear

    # Initial check
    if ! check_server; then
        echo -e "\n${RED}Please start the webhook server first:${NC}"
        echo "  cd $(pwd)"
        echo "  python3 src/webhook_server.py"
        exit 1
    fi

    echo -e "\n${GREEN}Monitoring webhook activity...${NC}"
    echo "Press Ctrl+C to stop"
    echo ""

    # Store initial counts
    prev_fact_finds=$(find data/forms/fact_finds -name "*.json" 2>/dev/null | wc -l)
    prev_automation=$(find data/forms/automation_forms -name "*.json" 2>/dev/null | wc -l)

    while true; do
        # Clear screen and show header
        clear
        echo "=========================================="
        echo "  Insurance SOA Webhook Monitor"
        echo "  $(date '+%Y-%m-%d %H:%M:%S')"
        echo "=========================================="

        # Check server status
        check_server || exit 1

        # Get current counts
        curr_fact_finds=$(find data/forms/fact_finds -name "*.json" 2>/dev/null | wc -l)
        curr_automation=$(find data/forms/automation_forms -name "*.json" 2>/dev/null | wc -l)

        # Check for new forms
        if [ "$curr_fact_finds" -gt "$prev_fact_finds" ]; then
            echo -e "\n${GREEN}🔔 NEW FACT FIND FORM RECEIVED!${NC}"
            prev_fact_finds=$curr_fact_finds
        fi

        if [ "$curr_automation" -gt "$prev_automation" ]; then
            echo -e "\n${GREEN}🔔 NEW AUTOMATION FORM RECEIVED!${NC}"
            prev_automation=$curr_automation
        fi

        # Show statistics
        get_stats
        count_files
        test_endpoints
        show_recent

        echo -e "\n${YELLOW}Webhook URLs to configure in Gravity Forms:${NC}"
        echo "  Fact Find:    $SERVER_URL/ff"
        echo "  Automation:   $SERVER_URL/automation"

        echo -e "\n${YELLOW}Refreshing in $CHECK_INTERVAL seconds...${NC}"
        sleep $CHECK_INTERVAL
    done
}

# Run the monitor
main