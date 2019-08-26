def submit_contract(name, code, constructor_args={}):
    author = ctx.signer
    __SpaceStorage().create_space(name=name, code=code, author=author, constructor_args=constructor_args)
