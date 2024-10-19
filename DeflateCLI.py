import click
from DeflateCompressor import DeflateCompressor


def permission_tracker(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PermissionError:
            click.echo("Compressor don't have permissions")

    return wrapper


@click.group()
def cli():
    """Deflate Compressor"""


@cli.command()
@click.argument('path', nargs=-1)
def compress(path):
    """Compress a file"""
    try:
        _compress(path)
    except PermissionError:
        click.echo("Compressor don't have permissions")


@cli.command()
@click.argument('path', nargs=-1)
def decompress(path):
    """Decompress a file"""
    _decompress(path)


@permission_tracker
def _compress(path):
    dc = DeflateCompressor()
    with open(path, "rb") as f:
        compressed = dc.compress(f)
    with open(f"{path}.dfl", "wb") as f:
        f.write(compressed)


@permission_tracker
def _decompress(path):
    dc = DeflateCompressor()
    with open(path, "wb") as f:
        compressed = dc.compress(f)
    with open(path[:-4], "wb") as f:
        f.write(compressed)
