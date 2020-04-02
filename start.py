import sys
import json
import os

if __name__ == "__main__":
    conf = None
    try:
        f = open('keys.txt', 'r')
        item = f.read()
        f.close()
        conf = json.loads(item)
    except:
        print("Failed to load configuration file. Please run setup.py")
        sys.exit(1)

    for item in conf.keys():
        os.environ[item] = conf[item]

    import JDRD
    JDRD.main()
        