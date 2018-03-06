# -*- coding: utf-8 -*-
params = {
  "scheme": {
    "remainder": {
      "descr":  "Remainder c",
      "values": range(0, 101),
      "value":  1
    },

    "modulo": {
      "descr":  "Modulo m",
      "values": range(2, 101),
      "value":  2
    }
  }
}

def generateProtocol(params):
  c = params["scheme"]["remainder"]["value"]
  m = params["scheme"]["modulo"]["value"]

  # Helper functions
  def label(q):
    if q is True:
      return "y";
    elif q is False:
      return "f";
    else:
      return q

  # Generate states
  numeric = range(m)
  boolean = [False, True]
  states  = numeric + boolean

  # Generate transitions
  transitions = []

  for i in range(len(numeric)):
    p = numeric[i]

    for j in range(i, len(numeric)):
      q    = numeric[j]
      pre  = map(label, (p, q))
      post = map(label, ((p + q) % m, ((p + q) % m) == (c % m)))

      if not Utils.silent(pre, post):
        transitions.append(Utils.transition(pre, post))

    for j in boolean:
      q    = boolean[j]
      pre  = map(label, (p, q))
      post = map(label, (p, p == (c % m)))

      if not Utils.silent(pre, post):
        transitions.append(Utils.transition(pre, post))

  # Generate predicate
  expr = ["{0}*C[{0}]".format(q) for q in numeric]
  predicate = "{} %=_{} {}".format(" + ".join(expr), m, c)

  # Generate style
  style = {label(q): {} for q in states}

  for q in numeric:
    style[label(q)]["size"] = 0.5 + 0.5 * q / (m - 1)

  style[label(True)]["size"]   = 0.5
  style[label(False)]["size"]  = 0.5
  style[label(True)]["color"]  = "blue"
  style[label(False)]["color"] = "red"

  return {
    "title":         "Remainder protocol",
    "states":        map(label, states),
    "transitions":   transitions,
    "initialStates": map(label, numeric),
    "trueStates":    map(label, [c % m, True]),
    "predicate":     predicate,
    "description":   """This protocol tests whether
                        0·C[0] + 1·C[1] + ... + (m-1)·C[m-1] ≡ c (mod m).""",
    "statesStyle": style
  }
