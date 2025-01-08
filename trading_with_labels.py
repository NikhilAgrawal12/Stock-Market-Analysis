"""
import pandas as pd

# Load data
ticker_file = r"AAL.csv"
df = pd.read_csv(ticker_file)

# Convert 'Date' to datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Initialize capital for both strategies
initial_capital = 100

# Add Year column to df
df['Year'] = df['Date'].dt.year

# Initialize lists to store annual differences
annual_differences = []
yearly_results = []

# Process data for each year
years = df['Year'].unique()

for year in years:
    year_data = df[df['Year'] == year]
    
    # Calculate buy-and-hold capital for the year
    first_open_price = year_data.iloc[0]['Open']
    last_close_price = year_data.iloc[-1]['Adj Close']
    buy_and_hold_yearly = (initial_capital / first_open_price) * last_close_price
    
    # Calculate label-based capital for the year
    label_based_capital = initial_capital
    holding_stock = False
    stock_quantity = 0
    
    for i, row in year_data.iterrows():
        if row['Weekday'] == 'Friday':  # Ensure 'Friday' is in correct format
            label = row['Label']
            close_price = row['Adj Close']
            
            if pd.notna(label):  # Ensure label is not missing
                if label == 'Green' and not holding_stock:
                    open_price = row['Open']  # Buy stock at opening price
                    stock_quantity = label_based_capital / open_price
                    holding_stock = True
                elif label == 'Red' and holding_stock:
                    label_based_capital = stock_quantity * close_price  # Sell stock at closing price
                    holding_stock = False

    # If we are holding stock at the end of the year, sell it
    if holding_stock:
        label_based_capital = stock_quantity * year_data.iloc[-1]['Adj Close']

    # Calculate annual difference
    annual_difference = label_based_capital - buy_and_hold_yearly
    annual_differences.append(annual_difference)
    
    # Store results for each year
    yearly_results.append({
        'Year': year,
        'Buy-and-Hold Capital': buy_and_hold_yearly,
        'Label-Based Capital': label_based_capital,
        'Annual Difference': annual_difference
    })

# Print results for each year
for result in yearly_results:
    print(f"Year: {result['Year']}")
    print(f"Buy-and-Hold Final Capital: {result['Buy-and-Hold Capital']}")
    print(f"Label-Based Strategy Final Capital: {result['Label-Based Capital']}")
    print(f"Annual Difference: {result['Annual Difference']}")
    print()

# Calculate and print minimum, maximum, and average annual differences
min_difference = min(annual_differences)
max_difference = max(annual_differences)
avg_difference = sum(annual_differences) / len(annual_differences)

print(f"Minimum Annual Difference: {min_difference}")
print(f"Maximum Annual Difference: {max_difference}")
print(f"Average Annual Difference: {avg_difference}")
"""

import pandas as pd
import matplotlib.pyplot as plt

# Load the stock data
ticker_file = r"AAL.csv"
df = pd.read_csv(ticker_file)

# Convert 'Date' to datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Add a Year column and ensure it's sorted by Date
df['Year'] = df['Date'].dt.year
df = df.sort_values(by='Date')

# Filter for only the years 2022 and 2023
df = df[df['Year'].isin([2022, 2023])]

# Initialize parameters
initial_capital = 100
years = [2022, 2023]
results = {}

for year in years:
    # Filter data for the specific year
    year_data = df[df['Year'] == year].reset_index(drop=True)

    # Initialize variables
    capital = initial_capital
    balance_history = []  # To store weekly account balances
    holding_stock = False
    stock_quantity = 0
    min_balance = float('inf')
    max_balance = -float('inf')
    max_growth_weeks = 0
    max_decline_weeks = 0
    current_growth_streak = 0
    current_decline_streak = 0

    # Loop through the year data to simulate trading
    for i, row in year_data.iterrows():
        # Only make a decision on Fridays
        if row['Weekday'] == 'Friday':
            next_label = row['Label']
            close_price = row['Adj Close']

            # If next week is predicted to be green
            if next_label == 'Green':
                if not holding_stock:
                    # Buy stock with all capital
                    stock_quantity = capital / close_price
                    holding_stock = True
                    capital = 0
            elif next_label == 'Red' and holding_stock:
                # Sell stock and convert back to cash
                capital = stock_quantity * close_price
                holding_stock = False
                stock_quantity = 0

            # Track the current balance (stock value or cash)
            current_balance = capital if not holding_stock else stock_quantity * close_price
            balance_history.append(current_balance)

            # Update min and max balance
            if current_balance < min_balance:
                min_balance = current_balance
            if current_balance > max_balance:
                max_balance = current_balance

            # Update growth/decline streaks
            if len(balance_history) > 1:
                if current_balance > balance_history[-2]:
                    current_growth_streak += 1
                    current_decline_streak = 0
                elif current_balance < balance_history[-2]:
                    current_decline_streak += 1
                    current_growth_streak = 0

                # Track the longest growth and decline streaks
                max_growth_weeks = max(max_growth_weeks, current_growth_streak)
                max_decline_weeks = max(max_decline_weeks, current_decline_streak)

    # Final balance at the end of the year
    final_balance = balance_history[-1]

    # Store the results for the year
    results[year] = {
        'balance_history': balance_history,
        'final_balance': final_balance,
        'min_balance': min_balance,
        'max_balance': max_balance,
        'max_growth_weeks': max_growth_weeks,
        'max_decline_weeks': max_decline_weeks,
    }

# Plotting the account growth over time for both years
plt.figure(figsize=(10, 6))
for year in years:
    plt.plot(results[year]['balance_history'], label=f"Year {year}")
plt.xlabel("Week Number")
plt.ylabel("Account Balance ($)")
plt.title("Growth of Account Balance Over Time for 2022 and 2023")
plt.legend()
plt.grid(True)
plt.show()

# Print out results for each year
for year in years:
    print(f"Results for Year: {year}")
    print(f"Final Account Balance: ${results[year]['final_balance']:.2f}")
    print(f"Minimum Account Balance: ${results[year]['min_balance']:.2f}")
    print(f"Maximum Account Balance: ${results[year]['max_balance']:.2f}")
    print(f"Longest Growth Streak (weeks): {results[year]['max_growth_weeks']}")
    print(f"Longest Decline Streak (weeks): {results[year]['max_decline_weeks']}")
    print()

# Calculate the average and volatility (standard deviation) of weekly balances for both years
for year in years:
    balance_history = results[year]['balance_history']
    average_balance = sum(balance_history) / len(balance_history)
    volatility_balance = pd.Series(balance_history).pct_change().std() * 100  # Percent change volatility

    print(f"Year {year}:")
    print(f"  Average Weekly Balance: ${average_balance:.2f}")
    print(f"  Volatility (Std Dev) of Weekly Balance: {volatility_balance:.2f}%")
    print()
