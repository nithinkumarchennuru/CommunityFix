import logging
import pymysql
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

logger = logging.getLogger(__name__)

# Initialize Flask-SQLAlchemy extension
db = SQLAlchemy()


def test_database_connection(config_obj):
    """
    Test direct MySQL server connectivity and database availability
    using credentials provided in the configuration.
    
    Returns:
        dict: Diagnostic details including connection status, server version, and any errors.
    """
    host = config_obj.DB_HOST
    port = config_obj.DB_PORT
    user = config_obj.DB_USER
    password = config_obj.DB_PASSWORD
    db_name = config_obj.DB_NAME

    result = {
        "connected": False,
        "database_exists": False,
        "host": host,
        "port": port,
        "user": user,
        "database": db_name,
        "server_version": None,
        "message": "",
        "error": None
    }

    # Step 1: Attempt direct server-level connection using PyMySQL
    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset="utf8mb4",
            connect_timeout=3
        )
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version_row = cursor.fetchone()
            result["server_version"] = version_row[0] if version_row else "Unknown"

            # Check if target database exists
            cursor.execute("SHOW DATABASES LIKE %s", (db_name,))
            db_row = cursor.fetchone()
            if db_row:
                result["database_exists"] = True
            else:
                # Attempt to create database if permitted
                try:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                    conn.commit()
                    result["database_exists"] = True
                    logger.info(f"Database '{db_name}' automatically initialized.")
                except Exception as create_err:
                    logger.warning(f"Could not auto-create database '{db_name}': {create_err}")

        conn.close()
        result["connected"] = True
        result["message"] = (
            f"Successfully connected to MySQL server v{result['server_version']} "
            f"at {host}:{port}. Database '{db_name}' {'is ready' if result['database_exists'] else 'does not exist yet'}."
        )
        return result

    except pymysql.err.OperationalError as op_err:
        err_code, err_msg = op_err.args if len(op_err.args) >= 2 else (0, str(op_err))
        result["error"] = f"OperationalError [{err_code}]: {err_msg}"
        if err_code == 1045:
            result["message"] = f"Access denied for user '{user}'@'{host}'. Please verify DB_PASSWORD in backend/.env."
        elif err_code == 2003:
            result["message"] = f"Cannot connect to MySQL server at {host}:{port}. Ensure MySQL service is running."
        else:
            result["message"] = f"MySQL connection failed: {err_msg}"
        logger.error(result["message"])
        return result

    except Exception as exc:
        result["error"] = str(exc)
        result["message"] = f"Unexpected database connection error: {str(exc)}"
        logger.error(result["message"])
        return result


def verify_sqlalchemy_engine(app):
    """
    Execute a test query using the configured SQLAlchemy engine.
    """
    try:
        with app.app_context():
            with db.engine.connect() as connection:
                res = connection.execute(text("SELECT 1 AS alive"))
                row = res.fetchone()
                return row[0] == 1
    except Exception as e:
        logger.error(f"SQLAlchemy test query failed: {e}")
        return False
