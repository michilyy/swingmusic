from swingmusic.settings import TCOLOR, Info, Paths
from swingmusic.utils.network import get_ip


def log_startup_info(host: str, port: int):
    print(f"{TCOLOR.HEADER}Swing Music v{Info.SWINGMUSIC_APP_VERSION} {TCOLOR.ENDC}")

    addresses = [host]

    if host == "0.0.0.0":
        remote_ip = get_ip()
        addresses.extend(["127.0.0.1"] + ([remote_ip] if remote_ip else []))

    print("Server running on:\n")
    for address in addresses:
        print(
            f"{TCOLOR.OKGREEN}http://{address}:{port}{TCOLOR.ENDC}"
        )

    print(f"\n{TCOLOR.YELLOW}Data folder: {Paths().app_dir}{TCOLOR.ENDC}\n")
