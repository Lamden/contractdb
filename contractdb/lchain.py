import click
import json
import ecdsa
from contractdb.client.network import ChainCmds
from contractdb.utils import make_tx

@click.group()
@click.option('--verbose', is_flag=True)
def cli(verbose):
    if verbose:
        click.echo('Verbose Mode - Active')


@cli.command()
@click.option('--contract', default='None', help='Queries for given contract name')
def check(contract):
    """ : check given contract exists"""
    cmd = ChainCmds()

    command = {'command': 'get_contract',
               'arguments': {'name': contract}
               }
    click.echo("Query Command")
    click.echo(command)
    result = cmd.server_call(command)
    click.echo("Result")
    click.echo(result)


@cli.command()
@click.option('--contract', help='invoking contract name')
@click.option('--func', help='executing function')
@click.option('--name', help='name new contract')
@click.option('--code_path', type=click.Path(), help='Give input file for new contract')
def run(contract, func, name, code_path):
    """ : Run given tx dict """
    cmd = ChainCmds()

    nakey = ecdsa.SigningKey.generate(curve = ecdsa.NIST256p)
    pk = nakey.get_verifying_key().to_string().hex()

    code = ""
    with open(code_path, 'r') as f:
        code = f.read()

    tx = make_tx(nakey,
                 contract = contract,
                 func = func,
                 arguments = {
                     'code': code,
                     'name': name
                 })

    command = {'command': 'run',
               'arguments': {'transaction': tx}
               }
    click.echo("Query Command")
    click.echo(command)
    res = cmd.server_call(command)
    click.echo("Result")
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
    command = {'command': 'lint',
               'arguments': {'code': code}
               }
    click.echo("Query Command")
    click.echo(command)
    res = cmd.server_call(command)
    click.echo("Result")
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
    click.echo("Query Command")
    click.echo(command)
    res = cmd.server_call(command)
    click.echo("Result")
    click.echo(res)


@cli.command()
@click.option('--contract', default='None', help='Name of contract')
def get_vars(contract):
    """ : Get Vars for given contract """

    cmd = ChainCmds
    command = {'command': 'get_vars',
               'arguments': {'contract': contract}
               }
    click.echo("Query Command")
    click.echo(command)
    result = cmd.server_call(command)
    click.echo("Result")
    click.echo(result)


if __name__ == '__main__':
    cli()
