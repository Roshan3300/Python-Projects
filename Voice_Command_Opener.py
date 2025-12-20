import os

cmd = input("Say command(open chrome / open notepad): ").lower()

if "chrome" in cmd:
    os.system("start chrome")
elif "notepad" in cmd:
    os.system("start notepad")
else:
    print("Command not recognized.")
    