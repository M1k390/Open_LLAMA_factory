

pot="""
def pot(hello:str):
    raise Exception("implement this function")
"""

scope={}
exec(pot,scope)

print(scope["pot"]("ao"))
