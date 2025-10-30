"""Web dashboard for visualizing trading arena"""
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
from datetime import datetime
import json
import os
from market_data_service import get_market_service
from config import Config
import random


def generate_fallback_market_data():
    """Generate fallback market data from config trading pairs"""
    markets_data = []
    trading_pairs = Config.TRADING_PAIRS
    
    # Sample prices for common cryptos (fallback only)
    sample_prices = {
        "BTC": 67000,
        "ETH": 3500,
        "SOL": 170,
        "BNB": 600,
        "ADA": 0.5,
        "DOT": 7.5,
        "MATIC": 0.8,
        "AVAX": 35,
        "LINK": 15,
        "UNI": 8
    }
    
    for pair in trading_pairs:
        # Extract symbol (e.g., "BTC/USDT" -> "BTC")
        symbol = pair.split("/")[0]
        base_price = sample_prices.get(symbol, 100)  # Default to 100 if unknown
        
        markets_data.append({
            "symbol": symbol,
            "price": base_price * random.uniform(0.98, 1.02),  # Add small variation
            "change": random.uniform(-3, 3)
        })
    
    return markets_data


# Initialize Dash app
app = dash.Dash(__name__)

# Initialize market data service
market_service = get_market_service()

# Load real agent data from arena state file
def load_agent_data():
    """Load actual agent data from arena state file"""
    state_file = "arena_state.json"

    # Check if state file exists
    if not os.path.exists(state_file):
        # Return placeholder data if arena hasn't run yet
        return [{
            "name": "No Active Arena",
            "value": Config.STARTING_CAPITAL,
            "return": 0.0,
            "trades": 0,
            "positions": {},
            "recent_trades": [],
            "win_rate": 0.0
        }]

    try:
        with open(state_file, 'r') as f:
            state_data = json.load(f)

        agents = []
        for agent in state_data.get("agents", []):
            agents.append({
                "name": agent.get("agent_name", "Unknown"),
                "value": agent.get("portfolio_value", 0),
                "return": agent.get("total_return", 0),
                "trades": agent.get("total_trades", 0),
                "positions": agent.get("positions", {}),
                "recent_trades": agent.get("recent_trades", []),
                "win_rate": agent.get("win_rate", 0.0),
                "cycle_history": agent.get("cycle_history", [])
            })

        return agents if agents else [{
            "name": "No Active Agents",
            "value": Config.STARTING_CAPITAL,
            "return": 0.0,
            "trades": 0,
            "positions": {},
            "recent_trades": [],
            "win_rate": 0.0
        }]
    except Exception as e:
        print(f"Error loading agent data: {e}")
        return [{
            "name": "Error Loading Data",
            "value": Config.STARTING_CAPITAL,
            "return": 0.0,
            "trades": 0,
            "positions": {},
            "recent_trades": [],
            "win_rate": 0.0
        }]

app.layout = html.Div([
    html.Div([
        html.H1("🤖 AI Trading Arena Dashboard", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
        html.H3("Live Competition Tracking", 
                style={'textAlign': 'center', 'color': '#7f8c8d', 'marginBottom': 50}),
    ]),
    
    # Trading Mode Indicator
    html.Div([
        html.H2("📊 MOCK TRADING MODE", 
                id='trading-mode',
                style={
                    'textAlign': 'center',
                    'backgroundColor': '#27ae60',
                    'color': 'white',
                    'padding': '15px',
                    'borderRadius': '10px',
                    'marginBottom': 10
                }),
        html.P(id='data-source-indicator',
               style={
                   'textAlign': 'center',
                   'color': '#7f8c8d',
                   'fontSize': 14,
                   'marginBottom': 20
               })
    ]),
    
    # Leaderboard
    html.Div([
        html.H2("🏆 Leaderboard", style={'color': '#2c3e50', 'marginBottom': 20}),
        html.Div(id='leaderboard-table')
    ], style={'marginBottom': 50}),
    
    # Performance Chart
    html.Div([
        html.H2("📈 Portfolio Performance", style={'color': '#2c3e50', 'marginBottom': 20}),
        dcc.Graph(id='performance-chart')
    ], style={'marginBottom': 50}),
    
    # Arena Status and Market Data
    html.Div([
        html.Div([
            html.H2("🔄 Arena Status", style={'color': '#2c3e50', 'marginBottom': 20}),
            html.Div(id='cycle-info', style={
                'backgroundColor': 'white',
                'padding': '20px',
                'borderRadius': '10px'
            })
        ], style={'flex': '1', 'marginRight': '20px'}),

        html.Div([
            html.H2("💹 Live Market Prices", style={'color': '#2c3e50', 'marginBottom': 20}),
            html.Div(id='market-prices', style={
                'display': 'flex',
                'justifyContent': 'space-around',
                'flexWrap': 'wrap'
            })
        ], style={'flex': '2'}),
    ], style={'display': 'flex', 'marginBottom': 50}),
    
    # Auto-refresh
    dcc.Interval(
        id='interval-component',
        interval=Config.DASHBOARD_UPDATE_INTERVAL*1000,  # Update interval from config
        n_intervals=0
    )
], style={'padding': '40px', 'backgroundColor': '#ecf0f1', 'minHeight': '100vh'})


@app.callback(
    Output('leaderboard-table', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_leaderboard(n):
    """Update leaderboard table with real agent data"""
    agents = load_agent_data()
    rows = []

    for i, agent in enumerate(agents, 1):
        return_color = '#27ae60' if agent['return'] >= 0 else '#e74c3c'

        # Build positions summary
        positions_text = ""
        if agent.get('positions'):
            pos_list = []
            for symbol, pos_data in agent['positions'].items():
                symbol_name = symbol.split('/')[0]
                pnl = pos_data.get('pnl', 0)
                pnl_color = '#27ae60' if pnl >= 0 else '#e74c3c'
                pos_list.append(
                    html.Span([
                        f"{symbol_name}: {pos_data.get('quantity', 0):.4f} ",
                        html.Span(f"({pnl:+.2f})", style={'color': pnl_color})
                    ])
                )
            positions_text = html.Div(pos_list, style={'fontSize': 12, 'color': '#7f8c8d', 'marginTop': 5})

        # Build recent trade info
        recent_trade_text = ""
        if agent.get('recent_trades'):
            last_trade = agent['recent_trades'][-1]
            trade_emoji = "🟢" if last_trade.get('type') == 'buy' else "🔴"
            recent_trade_text = html.Div(
                f"{trade_emoji} Last: {last_trade.get('type', '').upper()} {last_trade.get('symbol', '')} @ ${last_trade.get('price', 0):.2f}",
                style={'fontSize': 11, 'color': '#95a5a6', 'marginTop': 3, 'fontStyle': 'italic'}
            )

        rows.append(
            html.Div([
                html.Div([
                    html.Span(f"{i}. ", style={'fontWeight': 'bold', 'fontSize': 20}),
                    html.Span(agent['name'], style={'fontSize': 18, 'marginRight': 20}),
                    html.Span(f"${agent['value']:,.2f}",
                             style={'fontWeight': 'bold', 'marginRight': 20}),
                    html.Span(f"{agent['return']:+.2f}%",
                             style={'color': return_color, 'fontWeight': 'bold', 'marginRight': 20}),
                    html.Span(f"{agent['trades']} trades", style={'color': '#7f8c8d', 'marginRight': 15}),
                    html.Span(f"Win: {agent.get('win_rate', 0):.1f}%", style={'color': '#3498db', 'fontSize': 14}),
                ]),
                positions_text,
                recent_trade_text
            ], style={
                'padding': '15px',
                'marginBottom': '10px',
                'backgroundColor': 'white',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            })
        )
    return rows


@app.callback(
    Output('performance-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_chart(n):
    """Update performance chart with real cycle history"""
    agents = load_agent_data()
    fig = go.Figure()

    # Add traces for each agent
    for agent in agents:
        cycle_history = agent.get('cycle_history', [])

        if cycle_history:
            # Use actual cycle history
            cycles = [h['cycle'] for h in cycle_history]
            values = [h['portfolio_value'] for h in cycle_history]

            # Add hover text with additional info
            hover_text = [
                f"Cycle {h['cycle']}<br>"
                f"Value: ${h['portfolio_value']:,.2f}<br>"
                f"Return: {h['total_return']:+.2f}%<br>"
                f"Trades: {h['total_trades']}<br>"
                f"Win Rate: {h['win_rate']:.1f}%"
                for h in cycle_history
            ]

            fig.add_trace(go.Scatter(
                x=cycles,
                y=values,
                mode='lines+markers',
                name=agent['name'],
                line=dict(width=3),
                hovertext=hover_text,
                hoverinfo='text'
            ))
        else:
            # No cycle history yet - show current state only
            fig.add_trace(go.Scatter(
                x=[0, 1],
                y=[Config.STARTING_CAPITAL, agent['value']],
                mode='lines+markers',
                name=agent['name'],
                line=dict(width=3, dash='dash')
            ))

    fig.update_layout(
        title='Portfolio Value Over Trading Cycles',
        xaxis_title='Cycle Number',
        yaxis_title='Portfolio Value ($)',
        hovermode='closest',
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
    )

    return fig


@app.callback(
    Output('cycle-info', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_cycle_info(n):
    """Update cycle information"""
    state_file = "arena_state.json"

    if not os.path.exists(state_file):
        return html.Div([
            html.P("⏸️ Arena not started", style={'fontSize': 18, 'fontWeight': 'bold'}),
            html.P("Waiting for trading cycles...", style={'color': '#7f8c8d', 'marginTop': 10})
        ])

    try:
        with open(state_file, 'r') as f:
            state_data = json.load(f)

        current_cycle = state_data.get('current_cycle', 0)
        timestamp = state_data.get('timestamp', '')
        num_agents = len(state_data.get('agents', []))

        # Format timestamp
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime('%H:%M:%S')
        except:
            time_str = 'Unknown'

        return html.Div([
            html.Div([
                html.Span("Cycle: ", style={'color': '#7f8c8d'}),
                html.Span(f"#{current_cycle}", style={'fontSize': 24, 'fontWeight': 'bold', 'color': '#2c3e50'})
            ], style={'marginBottom': 15}),

            html.Div([
                html.Span("Active Agents: ", style={'color': '#7f8c8d'}),
                html.Span(f"{num_agents}", style={'fontSize': 18, 'fontWeight': 'bold', 'color': '#3498db'})
            ], style={'marginBottom': 15}),

            html.Div([
                html.Span("Last Update: ", style={'color': '#7f8c8d'}),
                html.Span(time_str, style={'fontSize': 16, 'color': '#27ae60'})
            ]),
        ])

    except Exception as e:
        return html.Div([
            html.P("⚠️ Error loading cycle info", style={'color': '#e74c3c'}),
            html.P(str(e), style={'fontSize': 12, 'color': '#7f8c8d'})
        ])


@app.callback(
    [Output('market-prices', 'children'),
     Output('data-source-indicator', 'children')],
    Input('interval-component', 'n_intervals')
)
def update_market_prices(n):
    """Update market prices with real-time data from Binance"""
    try:
        # Fetch real-time market data from Binance
        markets_data = market_service.format_for_display()
        
        if not markets_data:
            # Fallback to sample data based on config
            markets_data = generate_fallback_market_data()
    except Exception as e:
        print(f"Error fetching market data: {e}")
        # Fallback to sample data based on config
        markets_data = generate_fallback_market_data()
    
    cards = []
    for market in markets_data:
        change_color = '#27ae60' if market['change'] >= 0 else '#e74c3c'
        
        # Add volume info if available
        volume_text = f"Vol: {market.get('volume', 0):,.0f}" if 'volume' in market else ""
        
        # Indicator based on data source
        source = market.get('source', 'unknown')
        if source == 'binance':
            live_indicator = "🔴 LIVE - Binance"
            indicator_color = '#e74c3c'
        else:
            live_indicator = "⚪ Simulated"
            indicator_color = '#95a5a6'
        
        cards.append(
            html.Div([
                html.H3(market['symbol'], style={'color': '#2c3e50', 'marginBottom': 10}),
                html.H2(f"${market['price']:,.2f}", 
                       style={'color': '#34495e', 'marginBottom': 5}),
                html.P(f"{market['change']:+.2f}%", 
                      style={'color': change_color, 'fontSize': 18, 'fontWeight': 'bold', 'marginBottom': 5}),
                html.P(volume_text, 
                      style={'color': '#95a5a6', 'fontSize': 12, 'margin': 0}) if volume_text else None,
                html.P(live_indicator, 
                      style={'color': indicator_color, 'fontSize': 10, 'marginTop': 10, 'fontWeight': 'bold'})
            ], style={
                'padding': '20px',
                'backgroundColor': 'white',
                'borderRadius': '10px',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
                'minWidth': '200px',
                'margin': '10px'
            })
        )
    
    # Determine overall data source indicator
    is_real = markets_data[0].get('source') == 'binance' if markets_data else False
    data_source_text = "📡 Data Source: Live from Binance API" if is_real else "📡 Data Source: Simulated (Binance API unavailable)"
    
    return cards, data_source_text


if __name__ == '__main__':
    dashboard_url = f"http://{Config.DASHBOARD_HOST}:{Config.DASHBOARD_PORT}"
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║           📊 TRADING ARENA DASHBOARD 📊                  ║
    ║                                                           ║
    ║   Open {dashboard_url:<43} ║
    ║                                                           ║
    ║   🔴 LIVE market data from Binance API                   ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Test market data connection
    print("\n🔄 Testing Binance API connection...")
    try:
        test_data = market_service.get_all_tickers()
        if test_data:
            print("✅ Successfully connected to Binance API")
            for symbol, data in test_data.items():
                print(f"   {symbol}: ${data['price']:,.2f} ({data['change_percent']:+.2f}%)")
        else:
            print("⚠️  No data received from Binance API")
    except Exception as e:
        print(f"⚠️  Error connecting to Binance API: {e}")
        print("   Dashboard will use fallback data")
    
    print(f"\n🚀 Starting dashboard server on {Config.DASHBOARD_HOST}:{Config.DASHBOARD_PORT}...\n")
    app.run(debug=True, host=Config.DASHBOARD_HOST, port=Config.DASHBOARD_PORT)
