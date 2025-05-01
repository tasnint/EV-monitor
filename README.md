# EV Battery Monitor

A real-time desktop dashboard to simulate and visualize electric vehicle (EV) battery telemetry. Built with **PyQt6** and **pyqtgraph**, it displays and logs key battery metrics like:

- **State of Charge (SoC)**
- **Battery Temperature**
- **State of Health (SoH)**

This tool is perfect for visual demos, testing analytics workflows, or developing front-end interfaces for smart mobility systems.

### Demo Video:
[Click to watch demo](demo/demo.mp4)
![Video Thumbail]demo/thumbnail.png)


## Features:
- Real-time simulation of EV battery metrics  
- Live graph of temperature data using `pyqtgraph`  
- Save simulation data as `.csv`  
- Load and visualize historical data from CSV  
- Reset simulation and graph  
- Smooth UI with background threading (`QThread`) 
