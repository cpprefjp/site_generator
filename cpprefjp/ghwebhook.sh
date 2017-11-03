#!/bin/bash

set -e

su - melpon -c "
set -e
cd site_generator
cpprefjp/ghwebhook_on_user.sh \"$@\"
"
