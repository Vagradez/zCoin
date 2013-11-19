import socket
import json
import config
import random
import sqlite3
import base64
import hashlib

def get_nodes(obj, data):
    with open("nodes.db", 'rb') as file:
        while True:
            x = file.read(100)
            if not x:
                break
            md5sum = hashlib.md5(x).hexdigest()
            out = base64.b64encode(x)
            x = json.dumps({"md5sum":md5sum, "data":out})
            obj.send(x)

def get_nodes_send(god=False):
    node = sqlite3.connect("nodes.db")
    cmd = {"cmd":"get_nodes"}
    nodes = node.execute("SELECT ip, port FROM data WHERE relay=?", [True])
    if not nodes:
        return
    nodes = nodes.fetchall()
    if god:
        nodes = config.brokers
    random.shuffle(nodes)
    for x in nodes:
        
        s = socket.socket()
        try:
            s.settimeout(1)
            s.connect((x[0], x[1]))
        except:
            s.close()
            continue
        else:
            s.send(json.dumps(cmd))
            out = ""
            current = ""
            while True:
                try:
                    data = s.recv(1)
                except:
                    pass
                if data:
                    current = current + data
                    if data != "}":
                        continue
                    try:
                        data = json.loads(current)
                    except ValueError:
                        break
                    else:
                        current = ""
                        check = base64.b64decode(data['data'])
                        if hashlib.md5(check).hexdigest() == data['md5sum']:
                            out = out + check
                        else:
                            break
                else:
                    break
            
            with open("nodes.db", 'wb') as file:
                file.write(out)
