import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QPushButton, QLabel, QComboBox, QFileDialog, 
                             QHBoxLayout, QLineEdit, QMessageBox, QSlider, QScrollArea)
from PyQt5.QtCore import Qt

class DataPlotterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Plotter")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.label = QLabel("Choose a CSV file to start:")
        self.layout.addWidget(self.label)

        self.file_button = QPushButton("Choose File")
        self.file_button.clicked.connect(self.choose_file)
        self.layout.addWidget(self.file_button)

        self.x_menu = QComboBox()
        self.x_menu.currentIndexChanged.connect(self.update_label_menu)
        self.layout.addWidget(self.x_menu)

        self.label_menu = QComboBox()
        self.label_menu.currentIndexChanged.connect(self.update_slider_range)
        self.layout.addWidget(self.label_menu)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.valueChanged.connect(self.update_slider)
        self.layout.addWidget(self.slider)

        self.range_layout = QHBoxLayout()
        self.start_label = QLabel("Start:")
        self.start_input = QLineEdit()
        self.start_input.setText("0")
        self.length_label = QLabel("Length:")
        self.length_input = QLineEdit()
        self.length_input.setText("100")
        self.end_label = QLabel("End:")
        self.end_input = QLineEdit()
        self.end_input.setText("100")
        self.range_layout.addWidget(self.start_label)
        self.range_layout.addWidget(self.start_input)
        self.range_layout.addWidget(self.length_label)
        self.range_layout.addWidget(self.length_input)
        self.range_layout.addWidget(self.end_label)
        self.range_layout.addWidget(self.end_input)
        self.layout.addLayout(self.range_layout)

        self.plot_button = QPushButton("Plot Data")
        self.plot_button.clicked.connect(self.plot_data)
        self.layout.addWidget(self.plot_button)

        self.mode_button = QPushButton("Switch Plot Mode")
        self.mode_button.clicked.connect(self.switch_mode)
        self.layout.addWidget(self.mode_button)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        self.canvas = FigureCanvas(plt.figure(figsize=(12, 8)))
        self.scroll_layout.addWidget(self.canvas)

        self.file_path = ""
        self.data = None
        self.labels = []
        self.headers = []
        self.start_val = 0
        self.length = 100
        self.plot_mode = 0  # 0 for combined, 1 for separate

    def choose_file(self):
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if self.file_path:
            self.data = pd.read_csv(self.file_path)
            self.headers = [col for col in self.data.columns if col != 'label']
            self.x_menu.clear()
            self.x_menu.addItems(self.headers)

    def update_label_menu(self):
        if self.data is not None:
            x_header = self.x_menu.currentText()
            self.labels = self.data['label'].unique().astype(str)
            self.label_menu.clear()
            self.label_menu.addItems(self.labels)
            self.update_slider_range()

    def update_slider_range(self):
        if self.data is not None:
            label = self.label_menu.currentText()
            x_header = self.x_menu.currentText()
            subset = self.data[self.data['label'] == label]
            if not subset.empty:
                min_val = subset[x_header].min()
                max_val = subset[x_header].max()
                self.slider.setRange(int(min_val), int(max_val - self.length))
                self.slider.setValue(int(min_val))
                self.start_input.setText(str(min_val))
                self.length = min(100, max_val - min_val)  # default length
                self.length_input.setText(str(self.length))
                self.end_input.setText(str(min_val + self.length))

    def update_slider(self):
        self.start_val = self.slider.value()
        try:
            self.length = int(self.length_input.text())
        except ValueError:
            self.length = 100
        x_header = self.x_menu.currentText()
        max_end_val = self.data[self.data['label'] == self.label_menu.currentText()][x_header].max()
        self.start_val = max(self.data[x_header].min(), min(self.start_val, max_end_val - self.length))
        self.start_input.setText(str(self.start_val))
        self.end_input.setText(str(self.start_val + self.length))
        self.plot_data()

    def switch_mode(self):
        self.plot_mode = 1 - self.plot_mode  # Toggle between 0 and 1
        self.plot_data()

    def plot_data(self):
        label = self.label_menu.currentText()
        x_header = self.x_menu.currentText()
        if self.data is not None and label and x_header:
            try:
                self.start_val = float(self.start_input.text())
                self.length = int(self.length_input.text())
                self.end_val = self.start_val + self.length

                subset = self.data[(self.data['label'] == label) & 
                                   (self.data[x_header] >= self.start_val) & 
                                   (self.data[x_header] < self.end_val)]
                
                if self.plot_mode == 0:
                    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10))

                    ax1.plot(subset[x_header], subset['accel_x'], label='Accel X')
                    ax1.plot(subset[x_header], subset['accel_y'], label='Accel Y')
                    ax1.plot(subset[x_header], subset['accel_z'], label='Accel Z')
                    ax1.set_title(f'Acceleration Data for Label {label}')
                    ax1.set_xlabel(x_header)
                    ax1.set_ylabel('Acceleration')
                    ax1.legend()

                    ax2.plot(subset[x_header], subset['gyr_x'], label='Gyro X')
                    ax2.plot(subset[x_header], subset['gyr_y'], label='Gyro Y')
                    ax2.plot(subset[x_header], subset['gyr_z'], label='Gyro Z')
                    ax2.set_title(f'Gyrometer Data for Label {label}')
                    ax2.set_xlabel(x_header)
                    ax2.set_ylabel('Gyrometer')
                    ax2.legend()

                else:
                    fig, axes = plt.subplots(3, 2, figsize=(16, 12))
                    axes = axes.flatten()

                    axes[0].plot(subset[x_header], subset['accel_x'], label='Accel X')
                    axes[0].set_title(f'Accel X for Label {label}')
                    axes[0].set_xlabel(x_header)
                    axes[0].set_ylabel('Accel X')

                    axes[1].plot(subset[x_header], subset['accel_y'], label='Accel Y')
                    axes[1].set_title(f'Accel Y for Label {label}')
                    axes[1].set_xlabel(x_header)
                    axes[1].set_ylabel('Accel Y')

                    axes[2].plot(subset[x_header], subset['accel_z'], label='Accel Z')
                    axes[2].set_title(f'Accel Z for Label {label}')
                    axes[2].set_xlabel(x_header)
                    axes[2].set_ylabel('Accel Z')

                    axes[3].plot(subset[x_header], subset['gyr_x'], label='Gyro X')
                    axes[3].set_title(f'Gyro X for Label {label}')
                    axes[3].set_xlabel(x_header)
                    axes[3].set_ylabel('Gyro X')

                    axes[4].plot(subset[x_header], subset['gyr_y'], label='Gyro Y')
                    axes[4].set_title(f'Gyro Y for Label {label}')
                    axes[4].set_xlabel(x_header)
                    axes[4].set_ylabel('Gyro Y')

                    axes[5].plot(subset[x_header], subset['gyr_z'], label='Gyro Z')
                    axes[5].set_title(f'Gyro Z for Label {label}')
                    axes[5].set_xlabel(x_header)
                    axes[5].set_ylabel('Gyro Z')

                    fig.tight_layout()

                self.canvas.figure = fig
                self.canvas.draw()
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Please enter valid start and end values.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = DataPlotterApp()
    main_win.show()
    sys.exit(app.exec_())
