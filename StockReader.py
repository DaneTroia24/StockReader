import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from datetime import datetime, timedelta
os.system('cls' if os.name == 'nt' else 'clear')


def get_stock_data(api_key, ticker, days_tracked):    
    # Calculate date range 
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=int(days_tracked))).strftime('%Y-%m-%d')
    
    # Build API URL
    url = "https://api.polygon.io/v2/aggs/ticker/" + ticker + f"/range/1/day/{start_date}/{end_date}"
    
    # API parameters
    params = {
        'adjusted': 'true',
        'sort': 'asc',
        'apikey': api_key
    }
    
    # Make API request
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if 'results' in data and data['results']:
            # Convert to DataFrame
            df = pd.DataFrame(data['results'])
            
            # Convert timestamp to readable date
            df['date'] = pd.to_datetime(df['t'], unit='ms')
            df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')
            
            # Rename columns to be more readable
            df = df.rename(columns={
                'o': 'open',
                'h': 'high', 
                'l': 'low',
                'c': 'close',
                'v': 'volume'
            })
            
            # Select only the columns needed
            final_df = df[['date', 'date_str', 'open', 'high', 'low', 'close', 'volume']].copy()
            
            # Round prices to 2 decimal places
            for col in ['open', 'high', 'low', 'close']:
                final_df[col] = final_df[col].round(2)
            
            return final_df
            
        else:
            print("No data found in API response")
            return None
    else:
        print(f"API Error: {response.status_code} - {response.text}")
        return None

def create_price_graph(stock, days_tracked, df, filename="stock_chart.png"):
    if df is None:
        print("No data to graph")
        return
    
    try:
        plt.figure(figsize=(12, 8))
        
        # Plot the closing price
        plt.plot(df['date'], df['close'], linewidth=2, color='#1f77b4', label='Close Price')
        
        # Add high and low as a shaded area
        plt.fill_between(df['date'], df['low'], df['high'], alpha=0.3, color='lightblue', label='Daily Range (High-Low)')
        
        # Customize the graph
        plt.title(stock + ' Stock Price - Last ' + days_tracked + ' Days', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Price ($)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        days_tracked = int(days_tracked)
        x_int = max(1, days_tracked // 15)

        # Format x-axis dates
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=int(x_int)))
        plt.xticks(rotation=45)
        
        # Add some padding to the y-axis
        y_min = df['low'].min() * 0.995
        y_max = df['high'].max() * 1.005
        plt.ylim(y_min, y_max)
        
        # Add latest price annotation
        latest_price = df['close'].iloc[-1]
        latest_date = df['date'].iloc[-1]
        plt.annotate(f'Latest: ${latest_price:.2f}', 
                    xy=(latest_date, latest_price),
                    xytext=(10, 10), textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        # Tight layout to prevent label cutoff
        plt.tight_layout()
        
        # Save the graph
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        
        # Show the graph
        plt.show()
        
    except Exception as e:
        print(f"Error creating graph: {e}")

def save_to_text_file(df, filename="stock_data.txt"):    
    if df is None:
        print("No data to save")
        return
    
    try:
        with open(filename, 'w') as f:
            # Write header
            f.write("Stock Data\n")
            f.write("=" * 50 + "\n")
            f.write(f"Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Write column headers
            f.write(f"{'Date':<12} {'Open':<8} {'High':<8} {'Low':<8} {'Close':<8} {'Volume':<12}\n")
            f.write("-" * 60 + "\n")
            
            # Write data rows
            for _, row in df.iterrows():
                f.write(f"{row['date_str']:<12} "
                       f"{row['open']:<8} "
                       f"{row['high']:<8} "
                       f"{row['low']:<8} "
                       f"{row['close']:<8} "
                       f"{row['volume']:<12}\n")
        
    except Exception as e:
        print(f"Error saving file: {e}")

def get_api_key():
    # Try to get API key from environment variable
    api_key = os.getenv('POLYGON_API_KEY')
    
    if api_key:
        return api_key
    else:        
        # Fallback to user input
        api_key = input("Enter your Polygon.io API key: ").strip()
        
        if not api_key:
            print("API key is required to continue")
            return None
            
        return api_key

if __name__ == "__main__":
    print("=== Stock Price Tracker ===\n")
    
    # Get API key from environment or user input
    API_KEY = get_api_key()
    
    if not API_KEY:
        print("Exiting...")
        exit()

    stock = input("\nEnter a Ticker to Track: ").upper()
    days_tracked = input("Enter Number of Days: ")
    
    # Get stock data
    stock_data = get_stock_data(API_KEY, stock, days_tracked)
    
    if stock_data is not None:
        print(f"\nSuccessfully retrieved data for {stock}")
        
        save_to_text_file(stock_data)
        create_price_graph(stock, days_tracked, stock_data)
    else:
        print("Failed to retrieve data")
