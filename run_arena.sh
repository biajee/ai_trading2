#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║           🤖 AI TRADING ARENA 🤖                         ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check .env file
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Choose an option:"
echo "1) Run Trading Arena"
echo "2) Run Dashboard"
echo "3) Run Both (Arena + Dashboard)"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo "🚀 Starting Trading Arena..."
        python main.py
        ;;
    2)
        echo "📊 Starting Dashboard..."
        python dashboard.py
        ;;
    3)
        echo "🚀 Starting both Arena and Dashboard..."
        python dashboard.py &
        sleep 2
        python main.py
        ;;
    *)
        echo "❌ Invalid choice"
        ;;
esac
