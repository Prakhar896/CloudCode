from models import CloudCode
import json

cc = CloudCode()

contWriter = input("HTTP or WS? (h/w) ").lower() == "w"

if not contWriter:
    while True:
        input("Enter to write: ")
        cc.write("main.py")
else:
    try:
        r = cc.fragment.initStream()
        if r != True:
            print("Error: Failed to init stream. Err: {}".format(r))
        
        while True:
            input("Enter to write: ")
            with open("main.py", "r") as f:
                code = f.read()
            cc.fragment.data["code"] = code
            cc.fragment.data["executed"] = False
            cc.fragment.writeWS()
    except KeyboardInterrupt:
        cc.fragment.stream.disconnect()