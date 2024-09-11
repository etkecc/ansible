#!/bin/sh

path=$1
max_iterations=${2:-0}

counter=0
while ! [ -f $path ]; do
		let counter=counter+1

		if [ "$max_iterations" -gt "0" ]; then
				if [ "$counter" -gt "$max_iterations" ]; then
						echo "Giving up waiting for $path after $max_iterations iterations"
						exit 1
				fi
		fi

		if [ "$max_iterations" -gt "0" ]; then
			echo "$path is missing.. Waiting ($counter/$max_iterations)..."
		else
			echo "$path is missing.. Waiting ($counter/inf.)..."
		fi

		sleep 1
done
