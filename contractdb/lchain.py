import click
from contractdb.interfaces import StateInterface as si

pass_si = click.make_pass_decorator(si)

@click.group()
@click.argument('myargs', nargs=-1)
@click.pass_context
@click.option('--verbose', is_flag=True)
def cli(ctx, myargs, verbose):
    if verbose:
        click.echo('Verbose Mode - Active')
    ctx.obj = si(myargs)
    click.echo("arguments: %s", myargs)


@cli.command()
@pass_si
def status(si):
    """ : Cli Status"""
    click.echo(si.ok())


@cli.command()
@pass_si
@click.option('--name', default='None', help='Queries for given contract name')
def contract(si, name):
    """ : Get given contract code"""
    pass


@cli.command()
@pass_si
@click.option('--code', default='None', help='Give input file for new contract')
@click.option('--name', help='Name of new contract to run')
def run(si, code, name):
    """ : Run given tx dict """
    pass


@cli.command()
@pass_si
@click.option('--path', type=click.File('rb'), help='Give input file for new contract')
def lint(si, path):
    """ : Run linter on given code str """
    code = ""
    while True:
        chunk = path.read(1024)
        if not chunk:
            break
        code = code + " " + str(chunk)
    click.echo(code)

    # res = si.lint(code=code)
    # click.echo(res)

@cli.command()
@pass_si
@click.option('--path', type=click.File('rb'), help='Give input file for new contract')
def compile_contract(si, path):
    """ : Compile given code str """
    code = ""
    while True:
        chunk = path.read(1024)
        if not chunk:
            break
        code = code + " " + str(chunk)
    click.echo(code)

    # res = si.compile_code(code = code)
    # click.echo(res)


@cli.command()
@pass_si
@click.option('--contract', default='None', help='Name of contract')
def get_vars(si, contract):
    """ : Get Vars for given contract """
    pass


if __name__ == '__main__':

    cli()
