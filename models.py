import os, json, time
from fragment import CloudFragment

# plan
# - interactive init, or manual parameter pass
# - {"code": "", "output": "", "executed": Bool}
# - fetchRunLive()
# - fetchRun()
# - write()

class CloudCode:
    def __init__(self, interactive=True):
        self.fragment = CloudFragment()
        
        manual_init = False
        
        # Check if cloud_code.json exists and load it
        if os.path.isfile(os.path.join(os.getcwd(), "cloud_code.json")):
            data = None
            with open("cloud_code.json", "r") as f:
                data = json.load(f)
            
            if "fragmentID" in data and "secret" in data and "apiKey" in data:
                self.fragment.fragmentID = data["fragmentID"]
                self.fragment.secret = data["secret"]
                if self.fragment.apiKey == None:
                    self.fragment.apiKey = data["apiKey"]
            else:
                raise Exception("CLOUDCODE ERROR: Invalid cloud_code.json file.")
            
            self.fragment.read()
        elif interactive:
            # Interactive CloudCode setup
            # Two options: create new fragment or use existing one
            
            if self.fragment.apiKey == None:
                self.fragment.apiKey = input("CC: Enter server API key: ")
                print()
            
            if input("CC: Initialise new CloudCode? (y/n) ").lower() == "y":
                self.fragment.secret = input("CC: Enter your secret key: ")
                self.fragment.reason = input("CC: Enter reason for fragment creation: ")
                print()
                
                print("CC: Requesting new fragment...")
                res = self.fragment.request()
                if res.startswith("ERROR"):
                    raise Exception("CLOUDCODE INIT ERROR: Failed to create fragment. Response: {}".format(res))
                
                while True:
                    input("CC: Fragment requested. Please hit Enter after approval.")
                    res = self.fragment.read()
                    if isinstance(res, str):
                        print("CC: Fragment read failed. Please ensure approval and try again. (Response: {})".format(res))
                    else:
                        break
            else:
                self.fragment.fragmentID = input("CC: Enter fragment ID: ")
                self.fragment.secret = input("CC: Enter secret key: ")
        else:
            manual_init = True
        
        if not manual_init:
            with open("cloud_code.json", "w") as f:
                json.dump({
                    "fragmentID": self.fragment.fragmentID,
                    "secret": self.fragment.secret,
                    "apiKey": self.fragment.apiKey
                }, f)
            
        else:
            print("CC: Manual init mode. Please set up this instance manually.")
        
        print("CC: Init successful.")
    
    def write(self, filePath):
        if not os.path.isfile(filePath):
            raise Exception("CLOUDCODE ERROR: File does not exist.")

        with open(filePath, "r") as f:
            code = f.read()
        
        self.fragment.data["code"] = code
        self.fragment.data["executed"] = False
        self.fragment.write()
        print("CC: Code written.")
    
    def fetchRun(self, ignoreExecuted=False, noPrint=False, runner=None):
        data = self.fragment.read()
        if isinstance(data, str):
            raise Exception("CLOUDCODE ERROR: Failed to fetch run. Response: {}".format(data))
        
        if data["code"].strip() == "":
            print("CC: No code to run.")
            return
        if not ignoreExecuted and data["executed"]:
            if not noPrint:
                print("CC: Code already executed.")
            return
        
        # Execute the code
        if runner is not None:
            runner(data["code"])
        else:
            exec(data["code"])
        
        print("CC: Code executed.")
        
        if not data["executed"]:
            self.fragment.data["executed"] = True
            self.fragment.write()
    
    def fetchRunLive(self, runner=None):
        while True:
            self.fetchRun(ignoreExecuted=False, noPrint=True, runner=runner)
            time.sleep(2)
    
    def fetchRunLiveWS(self, ignoreExecuted=False, ignoreInitial=False, noPrint=False, runner=None):
        if self.fragment.stream == None:
            r = self.fragment.initStream()
            if r != True:
                print("CC ERROR: Failed to initialize stream. Response: {}".format(r))
        
        def defaultWSRunner(data: dict):
            if "code" not in data or data["code"].strip() == "":
                print("CC: No code to run.")
                return
            
            if not ignoreExecuted and data["executed"]:
                # This flow typically would not happen in a WebSocket-streaming based context
                if not noPrint:
                    print("CC: Code already executed.")
                return

            # Execute the code
            if runner is not None:
                runner(data["code"])
            else:
                exec(data["code"])
            
            if not data["executed"]:
                self.fragment.data["executed"] = True
                r = self.fragment.writeWS()
                if r != True:
                    print("CC ERROR: Failed to write execution success. Response: {}".format(r))
                time.sleep(0.5)
            
            if not noPrint:
                print("CC: Code executed.")
        
        if not ignoreInitial:
            time.sleep(0.5)
            r = self.fragment.readWS()
            if isinstance(r, str):
                print("CC ERROR: Failed to read initial data. Response: {}".format(r))
                return
            time.sleep(0.5)
            defaultWSRunner(r)
        
        try:
            print()
            print("CC: Live stream started.")
            r = self.fragment.liveStream(handler=defaultWSRunner)
            if r != None:
                raise Exception(r)
        except KeyboardInterrupt:
            self.fragment.stream.disconnect()
            print()
            print("CC: Stopped live stream.")