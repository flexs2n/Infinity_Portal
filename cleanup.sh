#!/bin/bash

echo "🧹 Cleaning up infinity_portal structure..."

# Remove files from root
echo "Removing misplaced files from root..."
rm -f __init__.py
rm -f autonomous_strategy_system.py
rm -f dashboard_generator.py
rm -f divergence_detector.py
rm -f exchange_monitor.py
rm -f trader_interface.py

echo "✅ Root cleanup complete"

# Fix typo in agents
echo "Fixing agents/__init__.py typo..."
if [ -f "agents/__init_.py" ]; then
    mv agents/__init_.py agents/__init__.py
fi

# Fix typo in data_collectors
echo "Fixing data_collectors filename..."
if [ -f "data_collectors/price_data_collectors.py" ]; then
    mv data_collectors/price_data_collectors.py data_collectors/price_data_collector.py
fi

# Create missing directories
echo "Creating missing directories..."
mkdir -p docs
mkdir -p configs
mkdir -p scripts
mkdir -p data/{historical,social,news,backtest_results}
mkdir -p tests/unit
mkdir -p tests/integration
mkdir -p tests/fixtures

echo "✅ Directory structure complete"

# Set permissions
echo "Setting permissions..."
chmod +x cleanup.sh

echo "🎉 Cleanup complete!"
echo ""
echo "Next steps:"
echo "1. Move implementation files to infinity_portal/ if they're still in root"
echo "2. Create the new files listed above"
echo "3. Run: pip install -e ."
echo "4. Run: pytest tests/"