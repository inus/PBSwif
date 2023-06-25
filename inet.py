import socket
from time import sleep

def up(host="8.8.8.8", port=53, timeout=5):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        #print(ex)
        return False

def test(delay):
    while True:
        print (up())
        sleep(delay if delay>1 else 3)

#test(2)        
