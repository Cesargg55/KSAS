#!/bin/bash
# KSAS - Merge Database Utility (Bash wrapper)

echo "======================================================"
echo "   KSAS - Database Merge Utility"
echo "======================================================"
echo ""
echo "Merge multiple analyzed_stars.json files"
echo ""

python3 merge_databases.py "$@"
