#!/usr/bin/env bash
#
# Perform some verification on the broken link checker.
# NB: The purpose of this script is
# to verify the working of the checker on a real web server.

HOST=localhost
PORT=8080
counter=5

start_server() {
    # We start the web server
    $PYTHON tests/server.py $HOST $PORT &
    # We get his pid
    server_pid=$!

    # We wait the server to start
    while [ $counter -gt 0 ]; do
        sleep .1
        if curl -I $HOST:$PORT -s --show-error; then
            break
        else
            echo Retry\($counter\)
            counter=$(expr $counter - 1)
        fi
    done

    # We verify if the server is run
    if [ $counter -eq 0 ]; then
        return 1
    fi
}

# We start the test
start_test() {
    report=$($PYTHON -m broken_link_checker http://$HOST:$PORT -D -d 0 $BLC_FLAGS)
    nb_broken_link_got=$(expr $(echo "$report" | grep -c .) - 2)
    if [ ! $nb_broken_link_got -eq $NB_BROKEN_LINK_EXPECTED ]; then
        echo "$NB_BROKEN_LINK_EXPECTED broken links expected, but $nb_broken_link_got got"
        echo "REPORT:"
        echo "$report"
        return 2
    fi
}

# We stop the server
stop_server() {
    kill $server_pid
}

if start_server; then
    start_test
else
    exit 1
fi

err_code=$?

stop_server

exit $err_code