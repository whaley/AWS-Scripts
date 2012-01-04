#!/bin/bash
BASE_DIRECTORY=$HOME/.ec2/

function outputChoices {
    local count=0
    for directory in ${directories[@]}
    do
        echo -e "$count:\t$(basename $directory)"
        ((count++))
    done

    echo -n "Select one of [0-$numberOfDirectories] - " \
        "any other input leaves creds unchanged:  "
}

function changeCredDirectory {
    if [[ -n $(echo -n $inputChoice | grep '^[0-9][0-9]*$')  && $inputChoice \
        -ge 0 && $inputChoice -le $numberOfDirectories ]]
    then
        newCredDirectory=${directories[$inputChoice]} 
        ln -nsf $newCredDirectory $BASE_DIRECTORY/current
        echo; echo "Credentials set to $newCredDirectory"
    else
        echo ;echo "Invalid selection - creds unchanged"
    fi
}

function setEnv {
    export AWS_ACCESS_KEY_ID="$(cat $HOME/.ec2/current/access_key)"
    export AWS_SECRET_ACCESS_KEY="$(cat $HOME/.ec2/current/secret_key)"
    export EC2_PRIVATE_KEY="$(/bin/ls $HOME/.ec2/current/pk-*.pem)"
    export EC2_CERT="$(/bin/ls $HOME/.ec2/cert-*.pem)"
}

directories=($(find $BASE_DIRECTORY -type d -maxdepth 1 -mindepth 1))
numberOfDirectories=$(( ${#directories[@]} - 1 ))

outputChoices
read inputChoice
changeCredDirectory 
setEnv
