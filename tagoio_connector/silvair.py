import logging
import os
import tempfile
from contextlib import asynccontextmanager

import capnp
import requests
import websockets

capnp.remove_import_hook()

DOMAIN = "api.platform-preprod.silvair.com"
DIR = os.path.expanduser("~/.config/tagoio_connector")
os.makedirs(DIR, exist_ok=True)


def open_connection(project_id, email, password, partner_id="silvair"):
    try:
        with open(f"{DIR}/silvair_token") as token_file:
            token = token_file.read()

        requests.get(
            f"https://{DOMAIN}/public/projects", headers={"Authorization": token}
        ).raise_for_status()

        logging.info("Reusing token for %s", email)

    except (requests.HTTPError, FileNotFoundError):
        token = None

    if not token:
        logging.info("Authenticating as %s", email)
        response = requests.post(
            f"https://{DOMAIN}/public/auth/login",
            json=dict(partnerId=partner_id, email=email, password=password),
        ).raise_for_status()

        token = response.json()["token"]

    with open(f"{DIR}/silvair_token", "w") as token_file:
        token_file.write(token)

    return websockets.connect(
        f"wss://{DOMAIN}/public/projects/{project_id}/mesh",
        extra_headers={"Authorization": token},
    )


async def send_multipart(connection, *frames):
    *head, tail = frames

    for i in head:
        await connection.send(b"\x01" + i)

    await connection.send(b"\x00" + tail)


async def recv_multipart(connection):
    more, *frame = await connection.recv()
    frames = [bytes(frame)]

    while more:
        more, *frame = await connection.recv()
        frames.append(bytes(frame))

    return frames


def get_messages():
    message_definitions = requests.get(
        f"http://{DOMAIN}/public/control/message_definitions"
    )
    with tempfile.NamedTemporaryFile(suffix=".capnp") as f:
        f.write(message_definitions.text.encode())
        return capnp.load(f.name)
