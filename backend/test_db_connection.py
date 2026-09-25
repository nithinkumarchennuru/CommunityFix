#!/usr/bin/env python
"""
CommunityFix - Initial Database Connection Test
Validates MySQL connectivity using configured environment variables.
"""

__test__ = False

import sys
import os
from app.config import Config
from app.database import test_database_connection


def main():
    print("=" * 65)
    print(" CommunityFix - Database Connection Diagnostic Tool")
    print("=" * 65)
    print(f"Target Host     : {Config.DB_HOST}")
    print(f"Target Port     : {Config.DB_PORT}")
    print(f"Target User     : {Config.DB_USER}")
    print(f"Password Set    : {'Yes (Length: ' + str(len(Config.DB_PASSWORD)) + ')' if Config.DB_PASSWORD else 'No (Empty)'}")
    print(f"Target Database : {Config.DB_NAME}")
    print("-" * 65)
    print("Testing connection to MySQL server...")

    result = test_database_connection(Config)

    if result["connected"]:
        print("\n [SUCCESS] MySQL Connection Test PASSED!")
        print(f"   Server Version  : {result.get('server_version', 'Unknown')}")
        print(f"   Database Status : {'Found/Ready' if result.get('database_exists') else 'Not Found'}")
        print(f"   Details         : {result['message']}")
        print("=" * 65)
        return 0
    else:
        print("\n [FAILED] MySQL Connection Test FAILED!")
        print(f"   Error Summary   : {result.get('error')}")
        print(f"   Explanation     : {result.get('message')}")
        print("\nTroubleshooting Tips:")
        print(" 1. Check if the MySQL service is running: Get-Service MySQL80")
        print(" 2. Verify your password in 'backend/.env' (DB_PASSWORD=<your_password>)")
        print(" 3. Verify user permissions for user 'root'@'127.0.0.1' or 'localhost'")
        print("=" * 65)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
