* https://developer.atlassian.com/blog/2016/02/best-way-to-store-dotfiles-git-bare-repo/
* https://dotfiles.github.io/

-----
* Git status like this: https://raw.github.com/nicksp/dotfiles/master/iterm/nick-terminal.png
    * powerline style
    * https://github.com/bhilburn/powerlevel9k
    * https://github.com/powerline/fonts
    * https://github.com/smkent/dotfiles
    * https://github.com/ryanoasis/nerd-fonts#font-patcher

* zsh
    * https://github.com/robbyrussell/oh-my-zsh


Sample `.zshrc` file
```shell
ZSH_THEME="powerlevel9k/powerlevel9k"

#POWERLEVEL9K_MODE="awesome-patched"
#POWERLEVEL9K_MODE='nerdfont-complete'

POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(status command_execution_time)
POWERLEVEL9K_LEFT_PROMPT_ELEMENTS=(context dir_writable dir vcs virtualenv)
POWERLEVEL9K_VIRTUALENV_BACKGROUND='094'

POWERLEVEL9K_COMMAND_EXECUTION_TIME_THRESHOLD=1
POWERLEVEL9K_COMMAND_EXECUTION_TIME_BACKGROUND='245'
POWERLEVEL9K_COMMAND_EXECUTION_TIME_FOREGROUND='black'

source $ZSH/oh-my-zsh.sh
POWERLEVEL9K_EXECUTION_TIME_ICON='\uF49B'

source virtualenvwrapper.sh
```
