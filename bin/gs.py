import subprocess

print("Fetching data from a remote repo")
subprocess.check_call("git fetch", shell=True)

#not_initialized = False
#need_update = False
#unresolved = False

print("Checking submodules status")
for line in subprocess.check_output("git submodule status --recursive", shell=True).decode("utf-8").splitlines():
    if line:
        text_status = ""
        status_char = line[:1]
        if status_char == "-":
            text_status = " -- not initialized"
        elif status_char == "+":
            text_status = " -- needs update"
        elif status_char == "U":
            text_status = " -- has merge conflicts"
        print("{line}{status}".format(line=line, status=text_status))

subprocess.check_call("git status", shell=True)