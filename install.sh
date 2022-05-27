#!/bin/bash
set -eu

ao_env_root="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

declare -a APT_PACKAGES=("build-essential" "python3" "python3-dev" "python3-venv"
  "dialog" "mc" "htop" "net-tools" "dnsutils" "mtr-tiny" "ncdu" "wget" "git"
  "nano" "traceroute" "colordiff" "jq" "pv")

all_pkgs_installed=true
for pkg in "${APT_PACKAGES[@]}"
do
  if ! dpkg-query -Wf'${db:Status-abbrev}' "${pkg}" 2>/dev/null | grep -q '^.i'; then
    echo "  ${pkg} package is not installed"
    all_pkgs_installed=false
  fi
done

if [ "$all_pkgs_installed" = true ] ; then
  echo "All necessary packages are already installed"
else
  echo "Updating lists of packages"
  sudo -- sh -c '/usr/bin/apt-get -qq update'
  PKGS="${APT_PACKAGES[@]}"
  echo "About to install the following packages: ${PKGS}"
  if [ -v DEBIAN_FRONTEND ]; then
    sudo DEBIAN_FRONTEND="${DEBIAN_FRONTEND}" PKGS="${PKGS}" -- sh -c '/usr/bin/apt-get -y -qq install ${PKGS}'
  else
    sudo PKGS="${PKGS}" -- sh -c '/usr/bin/apt-get -y -qq install ${PKGS}'
  fi
fi

# echo "Creating '~/.local/share/fonts' directory"
# mkdir -p ~/.local/share/fonts

# [!] This breaks fonts for snap installation of Chromium (probably has
# something to with snap package not having corresponding 'connection')
# snap connections chromium
# TODO: check if 'sudo mount --bind ${ao_env_root}/fonts ~/.local/share/fonts/ao-env'
# will solve the issue
# echo "Creating symlink ~/.local/share/fonts/ao-env ==> ${ao_env_root}/fonts"
# ln -sfn ${ao_env_root}/fonts ~/.local/share/fonts/ao-env

virualenv_dir="${HOME}/.cache/ao-env/virtualenv-py3"
echo "virualenv path: ${virualenv_dir}"

if [[ "$(python3 -c 'import sys; print(sys.version_info.minor)')" == "9" ]]; then
  python3_exe="python3"
else
  python3_exe="python3.9"
fi
echo "Python 3 executable: ${python3_exe}"

if [ ! -d "${virualenv_dir}" ]; then
  echo "Creating virualenv"
  ${python3_exe} -m venv "${virualenv_dir}"
fi

. "${virualenv_dir}/bin/activate"
# python3 -m site
pip3 install wheel
pip3 install colorama asciimatics humanfriendly PyInquirer packaging requests

if ! grep -q "export PATH=${ao_env_root}/bin:" ~/.profile; then
  echo "Adding '${ao_env_root}/bin' to PATH"
  echo -e "\nexport PATH=${ao_env_root}/bin:\$PATH\n" >> ~/.profile
fi
