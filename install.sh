#!/bin/bash
ao_env_root="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

grep -q -F "source ${ao_env_root}/ao-env_zshrc" ${HOME}/.zshrc
if [ $? -ne 0 ]; then
  echo "Updating .zshrc"
  if [ -f ${HOME}/.zshrc ]; then cp ${HOME}/.zshrc{,.ao-env_bak}; fi
  echo "source ${ao_env_root}/ao-env_zshrc" >>${HOME}/.zshrc
fi

echo "Done"
