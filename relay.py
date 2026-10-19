import socket
import threading

sessions = {}  # Stores active technician sessions { "code": socket }
lock = threading.Lock()

def bridge(s1, s2):
    """Pipes data back and forth between the Server (Technician) and Client (Customer)"""
    def forward(src, dst):
        try:
            while True:
                data = src.recv(4096)
                if not data:
                    break
                dst.sendall(data)
        except:
            pass
        finally:
            try: src.close()
            except: pass
            try: dst.close()
            except: pass

    t1 = threading.Thread(target=forward, args=(s1, s2), daemon=True)
    t2 = threading.Thread(target=forward, args=(s2, s1), daemon=True)
    t1.start()
    t2.start()

def handle_client(sock, addr):
    try:
        header = sock.recv(1024).decode('utf-8', errors='ignore').strip()
        if not header or ":" not in header:
            sock.close()
            return

        role, code = header.split(":", 1)

        if role == "SERVER":
            with lock:
                sessions[code] = sock
            print(f"[+] Technician registered session: {code}")
            while True:
                data = sock.recv(4096)
                if not data:
                    break

        elif role == "CLIENT":
            print(f"[+] Customer joining session: {code}")
            with lock:
                server_sock = sessions.pop(code, None)
            
            if not server_sock:
                sock.sendall(b"ERROR\n")
                sock.close()
                return

            sock.sendall(b"OK\n")
            print(f"[+] Bridge established for session: {code}")
            bridge(server_sock, sock)

    except Exception as e:
        print(f"[-] Error: {e}")
    finally:
        try: sock.close()
        except: pass

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", 9000))
    server.listen(5)
    print("[*] Free Cloud Relay Server running on port 9000...")
    
    while True:
        client_sock, addr = server.accept()
        threading.Thread(target=handle_client, args=(client_sock, addr), daemon=True).start()

if __name__ == "__main__":
    main()