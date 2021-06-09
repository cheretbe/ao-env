import sys
import platform
import pathlib
import subprocess
import colorama
import humanfriendly.prompts

colorama.init()

def color_print(print_color, msg):
    print("{color}{msg}{reset}".format(
        color=print_color, msg=msg, reset=colorama.Style.RESET_ALL
    ))

def color_print_bright(print_color, msg):
    print("{color}{msg}{reset}".format(
        color=print_color + colorama.Style.BRIGHT, msg=msg, reset=colorama.Style.RESET_ALL
    ))


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
        return str(
            pathlib.Path(__file__).resolve().parents[2] / "windows" / "openssl" /
            cpu_arch / "bin" / "openssl.exe"
        )
    return "openssl"

def get_openssl_config():
    if sys.platform == "win32":
        return (
            [
                "-config",
                str(
                    pathlib.Path(__file__).resolve().parents[2] / "windows" /
                    "openssl" / "conf" / "openssl.cnf"
                )
            ]
        )
    return []

def run(cmd_args, echo=True, **kwargs):
    if echo:
        print(cmd_args)
    subprocess.check_call(cmd_args, **kwargs)

def run_with_masked_password(cmd_args, echo=True, **kwargs):
    cmd_to_run = []
    cmd_to_print = []
    for arg in cmd_args:
        if isinstance(arg, dict):
            cmd_to_run += [arg["format"].format(arg["password"])]
            cmd_to_print += [arg["format"].format("*****")]
        else:
            cmd_to_run += [arg]
            cmd_to_print += [arg]

    if echo:
        print("[{}]".format("], [".join(cmd_to_print)))
    cmd_rc = subprocess.call(cmd_to_run, **kwargs)
    if cmd_rc != 0:
        sys.exit(
            "Command [{}] returned non-zero exit status {}".format(
                "], [".join(cmd_to_print), cmd_rc
            )
        )
