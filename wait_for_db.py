import os
import sys
import time
import socket

def wait_for_db():
    db_host = os.getenv('DB_HOST', 'db')
    db_port = int(os.getenv('DB_PORT', '3306'))
    
    start_time = time.time()
    timeout = 60  # 最多等待60秒
    
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((db_host, db_port))
                print("Database is available!")
                return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            time.sleep(1)
    
    print("Timeout: Database not available after 60 seconds.")
    return False

if __name__ == "__main__":
    if wait_for_db():
        sys.exit(0)
    else:
        sys.exit(1)