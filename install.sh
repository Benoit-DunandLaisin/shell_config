#!/bin/sh

echo "Installing configuration"
cd conf
ls -A1 | while read fic
do
    source="`pwd`/`basename ${fic}`"
    target="${HOME}/"`basename ${fic}`
    if [ -f "${target}" ]
    then
        echo "Make a backup of ${target} and replace it"
        mv "${target}" "${target}.bak"
        ln -s "${source}" "${target}"
    else
        if [ ! -e "${target}" ]
        then
            echo "Installing ${target}"
            ln -s "${source}" "${target}"
        fi
    fi
done
echo "All is done"
