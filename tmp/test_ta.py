from typing import Optional
import socket
from urllib3.connection import HTTPConnection

import requests


def get_html_content(url: str) -> Optional[str]:
    HTTPConnection.default_socket_options = HTTPConnection.default_socket_options + [
        (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
        (socket.SOL_TCP, socket.TCP_KEEPIDLE, 45),
        (socket.SOL_TCP, socket.TCP_KEEPINTVL, 10),
        (socket.SOL_TCP, socket.TCP_KEEPCNT, 6)
    ]
    s = requests.session()

    header = {
        # "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        # "accept-encoding": "gzip, deflate, br",
        # "accept-language": "en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7",
        # "cache-control": "max-age=0",
        # "upgrade-insecure-requests": "1",
        # "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"

        "Connection": "Keep-Alive",
        "Accept-Encoding": "identity",
        "User-Agent": "Wget/1.19.4 (linux-gnu)",
    }

    try:
        print(f'GET {url}')
        r = s.get(url, headers=header, verify=True, timeout=10)
    except Exception as e:
        msg = f'Network connection error'
        print(f"{msg}. {e}")
        return

    print("Status: ", r.status_code)
    if r.status_code != requests.codes.ok:
        msg = f'Network connection error'
        print(f'{msg}. Answer={r.status_code}')
        return

    print("Get - OK")
    return r.text


URL = "https://www.tripadvisor.ru/" + \
      "Hotel_Review-g609052-d650787-Reviews-Kolibri_Resort_Hotel-Avsallar_Alanya_Turkish_Mediterranean_Coast.html "
html = get_html_content(url=URL)
print(html[:256])
print("Ok")