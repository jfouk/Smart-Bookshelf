#! /bin/bash
while read x; do
    echo -n $(date);
    echo $x;
done
