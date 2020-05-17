import os
import json
import discord
import logging
import contextlib
from ftg.client import client
from discord.ext.commands import Bot


@contextlib.contextmanager
def bind_logger() -> None:
    try:
        logging.getLogger(__name__).setLevel(logging.INFO)

        log: logging.Logger = logging.getLogger(__name__)
        log.setLevel(logging.INFO)
        handler: logging.Handler = logging.FileHandler(
            filename="client/client.log",
            encoding="utf-8",
            mode="w"
        )
        fmt: logging.Formatter = logging.Formatter(
            "[{asctime}] [{levelname:<7}] {name}: {message}",
            "%Y-%m-%d %H:%M:%S",
            style="{"
        )
        handler.setFormatter(fmt)
        log.addHandler(handler)

        yield
    finally:
        for handle in log.handlers:
            handle.close()
            log.removeHandler(handle)


if __name__ == "__main__":
    with open("client/secret/secret.json") as secret:
        token = json.load(secret)["token"]

    with bind_logger():
        client: Bot = client.Ftg(
            ownerid=700091773695033505,
            activity=discord.Game(name='prefix: gn | https://github.com/Py-Ryan/ft.-Gunna')
        )
        client.run(token, os.listdir("extensions"))
