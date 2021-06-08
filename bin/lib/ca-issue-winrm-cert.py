import os
import sys
import argparse
import pathlib

sys.path.append(os.path.dirname(__file__))
import common

def print_verbose(msg, verbose=False):
    if verbose:
        print(msg)

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "ca_path", nargs="?", default=os.getcwd(),
        help="Path to offline CA directory (default is current working directory)"
    )
    parser.add_argument(
        "-b", "--batch-mode", action="store_true", default=False,
        help="Batch mode"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False,
        help="Increase output verbosity"
    )

    options, unknown = parser.parse_known_args() #pylint: disable=unused-variable
    return options

def main():
    options = parse_arguments()

    # print("there you go")

    root_ca_cert = pathlib.Path(options.ca_path) / "root_ca/root_ca.crt"
    root_ca_key = pathlib.Path(options.ca_path) / "root_ca/root_ca.key"

    host_name = "dummy.domain.tld"
    host_csr = pathlib.Path(options.ca_path) / f"output/{host_name}.csr"
    host_cert = host_csr.with_suffix(".crt")
    host_cert_key = host_csr.with_suffix(".key")
    ext_file = pathlib.Path(__file__).parent / "ssl" / "winrm_server_ext.cnf"

    host_csr.parent.mkdir(mode=0o775, parents=True, exist_ok=True)

    print_verbose(f"Root CA: {root_ca_cert}", options.verbose)
    print_verbose(f"Root CA key: {root_ca_key}", options.verbose)
    print_verbose(f"Certificate request: {host_csr}", options.verbose)
    print_verbose(f"Certificate: {host_cert}", options.verbose)
    print_verbose(f"Certificate key: {host_cert_key}", options.verbose)

    print("\nGenerating private key file")
    common.run_with_masked_password([
        common.get_openssl_executable(),
        "genrsa", "-out", str(host_cert_key),
        "-passout", {"format": "pass:{}", "password": ""},
        "2048",
    ])

    print("\nGenerating certificate request file")
    common.run_with_masked_password([
        common.get_openssl_executable(),
        "req", "-new", "-nodes", "-sha256", "-key", str(host_cert_key), "-out", str(host_csr),
        "-subj", f"/CN={host_name}"
    ] + common.get_openssl_config())

# "%~dp0OpenSSL-Win64\bin\openssl.exe" ^
#   x509 -req -extensions client_server_ssl ^
#   -extfile "%~dp0openssl-ext.conf" ^
#   -in "%TEMP%\%DEVICE_CN%.csr" -CA "%~dp0ca-files\ca.cert.pem" -CAkey "%~dp0ca-files\ca.key.pem" -CAcreateserial ^
#   -out "%TEMP%\%DEVICE_CN%.crt" -days 3650 -sha256

    print("\nSigning the certificate")
    # common.run_with_masked_password(
    #     [
    #         common.get_openssl_executable(),
    #         "x509", "-days", "3650",
    #         "-extensions", "winrm_server_ext", "-extfile", str(ext_file),
    #         "-req", "-CA", str(root_ca_cert), "-CAkey", str(root_ca_key), "-CAcreateserial",
    #         # "-passin", {"format": "pass:{}", "password": "0000"},
    #         "-in", str(host_csr), "-out", str(host_cert),
    #     ],
    #     env={"openssl_SAN": f"DNS:{host_name}"}
    # )

    import subprocess
    subprocess.check_call(
        [
            common.get_openssl_executable(),
            "x509", "-days", "3650",
            "-extensions", "winrm_server_ext", "-extfile", str(ext_file),
            "-req", "-CA", str(root_ca_cert), "-CAkey", str(root_ca_key), "-CAcreateserial",
            # "-passin", {"format": "pass:{}", "password": "0000"},
            "-in", str(host_csr), "-out", str(host_cert),
        ],
        env={"openssl_SAN": f"DNS:{host_name}"}
    )



if __name__ == "__main__":
    main()
