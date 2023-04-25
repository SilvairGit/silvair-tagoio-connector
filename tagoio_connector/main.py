import asyncio
import logging
import struct
from datetime import datetime

from tagoio_connector.silvair import (
    get_messages,
    open_connection,
    recv_multipart,
    send_multipart,
)


async def _main(project_id, email, password):
    messages = get_messages()

    async with open_connection(project_id, email, password) as connection:
        await send_multipart(connection, b"\x00", b"#.LIGHT_LIGHTNESS_STATUS")

        while True:
            frames = await recv_multipart(connection)

            # ignore everything but "RECEIVE" messages
            if frames[0] != b"\x02":
                continue

            payload = frames[1]
            header, body = payload[:12], payload[12:]
            timestamp, src, dst = struct.unpack("<QHH", header)
            dt = datetime.fromtimestamp(timestamp / 1000)

            msg = messages.AccessMessage.from_bytes_packed(body)

            # ignore "optional" variants of the message - they mean that the luminaire is currently fading
            if (
                msg.which() == "lightLightnessStatus"
                and msg.lightLightnessStatus.which() == "minimal"
            ):
                lightness = msg.lightLightnessStatus.minimal.presentLightness
                logging.info(
                    "[%s] %04x -> %04x: %s", dt.isoformat(), src, dst, lightness
                )


def main():
    project_id = input("Project ID")
    email = input("Email")
    password = input("Password")

    logging.basicConfig(level=logging.INFO)
    asyncio.run(_main(project_id, email, password))
