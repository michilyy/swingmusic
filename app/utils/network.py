import socket as Socket


def has_connection(host="google.it", port=80, timeout=3):
    """
    # REVIEW Was:
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        Socket.setdefaulttimeout(timeout)
        Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM).connect((host, port))
        return True
    except Socket.error as ex:
        return False


def get_ip(server:str="8.8.8.8") -> str|None:
    """
    Returns the public IP address of this device.

    :param server: Server address for retrieving public IP address. Default: "8.8.8.8"
    :return: public IP if successful, None otherwise.
    """

    try:
        with Socket.socket(Socket.AF_INET, Socket.SOCK_DGRAM) as soc:
            soc.connect((server, 80))
            return str(soc.getsockname()[0])

    except OSError:
        return None

