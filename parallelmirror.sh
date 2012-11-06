#!/bin/bash

PYTHON=`which python`
if [ "x$VIRTUAL_ENV" == "x" ]; then
    PYTHON=$HOME/virt/bin/python
fi

children=""
kill_children () {
    kill $children
    echo "Sent SIGTERM to children: $children"
    wait $children
}
trap kill_children SIGINT SIGTERM

for state in `$PYTHON manage.py knownstates`; do
    ($PYTHON manage.py mirrorstate --loglevel=notice --output=$state.log --forever $state) &
    children="$children $!"
done
wait

