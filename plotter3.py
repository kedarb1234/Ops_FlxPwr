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

# Function to create and save the revenue line plot
def plot_asset_revenues(asset_revenue_df):
    asset_revenue_df['delivery_start'] = pd.to_datetime(asset_revenue_df['delivery_start'])
    plt.figure(figsize=(12, 6))
    plt.plot(asset_revenue_df['delivery_start'], asset_revenue_df['mp_1_revenue'], label='Asset a_1 (mp_1)', marker='o')
    plt.plot(asset_revenue_df['delivery_start'], asset_revenue_df['mp_2_revenue'], label='Asset a_2 (mp_2)', marker='o')
    plt.plot(asset_revenue_df['delivery_start'], asset_revenue_df['mp_3_revenue'], label='Asset a_3 (mp_3)', marker='o')
    plt.plot(asset_revenue_df['delivery_start'], asset_revenue_df['mp_4_revenue'], label='Asset a_4 (mp_4)', marker='o')
    plt.title('Revenue per Asset Over Time', fontsize=14, fontweight='bold')
    plt.xlabel('Time (HH:MM)', fontsize=12)
    plt.ylabel('Revenue (€)', fontsize=12)
    plt.legend(title='Assets', loc='best')
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
    output_file = os.path.join(output_folder, "asset_revenue_plot.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Revenue plot saved to {output_file}")
    plt.close()

# Function to create and save the imbalance penalty line plot
def plot_imbalance_penalties(imbalance_penalty_df):
    imbalance_penalty_df['delivery_start'] = pd.to_datetime(imbalance_penalty_df['delivery_start'])
    plt.figure(figsize=(12, 6))
    plt.plot(imbalance_penalty_df['delivery_start'], imbalance_penalty_df['a_1_penalty'], label='Asset a_1', marker='o')
    plt.plot(imbalance_penalty_df['delivery_start'], imbalance_penalty_df['a_2_penalty'], label='Asset a_2', marker='o')
    plt.plot(imbalance_penalty_df['delivery_start'], imbalance_penalty_df['a_3_penalty'], label='Asset a_3', marker='o')
    plt.plot(imbalance_penalty_df['delivery_start'], imbalance_penalty_df['a_4_penalty'], label='Asset a_4', marker='o')
    plt.title('Imbalance Penalty per Asset Over Time', fontsize=14, fontweight='bold')
    plt.xlabel('Time (HH:MM)', fontsize=12)
    plt.ylabel('Imbalance Penalty (€)', fontsize=12)
    plt.legend(title='Assets', loc='best')
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
    output_file = os.path.join(output_folder, "imbalance_penalty_plot.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Imbalance penalty plot saved to {output_file}")
    plt.close()

# Function to create and save the revenue breakdown bar and point plot
def plot_revenue_breakdown(asset_invoices_df):
    # Create the plot
    plt.figure(figsize=(10, 6))

    # Bar positions
    assets = asset_invoices_df['asset_id']
    x = range(len(assets))

    # Plot gross revenue bars (total height)
    gross_bars = plt.bar(x, asset_invoices_df['gross_revenue'], color='lightblue', label='Gross Revenue (incl. VAT)', width=0.5)

    # Plot net revenue bars on top (overwrites part of gross revenue)
    plt.bar(x, asset_invoices_df['net_revenue'], color='skyblue', label='Net Revenue', width=0.5)

    # Plot unit net revenue as points on top of bars
    plt.scatter(x, asset_invoices_df['gross_revenue'], color='red', label='Unit Net Revenue (€/MW)', zorder=5, s=100)

    # Add text labels for gross revenue and unit net revenue
    for i, bar in enumerate(gross_bars):
        height = bar.get_height()
        # Gross revenue label (in lightblue, slightly above the bar)
        plt.text(bar.get_x() + bar.get_width() / 2, height + 50, f'{asset_invoices_df["gross_revenue"].iloc[i]:.2f} €',
                 ha='center', va='bottom', color='lightblue', fontsize=10, fontweight='bold')
        # Unit net revenue label (in red, slightly higher and offset to the right)
        plt.text(bar.get_x() + bar.get_width() / 2, height + 100, f'{asset_invoices_df["unit_net_revenue"].iloc[i]:.2f} €/MW',
                 ha='left', va='bottom', color='red', fontsize=10, fontweight='bold')

    # Add title, labels, and legend
    plt.title('Revenue Breakdown per Asset', fontsize=14, fontweight='bold')
    plt.xlabel('Asset', fontsize=12)
    plt.ylabel('Revenue (€)', fontsize=12)
    plt.xticks(x, assets, fontsize=10)
    plt.legend(loc='best')
    plt.grid(True, linestyle='--', alpha=0.7, axis='y')

    # Adjust y-axis limit to accommodate text labels
    plt.ylim(0, max(asset_invoices_df['gross_revenue']) * 1.2)  # Add 20% headroom

    # Adjust layout
    plt.tight_layout()

    # Create Output folder if it doesn't exist
    output_folder = "Output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created folder: {output_folder}")

    # Save the plot as PNG
    output_file = os.path.join(output_folder, "revenue_breakdown_plot.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Revenue breakdown plot saved to {output_file}")

    # Close the plot to free memory
    plt.close()

# Main execution
if __name__ == "__main__":
    # Load the data
    asset_revenue_df = load_csv_to_dataframe("asset_revenue.csv", delimiter=",")
    imbalance_penalty_df = load_csv_to_dataframe("imbalance_penalties.csv", delimiter=",")
    asset_invoices_df = load_csv_to_dataframe("asset_invoices.csv", delimiter=",")

    # Plot revenue if data loaded successfully
    if asset_revenue_df is not None:
        plot_asset_revenues(asset_revenue_df)
    else:
        print("Failed to load asset_revenue.csv. Revenue plotting aborted.")

    # Plot imbalance penalties if data loaded successfully
    if imbalance_penalty_df is not None:
        plot_imbalance_penalties(imbalance_penalty_df)
    else:
        print("Failed to load imbalance_penalties.csv. Imbalance penalty plotting aborted.")

    # Plot revenue breakdown if data loaded successfully
    if asset_invoices_df is not None:
        plot_revenue_breakdown(asset_invoices_df)
    else:
        print("Failed to load asset_invoices.csv. Revenue breakdown plotting aborted.")