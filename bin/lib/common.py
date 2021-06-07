import sys
import platform
import pathlib
import humanfriendly.prompts

def ask_for_confirmation(prompt, batch_mode, default):
    if batch_mode:
        print(prompt)
        print("Batch mode is on. Autoselecting default option ({})".format(
            {True: "yes", False: "no"}[default]
        ))
        confirmed = default
    else:
        confirmed = humanfriendly.prompts.prompt_for_confirmation(
            prompt, default=default
        )
    if not confirmed:
        sys.exit("Cancelled by user")

def get_openssl_executable():
    if sys.platform == "win32":
        cpu_arch = {True: "x86", False: "x64"}[platform.architecture()[0] == "32bit"]
        return (
            pathlib.Path(__file__).resolve().parents[2] / "windows" / "openssl" /
            cpu_arch / "bin" / "openssl.exe"
        )
    return "openssl"
