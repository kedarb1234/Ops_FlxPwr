import pandas as pd
import json
from datetime import datetime

# Main function to orchestrate the calls
def main():
    # Load data
    assets_df = load_csv_to_dataframe("assets_base_data.csv", delimiter=";")
    measured_df = load_csv_to_dataframe("measured_20241013.csv", delimiter=";")
    trades_df = load_json_to_dataframe("trades.json")
    market_index_df = load_csv_to_dataframe("market_index_price.csv", delimiter=";")
    imbalance_penalty_df = load_csv_to_dataframe("imbalance_penalty.csv", delimiter=";")
    forecast_a1_df = load_json_to_dataframe("a1.json", flatten=True)
    forecast_a2_df = load_json_to_dataframe("a2.json", flatten=True)
    forecast_a3_df = load_json_to_dataframe("a3.json", flatten=True)
    forecast_a4_df = load_json_to_dataframe("a4.json", flatten=True)

    if any(df is None for df in [assets_df, measured_df, trades_df, market_index_df, imbalance_penalty_df, 
                                forecast_a1_df, forecast_a2_df, forecast_a3_df, forecast_a4_df]):
        print("One or more input files failed to load. Exiting.")
        return

    # Convert measured production from kW to MW (divide by 1000)
    measured_df[['mp_1', 'mp_2', 'mp_3', 'mp_4']] = measured_df[['mp_1', 'mp_2', 'mp_3', 'mp_4']] / 1000

    # Match trades with measured production and save to Excel
    match_trades_with_measured(trades_df, measured_df)

    # Load the trade allocation output
    trade_allocation_df = pd.read_csv("trade_allocation.csv")
    if trade_allocation_df is None:
        print("Failed to load trade_allocation.xlsx. Exiting.")
        return

    # Calculate revenue for each asset and save to CSV
    calculate_asset_revenue(assets_df, trade_allocation_df, market_index_df)

    # Load the asset revenue output
    asset_revenue_df = load_csv_to_dataframe("asset_revenue.csv", delimiter=",")
    if asset_revenue_df is None:
        print("Failed to load asset_revenue.csv. Exiting.")
        return

    # Debug: Print column names to verify
    print("Columns in asset_revenue_df:", asset_revenue_df.columns.tolist())

    # Calculate invoices for each asset and save to CSV
    calculate_invoices(assets_df, trade_allocation_df, asset_revenue_df, market_index_df)

    # Calculate imbalance penalties and save to CSV
    calculate_imbalance_penalty(measured_df, forecast_a1_df, forecast_a2_df, forecast_a3_df, forecast_a4_df, imbalance_penalty_df)

# Function to load CSV files into DataFrames
def load_csv_to_dataframe(file_path, delimiter=";"):
    try:
        df = pd.read_csv(file_path, delimiter=delimiter)
        print(f"Loaded {file_path} successfully.")
        return df
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return None
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

# Function to load JSON files into DataFrames with optional flattening
def load_json_to_dataframe(file_path, flatten=False):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        if flatten and 'values' in data:
            # Convert nested 'values' dictionary to a DataFrame
            df = pd.DataFrame(list(data['values'].items()), columns=['delivery_start', 'forecast'])
            df['delivery_start'] = pd.to_datetime(df['delivery_start'])
            df['forecast'] = df['forecast'] / 1000  # Convert forecast from kW to MW
            df['asset_id'] = data['asset_id']
        else:
            df = pd.DataFrame(data)
        print(f"Loaded {file_path} successfully.")
        return df
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return None
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

# Function to match trades with measured production
def match_trades_with_measured(trades_df, measured_df):
    trades_df['delivery_start'] = pd.to_datetime(trades_df['delivery_start'])
    measured_df['delivery_start'] = pd.to_datetime(measured_df['delivery_start'])
    result = trades_df[['delivery_start', 'quantity']].copy()
    result['mp_1_contribution'] = 0.0
    result['mp_2_contribution'] = 0.0
    result['mp_3_contribution'] = 0.0
    result['mp_4_contribution'] = 0.0
    result['remaining_quantity'] = 0.0
    merged_df = pd.merge(trades_df, measured_df, on='delivery_start', how='left')
    for index, row in merged_df.iterrows():
        remaining = row['quantity']
        mp_1_used = min(remaining, row['mp_1'])
        result.at[index, 'mp_1_contribution'] = mp_1_used
        remaining -= mp_1_used
        mp_2_used = min(remaining, row['mp_2'])
        result.at[index, 'mp_2_contribution'] = mp_2_used
        remaining -= mp_2_used
        mp_3_used = min(remaining, row['mp_3'])
        result.at[index, 'mp_3_contribution'] = mp_3_used
        remaining -= mp_3_used
        mp_4_used = min(remaining, row['mp_4'])
        result.at[index, 'mp_4_contribution'] = mp_4_used
        remaining -= mp_4_used
        result.at[index, 'remaining_quantity'] = max(0, remaining)
    output_file = "trade_allocation.csv"
    result.to_csv(output_file, index=False)
    print(f"Trade allocation saved to {output_file}")

# Function to calculate revenue for each asset
def calculate_asset_revenue(assets_df, trade_allocation_df, market_index_df):
    trade_allocation_df['delivery_start'] = pd.to_datetime(trade_allocation_df['delivery_start'])
    market_index_df['delivery_start'] = pd.to_datetime(market_index_df['delivery_start'])
    revenue_df = pd.merge(trade_allocation_df, market_index_df, on='delivery_start', how='left')
    meter_to_asset = {'mp_1': 'a_1', 'mp_2': 'a_2', 'mp_3': 'a_3', 'mp_4': 'a_4'}
    revenue_df['mp_1_revenue'] = 0.0
    revenue_df['mp_2_revenue'] = 0.0
    revenue_df['mp_3_revenue'] = 0.0
    revenue_df['mp_4_revenue'] = 0.0
    for mp, asset_id in meter_to_asset.items():
        asset = assets_df[assets_df['asset_id'] == asset_id].iloc[0]
        price_model = asset['price_model']
        contribution_col = f"{mp}_contribution"
        if price_model == 'fixed':
            fixed_price = asset['price__eur_per_mwh']
            revenue_df[f"{mp}_revenue"] = revenue_df[contribution_col] * fixed_price
        elif price_model == 'market':
            revenue_df[f"{mp}_revenue"] = revenue_df[contribution_col] * revenue_df['market_index_price']
    output_df = revenue_df[['delivery_start', 'mp_1_revenue', 'mp_2_revenue', 'mp_3_revenue', 'mp_4_revenue']]
    output_file = "asset_revenue.csv"
    output_df.to_csv(output_file, index=False, sep=",")
    print(f"Asset revenue saved to {output_file}")

# Function to calculate invoices for each asset
def calculate_invoices(assets_df, trade_allocation_df, asset_revenue_df, market_index_df):
    required_cols = ['mp_1_revenue', 'mp_2_revenue', 'mp_3_revenue', 'mp_4_revenue']
    missing_cols = [col for col in required_cols if col not in asset_revenue_df.columns]
    if missing_cols:
        print(f"Error: Missing columns in asset_revenue_df: {missing_cols}")
        return

    meter_to_asset = {'mp_1': 'a_1', 'mp_2': 'a_2', 'mp_3': 'a_3', 'mp_4': 'a_4'}
    total_revenue = {
        'a_1': asset_revenue_df['mp_1_revenue'].sum(),
        'a_2': asset_revenue_df['mp_2_revenue'].sum(),
        'a_3': asset_revenue_df['mp_3_revenue'].sum(),
        'a_4': asset_revenue_df['mp_4_revenue'].sum()
    }
    total_contribution = {
        'a_1': trade_allocation_df['mp_1_contribution'].sum(),
        'a_2': trade_allocation_df['mp_2_contribution'].sum(),
        'a_3': trade_allocation_df['mp_3_contribution'].sum(),
        'a_4': trade_allocation_df['mp_4_contribution'].sum()
    }
    avg_market_price = market_index_df['market_index_price'].mean()
    invoice_df = pd.DataFrame(columns=['asset_id', 'net_revenue', 'unit_net_revenue', 'gross_revenue'])
    invoice_df['asset_id'] = ['a_1', 'a_2', 'a_3', 'a_4']
    for index, row in invoice_df.iterrows():
        asset_id = row['asset_id']
        asset = assets_df[assets_df['asset_id'] == asset_id].iloc[0]
        fee_model = asset['fee_model']
        if fee_model == 'fixed_as_produced':
            fee = total_contribution[asset_id] * asset['fee__eur_per_mwh']
        elif fee_model == 'fixed_for_capacity':
            fee = (asset['capacity__kw'] / 1000) * asset['fee__eur_per_mwh']
        elif fee_model == 'percent_of_market':
            fee = total_contribution[asset_id] * avg_market_price * (asset['fee_percent'] / 100)
        net_revenue = total_revenue[asset_id] + fee
        unit_net_revenue = net_revenue / (asset['capacity__kw'] / 1000)
        gross_revenue = net_revenue * 1.19
        invoice_df.at[index, 'net_revenue'] = net_revenue
        invoice_df.at[index, 'unit_net_revenue'] = unit_net_revenue
        invoice_df.at[index, 'gross_revenue'] = gross_revenue
    output_file = "asset_invoices.csv"
    invoice_df.to_csv(output_file, index=False, sep=",")
    print(f"Asset invoices saved to {output_file}")

# Function to calculate imbalance penalties
def calculate_imbalance_penalty(measured_df, forecast_a1_df, forecast_a2_df, forecast_a3_df, forecast_a4_df, imbalance_penalty_df):
    # Ensure datetime columns are consistent
    measured_df['delivery_start'] = pd.to_datetime(measured_df['delivery_start'])
    imbalance_penalty_df['delivery_start'] = pd.to_datetime(imbalance_penalty_df['delivery_start'])

    # Merge measured data with imbalance penalties
    imbalance_df = pd.merge(measured_df, imbalance_penalty_df, on='delivery_start', how='left')

    # Merge forecast data for each asset
    forecast_dfs = {
        'mp_1': forecast_a1_df,
        'mp_2': forecast_a2_df,
        'mp_3': forecast_a3_df,
        'mp_4': forecast_a4_df
    }
    for mp, forecast_df in forecast_dfs.items():
        forecast_df = forecast_df.rename(columns={'forecast': f'{mp}_forecast'})
        imbalance_df = pd.merge(imbalance_df, forecast_df[['delivery_start', f'{mp}_forecast']], 
                              on='delivery_start', how='left')

    # Calculate imbalance volume (measured - forecast) for each asset
    imbalance_df['a_1_imbalance'] = imbalance_df['mp_1'] - imbalance_df['mp_1_forecast']
    imbalance_df['a_2_imbalance'] = imbalance_df['mp_2'] - imbalance_df['mp_2_forecast']
    imbalance_df['a_3_imbalance'] = imbalance_df['mp_3'] - imbalance_df['mp_3_forecast']
    imbalance_df['a_4_imbalance'] = imbalance_df['mp_4'] - imbalance_df['mp_4_forecast']

    # Calculate imbalance penalty for each asset
    imbalance_df['a_1_penalty'] = imbalance_df['a_1_imbalance'] * imbalance_df['imbalance_penalty']
    imbalance_df['a_2_penalty'] = imbalance_df['a_2_imbalance'] * imbalance_df['imbalance_penalty']
    imbalance_df['a_3_penalty'] = imbalance_df['a_3_imbalance'] * imbalance_df['imbalance_penalty']
    imbalance_df['a_4_penalty'] = imbalance_df['a_4_imbalance'] * imbalance_df['imbalance_penalty']

    # Calculate total imbalance penalty per timestep
    imbalance_df['total_penalty'] = (imbalance_df['a_1_penalty'] + 
                                    imbalance_df['a_2_penalty'] + 
                                    imbalance_df['a_3_penalty'] + 
                                    imbalance_df['a_4_penalty'])

    # Select relevant columns for output
    output_df = imbalance_df[['delivery_start', 'a_1_penalty', 'a_2_penalty', 'a_3_penalty', 'a_4_penalty', 'total_penalty']]

    # Save to CSV
    output_file = "imbalance_penalties.csv"
    output_df.to_csv(output_file, index=False, sep=",")
    print(f"Imbalance penalties saved to {output_file}")

if __name__ == "__main__":
    main()