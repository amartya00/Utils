#!/bin/bash

tasksAutoComplete() {
    local cur
    local prev
    cur=$1
    prev=$2
    if [ "$prev" == "-e" ]; then
        COMPREPLY=( $( compgen -W "`ls $HOME/.Tasks/`" "$cur" ) )
    elif [ "$cur" == "-e" ]; then
        COMPREPLY=( $( compgen -W "`ls $HOME/.Tasks/`" "" ) )
    else
        COMPREPLY=( $( compgen -W "-h -n -e -u -a -t -c -d -l -i -f -r" "'$cur'" ) )
    fi
    return 0
}

utilsComplete() {
    local cur
    local prev
    COMPREPLY=()
    cur=${COMP_WORDS[COMP_CWORD]}
    prev=$3
    comm=${COMP_WORDS[0]}
    subcomm=${COMP_WORDS[1]}
    case "$subcomm" in
        "Tasks") tasksAutoComplete "$cur" "$prev" ;;
        *) COMPREPLY=( $( compgen -W "Time Tasks Services CredsManager" "$cur" ) ) ;;
    esac
    return 0
}

complete -F utilsComplete -o filenames Utils
