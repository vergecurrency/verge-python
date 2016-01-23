#!/bin/bash
git --no-pager log --no-merges --format="%ai %aN %n%n%x09* %s%d%n"
