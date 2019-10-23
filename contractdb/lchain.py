import click
import json
from contractdb.client.network import ChainCmds
from contractdb.utils import make_tx

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
@click.option('--key', help=' ecdsa.SigningKey')
@click.option('--contract', help='contract name')
@click.option('--func', help='executing function')
@click.option('--name', help='name')
@click.option('--code_path', type=click.File('rb'), help='Give input file for new contract')
def run(key, contract, func, name, code_path):
    """ : Run given tx dict """
    cmd = ChainCmds()

    code = ""
    while True:
        chunk = code_path.read(1024)
        if not chunk:
            break
        code = code + " " + str(chunk)


    tx = make_tx(key,
                 contract = contract,
                 func = func,
                 arguments = {
                     'code': code,
                     'name': name
                 })

    command = {'command': 'run',
               'arguments': {'transaction': tx}
               }

    res = cmd.server_call(command)
    click.echo(res)


@cli.command()
@click.option('--path', type=click.Path(), help='Give input file for new contract')
def lint(path):
    """ : Run linter on given code str """
    cmd = ChainCmds()
    code = None
    with open(path, 'r') as f:
        code = f.read()

    click.echo(path)
    print(code)
    command = {'command': 'lint',
               'arguments': {'code': code}
               }

    click.echo(command)
    res = cmd.server_call(command)
    click.echo(res)


@cli.command()
@click.option('--path', type=click.File('rb'), help='Give input file for new contract')
def compile_contract(path):
    """ : Compile given code str """
    cmd = ChainCmds()

    code = None
    with open(path, 'r') as f:
        code = f.read()

    command = {'command': 'compile',
               'arguments': {'code': code}
               }
    click.echo(command)
    res = cmd.server_call(command)
    click.echo(res)


@cli.command()
@click.option('--contract', default='None', help='Name of contract')
def get_vars(contract):
    """ : Get Vars for given contract """


if __name__ == '__main__':
    cli()
