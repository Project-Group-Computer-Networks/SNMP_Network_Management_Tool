import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

# Function to plot CPU utilization over time
def plot_cpu_utilisation(df, device_ip):
    plt.figure(figsize=(10, 5))

    plt.plot(df['secs'], df['CPU 1 Utilisation'], label='CPU 1 Utilisation', marker='o')
    plt.plot(df['secs'], df['CPU 2 Utilisation'], label='CPU 2 Utilisation', marker='o')

    plt.title(f'CPU Utilisation Over Time for {device_ip}')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Utilisation (%)')
    plt.xticks(df['secs'][::4])
    plt.legend()
    plt.grid(True)

    # Show the line graph
    plt.tight_layout()
    plt.show()

# Function to plot pie chart for CPU utilization
def plot_avg_utilisation(df, cpu_no, device_ip):
    if cpu_no == 1:
        avg_cpu = df['CPU 1 Utilisation'].mean()
    else:
        avg_cpu = df['CPU 2 Utilisation'].mean()
        
    sizes = [avg_cpu, 100 - avg_cpu]
    colors = ['#66b3ff', '#cccccc']  # Color for the filled portion and the empty portion
    labels = ['Utilised', 'Unused']

    fig, ax = plt.subplots()
    ax.pie(sizes, colors=colors, startangle=90, labels=labels, 
           wedgeprops=dict(width=0.3, edgecolor='w'))

    centre_circle = plt.Circle((0, 0), 0.7, color='white', fc='white', linewidth=1.25)
    fig.gca().add_artist(centre_circle)

    plt.text(0, 0, f'{avg_cpu:.2f}%', horizontalalignment='center', 
             verticalalignment='center', fontsize=20, fontweight='bold')

    ax.set(aspect="equal")
    plt.title(f'Average CPU {cpu_no} Utilisation Percentage for {device_ip}')
    plt.show()

# Function to plot memory usage over time
def plot_memory_usage(df, device_ip):
    plt.figure(figsize=(10, 5))

    plt.plot(df['secs'], df['Memory used'] / (1024 * 1024), label='Memory usage', marker='o')

    plt.title(f'Memory Usage Over Time for {device_ip}')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Memory Used (GB)')
    plt.xticks(df['secs'][::4])
    plt.legend()
    plt.grid(True)

    # Show the line graph
    plt.tight_layout()
    plt.show()

# Function to process each CSV file
def process_device_file(file):
    # Extract the device IP from the filename
    device_ip = os.path.splitext(os.path.basename(file))[0].replace("device_info_", "")
    
    # Load the CSV data
    df = pd.read_csv(file)
    
    # Convert timestamp and add seconds column
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['secs'] = [(i * 5) for i in range(len(df))]

    # Plot the data for the current device
    plot_cpu_utilisation(df, device_ip)
    plot_avg_utilisation(df, 1, device_ip)
    plot_avg_utilisation(df, 2, device_ip)
    plot_memory_usage(df, device_ip)

# Find all CSV files with the format "device_info_{ipv4_addr}.csv"
csv_files = glob.glob('device_info_*.csv')

# Iterate over all matching files
for file in csv_files:
    process_device_file(file)
