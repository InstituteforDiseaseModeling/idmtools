#!/bin/bash

chmod +x run_simulation.sh






    find $(pwd) -maxdepth 2 -name "_run.sh" -print0 | xargs -0 -I% dirname % | xargs -d "\n" -P 4 -I% bash -c 'cd $(pwd) && $(pwd)/run_simulation.sh %  1>> stdout.txt 2>> stderr.txt'
