#!/bin/bash
# Xavier Framework Greeting Display Script
# Displays beautiful ANSI art greetings for various occasions

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD_CYAN='\033[1;36m'
BOLD_WHITE='\033[1;37m'
LIGHT_WHITE='\033[0;97m'
LIGHT_CYAN='\033[0;96m'
BOLD_GREEN='\033[1;32m'
NC='\033[0m' # No Color

# Get occasion type (default: welcome)
OCCASION="${1:-welcome}"
VERSION="${2:-1.1.9}"

# Function to display Xavier logo
show_xavier_logo() {
    echo -e "${LIGHT_CYAN}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${LIGHT_CYAN}║                                                                       ║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}  ${BOLD_CYAN}██╗  ██╗ █████╗ ██╗   ██╗██╗███████╗██████╗${NC}                        ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}  ${BOLD_CYAN}╚██╗██╔╝██╔══██╗██║   ██║██║██╔════╝██╔══██╗${NC}                       ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}   ${BOLD_CYAN}╚███╔╝ ███████║╚██╗ ██╔╝██║█████╗  ██████╔╝${NC}                       ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}   ${BOLD_CYAN}██╔██╗ ██╔══██║ ╚████╔╝ ██║██╔══╝  ██╔══██╗${NC}                       ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}  ${BOLD_CYAN}██╔╝ ██╗██║  ██║  ╚██╔╝  ██║███████╗██║  ██║${NC}                       ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║${NC}  ${BOLD_CYAN}╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝╚══════╝╚═╝  ╚═╝${NC}                       ${LIGHT_CYAN}║${NC}"
    echo -e "${LIGHT_CYAN}║                                                                       ║${NC}"
}

# Function to display mini banner
show_mini_banner() {
    echo -e "${BOLD_CYAN}╔═══════════════════════════════════════════╗${NC}"
    echo -e "${BOLD_CYAN}║  XAVIER  │  Enterprise SCRUM Framework     ║${NC}"
    echo -e "${BOLD_CYAN}╚═══════════════════════════════════════════╝${NC}"
}

# Display based on occasion
case "$OCCASION" in
    "welcome")
        echo
        show_xavier_logo
        echo -e "${LIGHT_CYAN}║${NC}              ${BOLD_WHITE}Enterprise SCRUM Framework${NC}                             ${LIGHT_CYAN}║${NC}"
        echo -e "${LIGHT_CYAN}║${NC}                    ${LIGHT_WHITE}Version $VERSION${NC}                                     ${LIGHT_CYAN}║${NC}"
        echo -e "${LIGHT_CYAN}║                                                                       ║${NC}"
        echo -e "${LIGHT_CYAN}╠═══════════════════════════════════════════════════════════════════════╣${NC}"
        echo -e "${LIGHT_CYAN}║${NC}                                                                       ${LIGHT_CYAN}║${NC}"
        echo -e "${LIGHT_CYAN}║${NC}  ${LIGHT_WHITE}Welcome to Xavier! Your enterprise development assistant.${NC}          ${LIGHT_CYAN}║${NC}"
        echo -e "${LIGHT_CYAN}║${NC}                                                                       ${LIGHT_CYAN}║${NC}"
        echo -e "${LIGHT_CYAN}║${NC}  📋 Create stories with ${CYAN}/create-story${NC}                                ${LIGHT_CYAN}║${NC}"
        echo -e "${LIGHT_CYAN}║${NC}  🏃 Start sprints with ${CYAN}/start-sprint${NC}                                 ${LIGHT_CYAN}║${NC}"
        echo -e "${LIGHT_CYAN}║${NC}  📊 Check progress with ${CYAN}/show-backlog${NC}                               ${LIGHT_CYAN}║${NC}"
        echo -e "${LIGHT_CYAN}║${NC}  💡 Get help with ${CYAN}/xavier-help${NC}                                      ${LIGHT_CYAN}║${NC}"
        echo -e "${LIGHT_CYAN}║                                                                       ║${NC}"
        echo -e "${LIGHT_CYAN}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
        echo
        ;;

    "sprint-start")
        echo
        show_mini_banner
        echo
        echo -e "${GREEN}🚀 Sprint Started Successfully!${NC}"
        echo
        echo -e "${LIGHT_WHITE}Remember:${NC}"
        echo "  • Tasks execute sequentially"
        echo "  • Tests must be written first"
        echo "  • 100% coverage required"
        echo "  • Clean Code enforced"
        echo
        ;;

    "sprint-end")
        echo
        show_mini_banner
        echo
        echo -e "${GREEN}✅ Sprint Completed!${NC}"
        echo
        echo -e "${LIGHT_WHITE}Sprint Summary:${NC}"
        echo "  • Check velocity with /xavier-stats"
        echo "  • Review completed items"
        echo "  • Plan next sprint with /create-sprint"
        echo
        ;;

    "update-available")
        echo
        echo -e "${YELLOW}╔═══════════════════════════════════════════╗${NC}"
        echo -e "${YELLOW}║      📦 New Xavier Update Available!       ║${NC}"
        echo -e "${YELLOW}╚═══════════════════════════════════════════╝${NC}"
        echo
        echo "Run ${CYAN}/xavier-update${NC} to get the latest features"
        echo
        ;;

    "daily")
        # Random daily tips
        TIPS=(
            "💡 Tip: Use /create-project for AI-powered project setup"
            "💡 Tip: Keep stories under 13 points for better velocity"
            "💡 Tip: Break large tasks into smaller subtasks"
            "💡 Tip: Review your velocity after each sprint"
            "💡 Tip: Use /xavier-update to check for updates"
        )
        RANDOM_TIP=${TIPS[$RANDOM % ${#TIPS[@]}]}

        echo
        show_mini_banner
        echo
        echo -e "${LIGHT_WHITE}$RANDOM_TIP${NC}"
        echo
        ;;

    "mini")
        show_mini_banner
        ;;

    *)
        echo "Usage: $0 [welcome|sprint-start|sprint-end|update-available|daily|mini] [version]"
        ;;
esac