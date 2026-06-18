#!/bin/bash
# Master audit script for World River
# Runs comprehensive checks on feeds and links

set -e

echo "🌍 World River Audit Suite"
echo "=========================================="
echo ""

# 1. Quick feed check
echo "📡 Step 1: Feed Health Check"
python watch_feeds.py --threshold 3
echo ""

# 2. Quick paywall audit
echo "🔍 Step 2: Quick Paywall Audit (sampling)"
python audit_links.py --quick
echo ""

# 3. Suggest alternatives
echo "💡 Step 3: Suggesting Free Alternatives"
python audit_links.py --find-free
echo ""

echo "=========================================="
echo "✅ Audit complete!"
echo ""
echo "Results:"
echo "  • feed_health.json — Feed response times"
echo "  • audit_results.json — Paywall findings"
echo "  • suggested_sources.json — Free alternatives"
echo ""
echo "For full paywall audit (all links), run:"
echo "  python audit_links.py"
echo ""
