# main.py
import typer
from driver_monitor import DriverMonitor

app = typer.Typer()

@app.command()
def start(index: int = typer.Option(0, help="Camera index")):
    monitor = DriverMonitor(cam_index=index)
    monitor.run()

if __name__ == "__main__":
    app()

