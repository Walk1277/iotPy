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

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context, index: int = typer.Option(0, help="Camera index")):
    """IoT Driver Monitoring System"""
    if ctx.invoked_subcommand is None:
        # If no subcommand, run the monitor
        monitor = DriverMonitor(cam_index=index)
        monitor.run()

@app.command()
def start(index: int = typer.Option(0, help="Camera index")):
    """Start the driver monitoring system"""
    monitor = DriverMonitor(cam_index=index)
    monitor.run()

if __name__ == "__main__":
    app()
