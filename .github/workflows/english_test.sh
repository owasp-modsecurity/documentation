#!/bin/bash
# Content must be American English. Literal protocol names from the audit log
# spec (Sanitised-*) and Relearn CSS class names (grey) are exempt.
EXEMPT='Sanitised-(Args|Request-Headers|Response-Headers)|badge cstyle grey'
matches=$(grep -Ri -f .github/workflows/en_GB_wordlist content/ | grep -v -E "$EXEMPT")

[ -z "$matches" ] && exit 0

echo -e "\n****************************** Offending Matches *******************************"
echo "$matches"
exit 1
