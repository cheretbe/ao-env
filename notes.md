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

```
reg.exe ADD "HKCU\Software\Microsoft\Command Processor" /v AutoRun /t REG_SZ /d ^"^%HOMEDRIVE^%^%HOMEPATH^%\projects\ao-env\windows\ao-env_autoexec.bat^" /f
reg.exe ADD "HKCU\Software\Microsoft\Command Processor" /v AutoRun /t REG_SZ /d "%%HOMEDRIVE%%%%HOMEPATH%%\projects\ao-env\windows\ao-env_autoexec.bat" /f
```

```zsh
# Get list of supported colors
for code ({000..255}) print -P -- "$code: %K{$code}      %k%F{$code}\uE0B0 Foreground%f"
# Background/foreground combination test
(fcolor=009; bcolor=002; print -P "%K{$bcolor}%F{$fcolor} Color test %f%k%F{$bcolor}\uE0B0%f")
```

fonts
```
https://github.com/PygmalionPolymorph/dotfiles/blob/master/import_gnome_terminal
.local/share/fonts
```
