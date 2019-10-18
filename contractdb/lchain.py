import click
import json
from contractdb.client.network import ChainCmds



@click.group()
@click.option('--verbose', is_flag=True)
def cli(verbose):
    if verbose:
        click.echo('Verbose Mode - Active')


@cli.command()
def status():
    """ : Cli Status"""


@cli.command()
@click.option('--name', default='None', help='Queries for given contract name')
def contract(name):
    """ : Get given contract code"""
    cmd = ChainCmds()

    command = {'command': 'get_contract',
               'arguments': {'name': name}
               }
    click.echo(command)
    result = cmd.server_call(command)
    click.echo(result)


@cli.command()
@click.option('--tx', help='json string')
def run(tx):
    """ : Run given tx dict """
    dict = json.loads(tx)
    res = run(dict)
    click.echo(res)


@cli.command()
@click.option('--path', type=click.File('rb'), help='Give input file for new contract')
def lint(path):
    """ : Run linter on given code str """
    cmd = ChainCmds()
    code = ""
    while True:
        chunk = path.read(1024)
        if not chunk:
            break
        code = code + " " + str(chunk)

    command = {'command': 'lint',
               'arguments': {'code': code}
               }

    res = cmd.server_call(command)
    click.echo(res)


@cli.command()
@click.option('--path', type=click.File('rb'), help='Give input file for new contract')
def compile_contract(path):
    """ : Compile given code str """
    code = ""
    while True:
        chunk = path.read(1024)
        if not chunk:
            break
        code = code + " " + str(chunk)
    click.echo(code)


@cli.command()
@click.option('--contract', default='None', help='Name of contract')
def get_vars(contract):
    """ : Get Vars for given contract """


if __name__ == '__main__':
    cli()
