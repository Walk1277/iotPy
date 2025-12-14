# main.py
import sys
import os

# Add project root to Python path (Raspberry Pi compatibility)
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import typer
from driver_monitor.driver_monitor import DriverMonitor
import config

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context, index: int = typer.Option(None, help="Camera index (default: from config.py)")):
    """IoT Driver Monitoring System"""
    if ctx.invoked_subcommand is None:
        # If no subcommand, run the monitor
        # Use config CAMERA_INDEX if index not provided
        cam_index = index if index is not None else getattr(config, 'CAMERA_INDEX', 0)
        print(f"[Main] Using camera index: {cam_index}")
        try:
            monitor = DriverMonitor(cam_index=cam_index)
            monitor.run()
        except Exception as e:
            raise

@app.command()
def start(index: int = typer.Option(None, help="Camera index (default: from config.py)")):
    """Start the driver monitoring system"""
    # Use config CAMERA_INDEX if index not provided
    cam_index = index if index is not None else getattr(config, 'CAMERA_INDEX', 0)
    print(f"[Main] Using camera index: {cam_index}")
    try:
        monitor = DriverMonitor(cam_index=cam_index)
        monitor.run()
    except Exception as e:
        raise

if __name__ == "__main__":
    app()
