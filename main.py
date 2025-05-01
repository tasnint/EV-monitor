import sys
import random
import time
import csv
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import pyqtgraph as pg  # For live graph plotting


# ─────────────────────────────────────────────
# THREAD CLASS TO SIMULATE EV DATA IN BACKGROUND
# ─────────────────────────────────────────────

class DataGenerator(QThread):
    # Signal to send simulated SoC, Temp, SoH to the GUI
    data_updated = pyqtSignal(float, float, float)

    def run(self):
        # Initialize values
        soc, temp, soh = 80.0, 25.0, 95.0
        while True:
            # Simulate realistic changes in values
            soc += random.uniform(-0.5, 0.5)
            temp += random.uniform(-0.2, 0.1)
            soh += random.uniform(-0.01, 0.1)

            # Clamp values within acceptable ranges
            soc = max(0, min(soc, 100))
            temp = max(15, min(temp, 60))
            soh = max(20, min(soh, 100))

            # Emit updated values to the GUI
            self.data_updated.emit(soc, temp, soh)
            time.sleep(1)  # Update every second


# ─────────────────────────────────────────────
# MAIN GUI CLASS FOR EV MONITOR APP
# ─────────────────────────────────────────────

class EVMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EV Battery Monitor")
        self.setGeometry(100, 100, 800, 600)

        # Central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Labels for displaying values
        self.soc_label = QLabel("State of Charge (SoC): 0.0%")
        self.temp_label = QLabel("Temperature: 0.0 °C")
        self.soh_label = QLabel("State of Health (SoH): 0.0%")

        # Plotting widget for temperature
        self.plot_widget = pg.PlotWidget(title="Battery Temperature Over Time")
        self.plot_widget.setYRange(15, 60)  # Y-axis bounds for temp
        self.plot_data = self.plot_widget.plot(pen='y')  # Yellow line
        self.temp_data = []  # Y-values for plot
        self.time_data = []  # X-values (time)

        # Buttons for control
        self.start_button = QPushButton("Start Simulation")
        self.stop_button = QPushButton("Stop Simulation")
        self.reset_button = QPushButton("Reset Graph")
        self.save_button = QPushButton("Save Data to CSV")
        self.load_button = QPushButton("Load Data from CSV")

        # Connect buttons to their actions
        self.start_button.clicked.connect(self.start_simulation)
        self.stop_button.clicked.connect(self.stop_simulation)
        self.reset_button.clicked.connect(self.reset_simulation)
        self.save_button.clicked.connect(self.save_data_to_file)
        self.load_button.clicked.connect(self.load_data_from_file)

        # Add all widgets to layout
        self.layout.addWidget(self.soc_label)
        self.layout.addWidget(self.temp_label)
        self.layout.addWidget(self.soh_label)
        self.layout.addWidget(self.plot_widget)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)
        self.layout.addWidget(self.reset_button)
        self.layout.addWidget(self.save_button)
        self.layout.addWidget(self.load_button)

        # Variables to track state
        self.start_time = None
        self.logged_data = []  # Store all data points for saving

    # ─────────────────────────────────────────
    # Update GUI when new data is emitted from thread
    # ─────────────────────────────────────────
    def update_labels(self, soc, temp, soh):
        self.soc_label.setText(f"State of Charge (SoC): {soc:.1f}%")
        self.temp_label.setText(f"Temperature: {temp:.1f} °C")
        self.soh_label.setText(f"State of Health (SoH): {soh:.1f}%")

        # Track elapsed time since start
        if self.start_time is None:
            self.start_time = time.time()
        current_time = time.time() - self.start_time

        # Update plot data
        self.time_data.append(current_time)
        self.temp_data.append(temp)

        # Store for file saving
        self.logged_data.append((current_time, soc, temp, soh))

        # Limit graph to 60 points
        if len(self.time_data) > 60:
            self.time_data.pop(0)
            self.temp_data.pop(0)

        # Update graph
        self.plot_data.setData(self.time_data, self.temp_data)

    # ─────────────────────────────────────────
    # Start simulation (launch thread)
    # ─────────────────────────────────────────
    def start_simulation(self):
        if not hasattr(self, 'data_generator') or not self.data_generator.isRunning():
            self.data_generator = DataGenerator()
            self.data_generator.data_updated.connect(self.update_labels)
            self.data_generator.start()

    # ─────────────────────────────────────────
    # Stop simulation (terminate thread)
    # ─────────────────────────────────────────
    def stop_simulation(self):
        if hasattr(self, 'data_generator') and self.data_generator.isRunning():
            self.data_generator.terminate()
            QMessageBox.information(self, "Stopped", "Simulation stopped.")

    # ─────────────────────────────────────────
    # Reset graph and all data
    # ─────────────────────────────────────────
    def reset_simulation(self):
        self.time_data.clear()
        self.temp_data.clear()
        self.logged_data.clear()
        self.plot_data.clear()
        self.start_time = None
        QMessageBox.information(self, "Reset", "Graph and data reset.")

    # ─────────────────────────────────────────
    # Save data to CSV file
    # ─────────────────────────────────────────
    def save_data_to_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if file_name:
            with open(file_name, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Time', 'SoC', 'Temperature', 'SoH'])  # Column headers
                writer.writerows(self.logged_data)  # Write all logged data
            QMessageBox.information(self, "Saved", f"Data saved to {file_name}")

    # ─────────────────────────────────────────
    # Load data from CSV file and display on graph
    # ─────────────────────────────────────────
    def load_data_from_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if file_name:
            self.time_data.clear()
            self.temp_data.clear()
            self.logged_data.clear()
            with open(file_name, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.time_data.append(float(row['Time']))
                    self.temp_data.append(float(row['Temperature']))
                    self.logged_data.append((
                        float(row['Time']),
                        float(row['SoC']),
                        float(row['Temperature']),
                        float(row['SoH'])
                    ))
            self.plot_data.setData(self.time_data, self.temp_data)
            QMessageBox.information(self, "Loaded", f"Data loaded from {file_name}")


# ─────────────────────────────────────────────
# APPLICATION ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EVMonitor()
    window.show()
    sys.exit(app.exec())
