import os
import sys
import argparse
import pathlib
import colorama

sys.path.append(os.path.dirname(__file__))
import common

def print_verbose(msg, verbose=False):
    if verbose:
        print(msg)

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "host_name", help="Host name (FQDN)"
    )
    parser.add_argument(
        "-c", "--ca-path", default=os.getcwd(),
        help="Path to offline CA directory (default is current working directory)"
    )
    parser.add_argument(
        "-b", "--batch-mode", action="store_true", default=False,
        help="Batch mode"
    )
    parser.add_argument(
        "-p", "--ca-password", default=os.environ.get("AO_ROOT_CA_PASSWORD"),
        help=(
            "Root CA key password (can also be specified using AO_ROOT_CA_PASSWORD "
            "environment variable)"
        )
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False,
        help="Increase output verbosity"
    )

    options, unknown = parser.parse_known_args() #pylint: disable=unused-variable
    return options

def main():
    options = parse_arguments()

    root_ca_cert = pathlib.Path(options.ca_path) / "root_ca/root_ca.crt"
    root_ca_key = pathlib.Path(options.ca_path) / "root_ca/root_ca.key"

    host_csr = pathlib.Path(options.ca_path) / f"output/{options.host_name}.csr"
    host_cert = host_csr.with_suffix(".crt")
    host_cert_key = host_csr.with_suffix(".key")
    ext_file = pathlib.Path(__file__).parent / "ssl" / "winrm_server_ext.cnf"

    print_verbose(f"Root CA: {root_ca_cert}", options.verbose)
    print_verbose(f"Root CA key: {root_ca_key}", options.verbose)
    print_verbose(f"Certificate request: {host_csr}", options.verbose)
    print_verbose(f"Certificate: {host_cert}", options.verbose)
    print_verbose(f"Certificate key: {host_cert_key}", options.verbose)

    print(f"\nGenerating SSL certificate for host {options.host_name}")
    host_csr.parent.mkdir(mode=0o775, parents=True, exist_ok=True)

    common.color_print_bright(colorama.Fore.CYAN, "\nGenerating private key file")
    common.run_with_masked_password([
        common.get_openssl_executable(),
        "genrsa", "-out", str(host_cert_key),
        "-passout", {"format": "pass:{}", "password": ""},
        "2048",
    ])

    common.color_print_bright(colorama.Fore.CYAN, "\nGenerating certificate request file")
    common.run([
        common.get_openssl_executable(),
        "req", "-new", "-nodes", "-sha256", "-key", str(host_cert_key), "-out", str(host_csr),
        "-subj", f"/CN={options.host_name}"
    ] + common.get_openssl_config())

    common.color_print_bright(colorama.Fore.CYAN, "\nSigning the certificate")
    openssl_command = [
        common.get_openssl_executable(),
        "x509", "-days", "3650",
        "-extensions", "winrm_server_ext", "-extfile", str(ext_file),
        "-req", "-CA", str(root_ca_cert), "-CAkey", str(root_ca_key), "-CAcreateserial"
    ]
    if options.ca_password is not None:
        openssl_command += ["-passin", {"format": "pass:{}", "password": options.ca_password}]
    openssl_command += ["-in", str(host_csr), "-out", str(host_cert)]

    common.run_with_masked_password(
        openssl_command,
        env=dict(os.environ, openssl_SAN=f"DNS:{options.host_name}")
    )

if __name__ == "__main__":
    main()
