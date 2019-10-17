import click
from contractdb.interfaces import StateInterface as si


@click.group()
def cli():
    pass


@cli.command()
def status():
    """Description: Cli Status"""
    click.echo('Active')


@cli.command()
@cli.options('--string', default='None')
def check(string):
    """Description: State interface check"""
    click.echo(si.get_contract('stustu'))


if __name__ == '__main__':
    cli()
