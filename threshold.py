# -*- coding: utf-8 -*-
params = {
  "scheme": {
    "minCoeff": {
      "descr":  "Min. coeff. a",
      "values": range(-30, 31),
      "value":  -1
    },

    "maxCoeff": {
      "descr":  "Max. coeff. b",
      "values": range(-30, 31),
      "value":  1
    },

    "threshold": {
      "descr":  "Threshold c",
      "values": range(1, 101),
      "value":  2
    }
  }
}

def generateProtocol(params):
  a = params["scheme"]["minCoeff"]["value"]
  b = params["scheme"]["maxCoeff"]["value"]
  c = params["scheme"]["threshold"]["value"]
  s = max(abs(a), abs(b), abs(c) + 1)

  # Helper functions

  def is_leader(q):
    return (q[0] == 1)

  def output(q):
    return (q[1] == 1)

  def value(q):
    return q[2]

  def f(m, n):
    return max(-s, min(s, m + n))

  def g(m, n):
    return m + n - f(m, n)

  def o(m, n):
    return 1 if f(m, n) < c else 0

  # Generate states
  states = [(x, y, u) for u in range(-s, s + 1)
                          for x in [0, 1] for y in [0, 1]]

  # Generate transitions
  transitions = []

  for i in range(len(states)):
    for j in range(i, len(states)):
      p = states[i]
      q = states[j]

      if is_leader(p) or is_leader(q):
        m = value(p)
        n = value(q)
        pre  = (p, q)
        post = ((1, o(m, n), f(m, n)), (0, o(m, n), g(m, n)))
        t = Utils.transition(pre, post)

        if (not Utils.silent(pre, post) and t not in transitions):
          transitions.append(t)

  # Generate initial states
  initial_states = [q for q in states if is_leader(q) and
                                                value(q) >= a and value(q) <= b and
                                                 output(q) == (value(q) < c)]

  # Generate true states
  true_states = [q for q in states if output(q)]

  # Generate predicate
  expr = ["{}*C[{}]".format(value(q), q) for q in initial_states]
  predicate = "{} < {}".format(" + ".join(expr), c)

  # Generate description
  description = """This protocol evaluates the linear inequality
                   a·x_a + ... + b·x_b < c. Each state of the protocol
                   is of the form (l, o, v) where l is a bit indicating
                   whether the agent is active, o is the output of the
                   agent, and v is an integer indicating the value of
                   the agent. Described in Dana Angluin,
                   James Aspnes, Zoë Diamadi, Michael J. Fischer and
                   René Peralta. Computation in Networks of Passively
                   Mobile Finite-State Sensors. PODC 2004."""

  # Generate style
  style = {q: {} for q in states}

  for q in states:
    scale = (value(q) * 0.5 / s) + 0.5

    style[q]["size"] = 1.0 if is_leader(q) else 0.5

    if output(q):
      style[q]["color"] = "rgb({}, {}, {})".format(63, int(81 + 200 * (1 - scale)),
                                                       int(100 + 81 * scale))
    else:
      style[q]["color"] = "rgb({}, {}, {})".format(int(105 + 128 * scale),
                                                   int(30 + 180 * (1 - scale)), 99)

  return {
    "title":         "Threshold protocol",
    "states":        states,
    "transitions":   transitions,
    "initialStates": initial_states,
    "trueStates":    true_states,
    "predicate":     predicate,
    "description":   description,
    "statesStyle":   style
  }
