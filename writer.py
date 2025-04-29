from models import CloudCode

cc = CloudCode()
cc.write("main.py")

while True:
    input("Enter to write: ")
    cc.write("main.py")