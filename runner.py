from models import CloudCode

def e(code):
    try:
        exec(code, globals(), globals())  # Use globals() for both global and local scope
    except Exception as e:
        print("Exec error: {}".format(e))

cc = CloudCode()
cc.fetchRunLiveWS(runner=e)
print()
print("Ping:", cc.fragment.stream.ping())
print()
cc.fragment.stream.showHistory()