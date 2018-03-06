#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json

class Utils:
    @staticmethod
    def transition(pre, post):
        return {
            "name": "{}, {} -> {}, {}".format(pre[0], pre[1], post[0], post[1]),
            "pre":  [pre[0],  pre[1]],
            "post": [post[0], post[1]]
        }

    @staticmethod
    def silent(pre, post):
        return ((pre[0] == post[0] and pre[1] == post[1]) or
                (pre[0] == post[1] and pre[1] == post[0]))

n = len(sys.argv)

if (n != 2 and n != 3):
    print("Usage: program [file path] [param dict]")
else:
    script = sys.argv[1]
    execfile(script)

    if (n == 3):
        params = json.loads(sys.argv[2])
        protocol = generateProtocol(params)

        # Convert states to strings
        for p in ["states", "initialStates", "trueStates"]:
          protocol[p] = map(str, protocol[p])

        for i in range(len(protocol["transitions"])):
          for p in ["pre", "post"]:
           protocol["transitions"][i][p] = map(str, protocol["transitions"][i][p])

        if "statesStyle" in protocol:
          style = protocol["statesStyle"]
          protocol["statesStyle"] = {str(p): style[p] for p in style}

        print(json.dumps({"protocol": protocol}))
        file = open("protocol_net.spec", "w")
        file.write(json.dumps({"protocol": protocol}))
        file.close()
    else:
        try:
            params
        except NameError:
            params = {}

        print(json.dumps(params))
