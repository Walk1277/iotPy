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
        # #region agent log
        import json
        try:
            with open('/home/mingyeongmin/문서/development/pythonproject/iotPy/iot_project_OOP/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"location":"main.py:19","message":"Before DriverMonitor creation","data":{"index":cam_index},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"E"}) + '\n')
        except: pass
        # #endregion
        try:
            monitor = DriverMonitor(cam_index=cam_index)
            # #region agent log
            try:
                with open('/home/mingyeongmin/문서/development/pythonproject/iotPy/iot_project_OOP/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"location":"main.py:25","message":"After DriverMonitor creation, before run","data":{},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"E"}) + '\n')
            except: pass
            # #endregion
            monitor.run()
        except Exception as e:
            # #region agent log
            try:
                with open('/home/mingyeongmin/문서/development/pythonproject/iotPy/iot_project_OOP/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"location":"main.py:30","message":"Main execution error","data":{"error_type":type(e).__name__,"error_msg":str(e)},"timestamp":int(__import__('time').time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"E"}) + '\n')
            except: pass
            # #endregion
            raise

@app.command()
def start(index: int = typer.Option(None, help="Camera index (default: from config.py)")):
    """Start the driver monitoring system"""
    cam_index = index if index is not None else getattr(config, 'CAMERA_INDEX', 0)
    print(f"[Main] Using camera index: {cam_index}")
    monitor = DriverMonitor(cam_index=cam_index)
    monitor.run()

if __name__ == "__main__":
    app()
