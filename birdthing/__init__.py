__version__ = "0.1.0"

import click

from birdthing import manager, detect


@click.command()
@click.option(
    "-t",
    "--track",
    multiple=True,
    type=click.Choice(map(lambda v: v["name"], detect.LABEL_MAP.values())),
    help="Track the specified type of object (can be specified multiple times)",
)
def main(track):
    manager.run(track)
