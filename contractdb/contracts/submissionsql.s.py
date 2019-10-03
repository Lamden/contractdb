@__export('submissionsql')
def submit_contract(name, code, constructor_args={}):
    __SQLContract().submit(name=name, code=code, constructor_args=constructor_args)
