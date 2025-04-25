from models import CloudCode

def e(code):
    exec(code, globals(), globals())  # Use globals() for both global and local scope

cc = CloudCode()
cc.fetchRunLive(runner=e)