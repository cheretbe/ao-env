#!/bin/bash
set -euo

ao_env_root="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

declare -a APT_PACKAGES=("build-essential" "python3" "python3-dev" "python3-venv"
  "mc" "htop" "net-tools" "dnsutils" "mtr-tiny" "ncdu" "wget" "git"
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
  sudo PKGS="${PKGS}" -- sh -c '/usr/bin/apt-get -y -qq install ${PKGS}'
fi

echo "Creating '~/.local/share/fonts' directory"
mkdir -p "~/.local/share/fonts"

# ln -sfn TARGET LINK_NAME
ln -sfn "${ao_env_root}/fonts" "~/.local/share/fonts/ao-env"

virualenv_dir="${HOME}/.cache/ao-env/virtualenv-py3"
echo "virualenv path: ${virualenv_dir}"

if [ ! -d "${virualenv_dir}" ]; then
  echo "Creating virualenv"
  # mkdir -p "${virualenv_dir}"
  python3 -m venv "${virualenv_dir}"
fi

. "${virualenv_dir}/bin/activate"
# python3 -m site
pip3 install colorama asciimatics

exit 0

if ! [ -x "$(command -v python3)" ]; then
  apt-get update
  apt-get -y -q install build-essential python3 python3-dev python3-venv
fi

python3 ${ao_env_root}/install.py