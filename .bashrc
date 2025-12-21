# ~/.bashrc: executed by bash(1) for non-login shells.
# see /usr/share/doc/bash/examples/startup-files (in the package bash-doc)
# for examples

# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac

# don't put duplicate lines or lines starting with space in the history.
# See bash(1) for more options
HISTCONTROL=ignoreboth

# append to the history file, don't overwrite it
shopt -s histappend

# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
HISTSIZE=1000
HISTFILESIZE=2000

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# If set, the pattern "**" used in a pathname expansion context will
# match all files and zero or more directories and subdirectories.
#shopt -s globstar

# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

# set a fancy prompt (non-color, unless we know we "want" color)
case "$TERM" in
    xterm-color|*-256color) color_prompt=yes;;
esac

# uncomment for a colored prompt, if the terminal has the capability; turned
# off by default to not distract the user: the focus in a terminal window
# should be on the output of commands, not on the prompt
#force_color_prompt=yes

if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
	# We have color support; assume it's compliant with Ecma-48
	# (ISO/IEC-6429). (Lack of such support is extremely rare, and such
	# a case would tend to support setf rather than setaf.)
	color_prompt=yes
    else
	color_prompt=
    fi
fi

if [ "$color_prompt" = yes ]; then
    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
else
    PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
fi
unset color_prompt force_color_prompt

# If this is an xterm set the title to user@host:dir
case "$TERM" in
xterm*|rxvt*)
    PS1="\[\e]0;${debian_chroot:+($debian_chroot)}\u@\h: \w\a\]$PS1"
    ;;
*)
    ;;
esac

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    #alias dir='dir --color=auto'
    #alias vdir='vdir --color=auto'

    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

# colored GCC warnings and errors
#export GCC_COLORS='error=01;31:warning=01;35:note=01;36:caret=01;32:locus=01:quote=01'

# some more ls aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

# Add an "alert" alias for long running commands.  Use like so:
#   sleep 10; alert
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'

# Alias definitions.
# You may want to put all your additions into a separate file like
# ~/.bash_aliases, instead of adding them here directly.
# See /usr/share/doc/bash-doc/examples in the bash-doc package.

if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi

#############################################
# Personal Config
#############################################

eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
eval "$(starship init bash)"
eval "$(zoxide init bash)"

# User created run calls
if [ -f /home/linuxbrew/.linuxbrew/bin/fastfetch ]; then
	fastfetch
fi


#############################################
#Costom Functions
#############################################

# Creating Directories
function take {
	mkdir -p $1
	cd $1
}
# Quick Notes
function note {
	echo "date: $(date)" >> $HOME/qnotes.txt
	echo "$@" >> $HOME/qnotes.txt
	echo "" >> $HOME/qnotes.txt
}
# Eazy Whereis
function fsel {
	output=$(whereis $1)
	output_array=($output)
	counter=1
	for element in "${output_array[@]}"; do
	  echo "$counter. $element"
	  ((counter++))
	done
	echo "$counter. End the command"
	read -p "Select an output by its number: " selection
	if [[ $selection -gt 0 && $selection -le ${#output_array[@]} ]]; then
	  selected_element=${output_array[$((selection-1))]}
	  echo "You selected: $selected_element"
	  
	  # Check if the selected element is a directory and change to it
	  if [ -d "$selected_element" ]; then
	    cd "$selected_element"
	    echo "Changed directory to: $selected_element"
	  else
	    # Get the directory name and change to it
	    directory=$(dirname "$selected_element")
	    if [ -d "$directory" ]; then
	      cd "$directory"
	      echo "Changed directory to: $directory"
	    else
	      echo "Cannot change directory to: $directory"
	    fi
	  fi
	elif [[ $selection -eq $counter ]]; then
	  echo "Ending the command"
	else
	  echo "Invalid selection"
	fi
}

# Move files and DIR with progress bar
lmvr() {
    local src="$1"
    local dest="$2"

    if [[ -z "$src" || -z "$dest" ]]; then
        echo "Usage: lmvr <source> <destination>"
        return 1
    fi

    if [[ ! -e "$src" ]]; then
        echo "Source '$src' does not exist."
        return 1
    fi

    # Get all files and total size
    mapfile -t files < <(find "$src" -type f)
    local total_files=${#files[@]}
    if (( total_files == 0 )); then
        echo "No files to move."
        return 1
    fi

    local total_bytes=0
    for f in "${files[@]}"; do
        (( total_bytes += $(stat -c%s "$f") ))
    done

    echo "Moving $total_files files (${total_bytes} bytes) from '$src' to '$dest'..."

    mkdir -p "$dest"

    local moved_bytes=0
    local count=0
    local start_time=$(date +%s)
    local last_update_time=$start_time

    for file in "${files[@]}"; do
        local rel_path="${file#$src/}"
        local target_dir="$dest/$(dirname "$rel_path")"
        mkdir -p "$target_dir"

        local file_size=$(stat -c%s "$file")
        mv "$file" "$target_dir/"

        (( moved_bytes += file_size ))
        (( count++ ))

        local now=$(date +%s)
        if (( now > last_update_time )); then
            local elapsed=$(( now - start_time ))
            local speed=$(( moved_bytes / 1024 / 1024 / (elapsed + 1) )) # MB/s
            local remaining=$(( total_bytes - moved_bytes ))
            local eta_seconds=$(( speed > 0 ? (remaining / 1024 / 1024 / speed) : 0 ))

            # Convert ETA to human-readable format
            local eta
            if (( eta_seconds >= 60 )); then
                local mins=$((eta_seconds / 60))
                local secs=$((eta_seconds % 60))
                eta="${mins}m ${secs}s"
            else
                eta="${eta_seconds}s"
            fi

            # Progress bar
            local progress=$(( count * 100 / total_files ))
            local bar_width=$(( progress / 2 ))
            printf "\rProgress: [%-50s] %3d%% | Speed: %4d MB/s | ETA: %s" \
                "$(head -c $bar_width < /dev/zero | tr '\0' '#')" \
                "$progress" "$speed" "$eta"

            last_update_time=$now
        fi
    done

    echo -e "\nMove complete."
    find "$src" -depth -type d -empty -delete
}

cpp() {
    if [[ $# -lt 2 ]]; then
        echo "Usage: cpp <source> <destination>"
        return 1
    fi

    local source="$1"
    local dest="$2"

    if ! command -v numfmt >/dev/null; then
        echo "Error: 'numfmt' is required but not found."
        return 1
    fi

    # Build file list
    mapfile -t files < <(find "$source" -type f)

    # Get total size in bytes
    total_size=0
    for file in "${files[@]}"; do
        (( total_size += $(stat -c%s "$file") ))
    done

    # Start copying
    echo "Copying from '$source' to '$dest'..."
    mkdir -p "$dest"

    copied=0
    start_time=$(date +%s)

    for file in "${files[@]}"; do
        rel_path="${file#$source/}"
        target_path="$dest/$rel_path"
        mkdir -p "$(dirname "$target_path")"
        
        cp "$file" "$target_path"

        file_size=$(stat -c%s "$file")
        (( copied += file_size ))

        elapsed=$(( $(date +%s) - start_time ))
        elapsed=${elapsed:-1} # avoid division by zero
        percent=$(( copied * 100 / total_size ))
        speed=$(echo "$copied / 1048576 / $elapsed" | bc -l)
        eta=$(( (total_size - copied) / (copied / elapsed + 1) ))

        # Format progress bar
        bar_length=30
        filled=$(( percent * bar_length / 100 ))
        bar=$(printf "%-${bar_length}s" "#" | tr ' ' '#' | cut -c1-"$filled")
        empty=$(printf "%-${bar_length}s" " " | cut -c"$((filled + 1))"-"$bar_length")

        printf "\r[%s%s] %3d%% %.2f MB/s ETA: %02d:%02d " "$bar" "$empty" "$percent" "$speed" "$((eta/60))" "$((eta%60))"
    done

    echo -e "\nDone."
}

############################################
#Costom Alias
############################################

# Changing "ls" to "eza"
alias ls='eza -al --color=always --group-directories-first'
alias la='eza -a --color=always --group-directories-first'
alias ll='eza -l --color=always --group-directories-first'
alias ld='eza -dl */ --color=always'
alias lr='eza -lR --color=always'

# Changing z to cd
alias cd="z"
alias cdd="zi"
alias cdq="zq"
alias cdad="z add"
alias cdr="z remove"

# Git
alias gitcl="git clone"
alias gitad="git add ."
alias gitcom="git commit -m"
alias gitpu="git push -u origin main"

# ps
alias psa="ps auxf"
alias psgrep="ps aux | grep -v grep | grep -i -e VSZ -e"
alias psmem='ps auxf | sort -nr -k 4'
alias pscpu='ps auxf | sort -nr -k 3'

alias sr='source ~/.bashrc'
alias cl="clear"
alias mi='micro'
# Trimming Strings
alias trim="awk '{\$1=\$1;print}'"
# get error messages from journalctl
alias jctl="journalctl -p 3 -xb"
# human-readable sizes
alias df='df -h'
# show sizes in MB
alias free='free -m'
# colorize output (good for log files)
alias grep='grep --color=auto'

