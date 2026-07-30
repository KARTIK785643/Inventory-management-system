import os
from app import create_app
from app.seed import seed_database

app = create_app()

if __name__ == '__main__':
    db_file = os.path.join(os.path.dirname(__file__), 'inventory.db')
    if not os.path.exists(db_file):
        print("Database not found. Seeding initial data...")
        seed_database()

    print("Starting Flask Backend REST API on http://127.0.0.1:5000 ...")
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
