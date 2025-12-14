# api_server.py
"""
Flask-based HTTP REST API server for real-time communication with JavaFX UI.
Replaces file-based communication to eliminate I/O blocking issues.
"""
import threading
import sys
import os
import time

# Add project root to Python path (Raspberry Pi compatibility)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("[API] Flask not available. Install with: pip3 install flask flask-cors")


class APIServer:
    """
    HTTP REST API server for real-time data communication.
    Runs in a background thread to avoid blocking the main loop.
    """
    
    def __init__(self, port=5000):
        if not FLASK_AVAILABLE:
            raise ImportError("Flask is not installed. Install with: pip3 install flask flask-cors")
        
        self.app = Flask(__name__)
        CORS(self.app)  # Allow JavaFX to access from localhost
        
        self.port = port
        self.server_thread = None
        self.running = False
        self.server_ready = False  # Flag to indicate server is ready
        self.server_ready_lock = threading.Lock()
        
        # Shared data (thread-safe with lock)
        self.drowsiness_data = {}
        self.status_data = {}
        self.log_summary_data = {}
        self.lock = threading.Lock()
        
        # UI request flags (for bidirectional communication)
        self.user_response_flag = False
        self.stop_speaker_flag = False
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes for API endpoints."""
        
        @self.app.route('/api/drowsiness', methods=['GET'])
        def get_drowsiness():
            """Get current drowsiness status."""
            with self.lock:
                return jsonify(self.drowsiness_data if self.drowsiness_data else {})
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """Get current system status."""
            with self.lock:
                return jsonify(self.status_data if self.status_data else {})
        
        @self.app.route('/api/log_summary', methods=['GET'])
        def get_log_summary():
            """Get log summary statistics."""
            with self.lock:
                return jsonify(self.log_summary_data if self.log_summary_data else {})
        
        @self.app.route('/api/user_response', methods=['POST'])
        def post_user_response():
            """Handle user response from UI (touch screen)."""
            with self.lock:
                self.user_response_flag = True
            return jsonify({"status": "ok", "message": "User response received"})
        
        @self.app.route('/api/stop_speaker', methods=['POST'])
        def post_stop_speaker():
            """Handle stop speaker request from UI."""
            with self.lock:
                self.stop_speaker_flag = True
            return jsonify({"status": "ok", "message": "Stop speaker request received"})
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint."""
            return jsonify({"status": "ok", "service": "IoT Driver Monitor API"})
    
    def start(self, wait_for_ready=True, max_wait_time=5.0):
        """
        Start Flask server in background thread.
        
        Args:
            wait_for_ready: If True, wait for server to be ready before returning
            max_wait_time: Maximum time to wait for server to be ready (seconds)
        """
        if self.running:
            return
        
        self.running = True
        self.server_ready = False
        self.server_thread = threading.Thread(
            target=self._run_server,
            daemon=True,
            name="APIServer"
        )
        self.server_thread.start()
        print(f"[API] Starting server on http://localhost:{self.port}...")
        
        # Wait for server to be ready
        if wait_for_ready:
            start_time = time.time()
            while not self.server_ready and (time.time() - start_time) < max_wait_time:
                time.sleep(0.1)
            
            if self.server_ready:
                print(f"[API] Server ready on http://localhost:{self.port}")
                print(f"[API] Endpoints: /api/drowsiness, /api/status, /api/log_summary")
            else:
                print(f"[API] Warning: Server may not be ready yet (waited {max_wait_time}s)")
        else:
            print(f"[API] Server starting in background (endpoints: /api/drowsiness, /api/status, /api/log_summary)")
    
    def _run_server(self):
        """Run Flask server (called in background thread)."""
        try:
            # Mark server as ready after a short delay (allows Flask to initialize)
            def mark_ready():
                time.sleep(0.5)  # Give Flask time to start
                with self.server_ready_lock:
                    self.server_ready = True
            
            ready_thread = threading.Thread(target=mark_ready, daemon=True)
            ready_thread.start()
            
            self.app.run(
                host='0.0.0.0',  # Allow access from localhost
                port=self.port,
                debug=False,
                use_reloader=False,
                threaded=True  # Handle multiple requests concurrently
            )
        except Exception as e:
            print(f"[API] Server error: {e}")
            self.running = False
            with self.server_ready_lock:
                self.server_ready = False
    
    def is_ready(self):
        """Check if server is ready to accept requests."""
        with self.server_ready_lock:
            return self.server_ready
    
    def stop(self):
        """Stop the API server."""
        self.running = False
        # Flask doesn't have a clean shutdown, but daemon thread will exit with main process
    
    def update_drowsiness(self, data):
        """Update drowsiness data (thread-safe)."""
        with self.lock:
            self.drowsiness_data = data
    
    def update_status(self, data):
        """Update system status data (thread-safe)."""
        with self.lock:
            self.status_data = data
    
    def update_log_summary(self, data):
        """Update log summary data (thread-safe)."""
        with self.lock:
            self.log_summary_data = data
    
    def check_user_response(self):
        """Check if user responded via UI (thread-safe, resets flag)."""
        with self.lock:
            if self.user_response_flag:
                self.user_response_flag = False
                return True
            return False
    
    def check_stop_speaker(self):
        """Check if stop speaker was requested (thread-safe, resets flag)."""
        with self.lock:
            if self.stop_speaker_flag:
                self.stop_speaker_flag = False
                return True
            return False

