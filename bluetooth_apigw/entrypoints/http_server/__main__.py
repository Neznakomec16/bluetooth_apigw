import logging

from aiohttp.web import run_app
from bluetooth_apigw.entrypoints.http_server.app import create_app

logging.basicConfig(level=logging.INFO)


def cli():
    app = create_app()

    run_app(app)


if __name__ == "__main__":
    cli()
