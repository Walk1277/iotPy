# main.py
import sys
import os

# Add project root to Python path (Raspberry Pi compatibility)
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import typer
from driver_monitor.driver_monitor import DriverMonitor

app = typer.Typer()

@app.command()
def start(index: int = typer.Option(0, help="Camera index")):
    monitor = DriverMonitor(cam_index=index)
    monitor.run()

if __name__ == "__main__":
    app()
