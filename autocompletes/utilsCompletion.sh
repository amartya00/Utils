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

todoAutoComplete() {
    local cur
    local prev
    cur=$1
    prev=$2
    if [ "$prev" == "-d" ]; then
        COMPREPLY=( $( compgen -W '"%Y-%m-%d-%H-%M" "%Y-%m-%d" "%H:%M" now tomorrow today' "$cur" ) )
    elif [ "$cur" == "-d" ]; then
        COMPREPLY=( $( compgen -W '"%Y-%m-%d-%H-%M" "%Y-%m-%d" "%H:%M" now tomorrow today' "" ) )
    elif [ "$prev" == "-d" ]; then
        COMPREPLY=( $( compgen -W '"%Y-%m-%d-%H-%M" "%Y-%m-%d" "%H:%M" now tomorrow today' "$cur" ) )
    elif [ "$cur" == "-d" ]; then
        COMPREPLY=( $( compgen -W '"%Y-%m-%d-%H-%M" "%Y-%m-%d" "%H:%M" now tomorrow today' "" ) )
    else
        COMPREPLY=( $( compgen -W "-h -n -d -t -i -u -x -s -c --help --newTodo --dueDate --status --todoId --update --delete --sync --clean" "'$cur'" ) )
    fi
    return 0
}

timeUtilsComplete() {
    local cur
    local prev
    cur=$1
    prev=$2
    if [ "$prev" == "-f" ]; then
        COMPREPLY=( $( compgen -W '"%Y-%m-%d-%H-%M" "%Y-%m-%d" "%H:%M" now tomorrow today' "$cur" ) )
    elif [ "$cur" == "-f" ]; then
        COMPREPLY=( $( compgen -W '"%Y-%m-%d-%H-%M" "%Y-%m-%d" "%H:%M" now tomorrow today' "" ) )
    elif [ "$prev" == "--fmt" ]; then
        COMPREPLY=( $( compgen -W '"%Y-%m-%d-%H-%M" "%Y-%m-%d" "%H:%M" now tomorrow today' "$cur" ) )
    elif [ "$cur" == "-fmt" ]; then
        COMPREPLY=( $( compgen -W '"%Y-%m-%d-%H-%M" "%Y-%m-%d" "%H:%M" now tomorrow today' "" ) )
    else
        COMPREPLY=( $( compgen -W "-h -t -f --help --inputTime --fmt" "'$cur'" ) )
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
        "Todo") todoAutoComplete "$cur" "$prev" ;;
        "TimeUtils") timeUtilsComplete "$cur" "$prev" ;;
        *) COMPREPLY=( $( compgen -W "TimeUtils Tasks Todo CredsManager Work" "$cur" ) ) ;;
    esac
    return 0
}

complete -F utilsComplete -o filenames UtilsApp
