import sys
import os
import time
import threading
import argparse

def launch_server():
    from app import create_app
    from app.seed import seed_database

    db_path = os.path.join(os.path.dirname(__file__), 'inventory.db')
    if not os.path.exists(db_path):
        print("[Launcher] Database missing. Seeding initial data...")
        seed_database()

    app = create_app()
    print("[Launcher] Starting Flask API Server on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

def launch_gui():
    print("[Launcher] Launching CustomTkinter Desktop Client...")
    from gui.app import InventoryApp
    app = InventoryApp()
    app.mainloop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Inventory & Stock Management System")
    parser.add_argument('--server-only', action='store_true', help="Run Flask REST API server only")
    parser.add_argument('--gui-only', action='store_true', help="Run CustomTkinter GUI client only")
    parser.add_argument('--seed', action='store_true', help="Seed database with sample data and exit")
    args = parser.parse_args()

    if args.seed:
        from app.seed import seed_database
        seed_database()
        sys.exit(0)

    if args.server_only:
        launch_server()
    elif args.gui_only:
        launch_gui()
    else:
        # Dual launch: start server in background thread, then start GUI
        server_thread = threading.Thread(target=launch_server, daemon=True)
        server_thread.start()
        
        # Give server 1 second to start
        time.sleep(1.5)
        
        # Start GUI in main thread
        launch_gui()
