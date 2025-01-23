# cli.py

import click
from DeflateCompressor import DeflateCompressor, Archiver

@click.group()
def cli():
    pass

@cli.command()
@click.option(
    '--archive', '-a',
    required=True,
    type=click.Path(),
    help='Имя создаваемого архива (например, archive.dfl)'
)
@click.argument(
    'files',
    nargs=-1,
    type=click.Path(exists=True, readable=True)
)
def archive(archive, files):
    if not files:
        click.echo("Не указаны файлы для архивирования.", err=True)
        return

    compressor = DeflateCompressor()
    archiver = Archiver(compressor)
    archiver.archive_files(files, archive)
    click.echo("Архивирование завершено.")

@cli.command()
@click.option(
    '--archive', '-a',
    required=True,
    type=click.Path(exists=True, readable=True),
    help='Имя архива для разархивирования'
)
@click.option(
    '--output', '-o',
    default='.',
    type=click.Path(),
    help='Папка для извлечённых файлов (по умолчанию текущая директория)'
)
def extract(archive, output):
    archiver = Archiver(DeflateCompressor())
    archiver.extract_archive(archive, output)
    click.echo("Разархивирование завершено.")


if __name__ == '__main__':
    cli()
