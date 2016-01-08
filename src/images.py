#!/usr/bin/python
import os
import sys
import subprocess
import shutil

import sale


def err(s):
    sys.stderr.write(s + "\n")
    #sys.exit(1)


def get_info(f):
    p = subprocess.Popen(["mediainfo", f], stdout=subprocess.PIPE)
    stdout, stderr = p.communicate()
    rc = p.wait()
    assert rc == 0
    ret = {}
    lines = stdout.split("\n")
    for line in lines:
        if not line.strip():
            continue
        if ":" not in line:
            continue
        parts = line.split(":", 1)
        key = parts[0].strip()
        value = parts[1].strip()
        if key in ("Format", "Width", "Height", "File size"):
            ret[key] = value
    ret["name"] = f
    return ret


sale.load_data()
total_size = 0
for item in sale.g_items:
    dest = item.image_file
    src = dest.replace("thumbs/", "images/")
    if not os.path.exists(src):
        err("not found: %s" % src)
    else:
        info = get_info(src)
        print info["File size"], info["Format"], \
                info["Height"], info['Width'], info['name']
        total_size += float(info["File size"].split()[0])
        shutil.copy(src, dest)

sys.stderr.write("total file size: %s\n" % total_size)
