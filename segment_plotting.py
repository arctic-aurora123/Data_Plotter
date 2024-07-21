import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
file_path = 'IMU_motion_labeled.csv'
data = pd.read_csv(file_path)

# Get the unique labels and store them in an array of strings
labels = data['label'].unique().astype(str)

# Function to plot data for a specific label
def plot_data_by_label(data, label):
    subset = data[data['label'] == label]
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 1, 1)
    plt.plot(subset.index, subset['accel_x'], label='Accel X')
    plt.plot(subset.index, subset['accel_y'], label='Accel Y')
    plt.plot(subset.index, subset['accel_z'], label='Accel Z')
    plt.title(f'Acceleration Data for Label {label}')
    plt.xlabel('Index')
    plt.ylabel('Acceleration')
    plt.legend()
    
    plt.subplot(2, 1, 2)
    plt.plot(subset.index, subset['gyr_x'], label='Gyro X')
    plt.plot(subset.index, subset['gyr_y'], label='Gyro Y')
    plt.plot(subset.index, subset['gyr_z'], label='Gyro Z')
    plt.title(f'Gyrometer Data for Label {label}')
    plt.xlabel('Index')
    plt.ylabel('Gyrometer')
    plt.legend()
    
    plt.tight_layout()
    plt.show()

# Print the unique labels
print(f'Unique labels: {labels}')

# Plot data for each unique label
for label in labels:
    plot_data_by_label(data, label)
