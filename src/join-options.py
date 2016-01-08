#!/usr/bin/python

# Join all input lines with ;
# Used when merging multiple rows to a single cell
import sys
lines = sys.stdin.readlines()
lines = [x.strip() for x in lines]
print "; ".join(lines)
