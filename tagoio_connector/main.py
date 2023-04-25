import asyncio
import json
import logging
import struct
from datetime import datetime

from tagoio_connector import silvair, tagoio


async def _main(project_id, email, password, profile_token, device_token):
    messages = silvair.get_messages()

    async with silvair.open_connection(
        project_id, email, password
    ) as silvair_connection, tagoio.open_connection(
        profile_token, device_token
    ) as tagoio_connection:
        await silvair_connection.send_multipart(b"\x00", b"#.LIGHT_LIGHTNESS_STATUS")

        while True:
            frames = await silvair_connection.recv_multipart()

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

                await tagoio_connection.publish(
                    f"{src:04x}/lightness",
                    json.dumps(dict(variable="lightness", value=lightness)),
                )


def main():
    project_id ="<SILVAIR PROJECT ID>"
    email = "<SILVAIR USERNAME>"
    password = "<SILVAIR PASSWORD>"

    profile_token = "<TAGO.IO PROFILE/ACCOUNT TOKEN>"
    device_token = "<TAGO.IO DEVICE TOKEN>"

    logging.basicConfig(level=logging.INFO)
    asyncio.run(_main(project_id, email, password, profile_token, device_token))
