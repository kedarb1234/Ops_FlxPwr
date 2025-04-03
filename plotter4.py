import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# Function to load CSV file into a DataFrame
def load_csv_to_dataframe(file_path, delimiter=","):
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

# Function to create and save the revenue line plot for a specific asset
def plot_asset_revenues(asset_revenue_df, selected_asset):
    asset_revenue_df['delivery_start'] = pd.to_datetime(asset_revenue_df['delivery_start'])
    plt.figure(figsize=(12, 6))
    
    # Map asset to its revenue column
    asset_map = {'a_1': 'mp_1_revenue', 'a_2': 'mp_2_revenue', 'a_3': 'mp_3_revenue', 'a_4': 'mp_4_revenue'}
    revenue_col = asset_map[selected_asset]
    
    # Plot only the selected asset's revenue
    plt.plot(asset_revenue_df['delivery_start'], asset_revenue_df[revenue_col], 
             label=f'Asset {selected_asset}', marker='o')
    
    plt.title(f'Revenue for Asset {selected_asset} Over Time', fontsize=14, fontweight='bold')
    plt.xlabel('Time (HH:MM)', fontsize=12)
    plt.ylabel('Revenue (€)', fontsize=12)
    plt.legend(title='Asset', loc='best')
    plt.grid(True, linestyle='--', alpha=0.7)
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b %H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    output_folder = "Output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created folder: {output_folder}")
    
    output_file = os.path.join(output_folder, f"asset_revenue_plot_{selected_asset}.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Revenue plot for {selected_asset} saved to {output_file}")
    plt.close()

# Function to create and save the imbalance penalty line plot for a specific asset
def plot_imbalance_penalties(imbalance_penalty_df, selected_asset):
    imbalance_penalty_df['delivery_start'] = pd.to_datetime(imbalance_penalty_df['delivery_start'])
    plt.figure(figsize=(12, 6))
    
    # Map asset to its penalty column
    asset_map = {'a_1': 'a_1_penalty', 'a_2': 'a_2_penalty', 'a_3': 'a_3_penalty', 'a_4': 'a_4_penalty'}
    penalty_col = asset_map[selected_asset]
    
    # Plot only the selected asset's penalty
    plt.plot(imbalance_penalty_df['delivery_start'], imbalance_penalty_df[penalty_col], 
             label=f'Asset {selected_asset}', marker='o')
    
    plt.title(f'Imbalance Penalty for Asset {selected_asset} Over Time', fontsize=14, fontweight='bold')
    plt.xlabel('Time (HH:MM)', fontsize=12)
    plt.ylabel('Imbalance Penalty (€)', fontsize=12)
    plt.legend(title='Asset', loc='best')
    plt.grid(True, linestyle='--', alpha=0.7)
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b %H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    output_folder = "Output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created folder: {output_folder}")
    
    output_file = os.path.join(output_folder, f"imbalance_penalty_plot_{selected_asset}.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Imbalance penalty plot for {selected_asset} saved to {output_file}")
    plt.close()

# Function to create and save the revenue breakdown bar and point plot for a specific asset
def plot_revenue_breakdown(asset_invoices_df, selected_asset):
    # Filter DataFrame for the selected asset
    asset_data = asset_invoices_df[asset_invoices_df['asset_id'] == selected_asset]
    if asset_data.empty:
        print(f"No data found for asset {selected_asset}. Skipping revenue breakdown plot.")
        return
    
    plt.figure(figsize=(6, 6))  # Smaller figure size since it's one asset
    
    # Bar position (single bar)
    x = [0]
    
    # Plot gross revenue bar
    gross_bar = plt.bar(x, asset_data['gross_revenue'], color='lightblue', 
                        label='Gross Revenue (incl. VAT)', width=0.5)
    
    # Plot net revenue bar on top
    plt.bar(x, asset_data['net_revenue'], color='skyblue', label='Net Revenue', width=0.5)
    
    # Plot unit net revenue as a point
    plt.scatter(x, asset_data['gross_revenue'], color='red', 
                label='Unit Net Revenue (€/MW)', zorder=5, s=100)
    
    # Add text labels for gross revenue and unit net revenue
    for i, bar in enumerate(gross_bar):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2 + 0.1, height, 
                 f'{asset_data["gross_revenue"].iloc[i]:.2f} €',
                 ha='center', va='bottom', color='lightblue', fontsize=10, fontweight='bold')
        plt.text(bar.get_x() + bar.get_width() / 2 + 0.2, height, 
                 f'{asset_data["unit_net_revenue"].iloc[i]:.2f} €/MW',
                 ha='left', va='bottom', color='red', fontsize=10, fontweight='bold')
    
    plt.title(f'Revenue Breakdown for Asset {selected_asset}', fontsize=14, fontweight='bold')
    plt.xlabel('Asset', fontsize=12)
    plt.ylabel('Revenue (€)', fontsize=12)
    plt.xticks(x, [selected_asset], fontsize=10)
    plt.legend(loc='best')
    plt.grid(True, linestyle='--', alpha=0.7, axis='y')
    
    # Adjust y-axis limit
    plt.ylim(0, max(asset_data['gross_revenue']) * 1.2)
    
    plt.tight_layout()
    
    output_folder = "Output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created folder: {output_folder}")
    
    output_file = os.path.join(output_folder, f"revenue_breakdown_plot_{selected_asset}.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Revenue breakdown plot for {selected_asset} saved to {output_file}")
    plt.close()

# Function to get user input for asset selection
def get_user_asset_choice():
    valid_assets = ['a_1', 'a_2', 'a_3', 'a_4']
    print("What asset do you want to see the results for?")
    print("Options: a_1, a_2, a_3, a_4")
    
    while True:
        choice = input("Enter your choice (e.g., a_1): ").strip().lower()
        if choice in valid_assets:
            return choice
        else:
            print("Invalid choice. Please enter one of: a_1, a_2, a_3, a_4")

# Main execution
if __name__ == "__main__":
    # Get user input for asset selection
    selected_asset = get_user_asset_choice()

    # Load the data
    asset_revenue_df = load_csv_to_dataframe("asset_revenue.csv", delimiter=",")
    imbalance_penalty_df = load_csv_to_dataframe("imbalance_penalties.csv", delimiter=",")
    asset_invoices_df = load_csv_to_dataframe("asset_invoices.csv", delimiter=",")

    # Plot revenue if data loaded successfully
    if asset_revenue_df is not None:
        plot_asset_revenues(asset_revenue_df, selected_asset)
    else:
        print(f"Failed to load asset_revenue.csv. Revenue plotting for {selected_asset} aborted.")

    # Plot imbalance penalties if data loaded successfully
    if imbalance_penalty_df is not None:
        plot_imbalance_penalties(imbalance_penalty_df, selected_asset)
    else:
        print(f"Failed to load imbalance_penalties.csv. Imbalance penalty plotting for {selected_asset} aborted.")

    # Plot revenue breakdown if data loaded successfully
    if asset_invoices_df is not None:
        plot_revenue_breakdown(asset_invoices_df, selected_asset)
    else:
        print(f"Failed to load asset_invoices.csv. Revenue breakdown plotting for {selected_asset} aborted.")