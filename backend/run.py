import os
from app import create_app
from app.config import Config

app = create_app(os.getenv("FLASK_ENV", "development"))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "127.0.0.1")
    debug = Config.DEBUG

    print("=" * 60)
    print("  Starting CommunityFix Flask Backend Server")
    print(f"  Host: http://{host}:{port}")
    print(f"  Health Check: http://{host}:{port}/api/health")
    print(f"  Debug Mode: {debug}")
    print("=" * 60)

    app.run(host=host, port=port, debug=debug)
