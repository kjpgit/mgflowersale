import os
import sys
import subprocess

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
    f = item.image_file
    if not os.path.exists(f):
        err("not found: %s" % f)
    else:
        info = get_info(f)
        print info["File size"], info["Format"], \
                info["Height"], info['Width'], info['name']
        total_size += float(info["File size"].split()[0])

sys.stderr.write("total file size: %s\n" % total_size)

