import pandas as pd
import matplotlib.pyplot as plt
df=pd.read_csv('device_info.csv')
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df['secs'] = [(i * 5) for i in range(len(df))]


plt.figure(figsize=(10, 5))

plt.plot(df['secs'], df['CPU 1 Utilisation'], label='CPU 1 Utilisation', marker='o')
plt.plot(df['secs'], df['CPU 2 Utilisation'], label='CPU 2 Utilisation', marker='o')

plt.title('CPU Utilisation Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('Utilisation (%)')
plt.xticks(df['secs'][::4])
# plt.xticks(rotation=90)
plt.legend()
plt.grid(True)

# Show the line graph
plt.tight_layout()
plt.show()

def plot_utilisation(cpu_no):
    if(cpu_no==1):
        avg_cpu=df['CPU 1 Utilisation'].mean()
    else:
        avg_cpu=df['CPU 2 Utilisation'].mean()
    sizes=[avg_cpu,100-avg_cpu]
    colors = ['#66b3ff', '#cccccc']  # Color for the filled portion and the empty portion
    labels = ['Utilised', 'Unused']
    fig, ax = plt.subplots()
    ax.pie(sizes, colors=colors, startangle=90, labels=labels, wedgeprops=dict(width=0.3, edgecolor='w'),)
    centre_circle = plt.Circle((0, 0), 0.7, color='white', fc='white', linewidth=1.25)
    fig.gca().add_artist(centre_circle)
    plt.text(0, 0, f'{avg_cpu:.2f}%', horizontalalignment='center', verticalalignment='center', fontsize=20, fontweight='bold')
    ax.set(aspect="equal")
    plt.title('Average CPU '+str(cpu_no) +' Utilisation Percentage')
    plt.show()

plot_utilisation(1)
plot_utilisation(2)

plt.figure(figsize=(10, 5))

plt.plot(df['secs'], df['Memory used']/(1024*1024), label='Memory usage', marker='o')

plt.title('Memory usage Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('Memory used(in GB)')
plt.xticks(df['secs'][::4])
# plt.xticks(rotation=90)
plt.legend()
plt.grid(True)

# Show the line graph
plt.tight_layout()
plt.show()