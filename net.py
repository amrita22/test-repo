import numpy as np
import numpy.matlib
import re
from upward import in_upward, update_upward, merge_upward
import json
from scipy.sparse import lil_matrix, csr_matrix

num_places = 20
num_transitions = 20
pre_matrix = np.matlib.zeros((num_places, num_transitions),
                                    dtype=np.int8)

post_matrix = np.matlib.zeros((num_places, num_transitions),
                                    dtype=np.int8)

def num_places(self):
    return self.pre_matrix.shape[0]

def num_transitions(self):
    return self.pre_matrix.shape[1]

def get_pre(self, place, transition):
    return self.pre_matrix[place, transition].item()

def get_post(self, place, transition):
    return self.post_matrix[place, transition].item()

def set_pre(self, place, transition, value):
    self.pre_matrix[place, transition] = value

def set_post(self, place, transition, value):
    self.post_matrix[place, transition] = value

def pred(self, marking):
    succ = set()

    for t in range(self.num_transitions()):
        if self.fireable(marking, t, reverse=True):
            succ.add(self.fire(marking, t, reverse=True))

    return succ

def pred_upward(self, marking):
    pred = set()

    for t in range(self.num_transitions()):
        pre_marking = [0] * self.num_places()

        for p in range(self.num_places()):
            pre, post = self.get_pre(p, t), self.get_post(p, t)
            pre_marking[p] = max(pre, marking[p]+pre-post)

            #Upward.update(pred, Marking(pre_marking))

    return pred

def add_transition_from_protocol(petrinet, places_index, num_transitions, protocol, true_states, targets):
    pre_matrix, post_matrix = petrinet
    for transition in range (0, num_transitions):
        pre_places = protocol[transition]["pre"]
        post_places = protocol[transition]["post"]
        pre_flag_true = True
        post_flag_true = False

        pre_flag_false = True
        post_flag_false = False

        for pre_place in pre_places:
            pre_matrix[places_index[pre_place], transition] += 1
            if pre_place not in true_states:
                pre_flag_true = False
            if pre_place in true_states:
                pre_flag_false = False

        for post_place in post_places:
            post_matrix[places_index[post_place], transition] += 1
            if pre_flag_true is True and post_place not in true_states:
                post_flag_true = True
            elif pre_flag_false is True and post_place in true_states:
                post_flag_false = True

        if (pre_flag_true is True and post_flag_true is True) or (pre_flag_false is True and post_flag_false is True):
            data_file = open('targets.spec', 'a')
            target_inst = []
            for place in pre_matrix[:, transition]:
                data_file.write(str(place.item()))
                data_file.write(',')
                target_inst.append(('>=', place.item()))
            data_file.write('\n')
            data_file.close()
            targets.append(target_inst)

def add_transition(petrinet, places, transition, rule):
    pre_matrix, post_matrix = petrinet
    pos = rule.find('->')
    guards_str = rule[:pos]
    updates_str = rule[pos + 2:]
    guards = {}
    updates = {}

    # Parse guards
    for guard in guards_str.split(','):
        var, value = guard.split('>=')

        guards[var.strip()] = int(value)

    # Parse updates
    for update in updates_str.split(','):
        match = re.search('\s*(.*)\'\s*=\s*(.*)\s*(\+|-)\s*(.*)\s*',
                          update)  # xi' = xj {+,-} value

        if match is not None:
            var_in = match.group(1).strip()
            var_out = match.group(2).strip()
            value = int(match.group(3) + match.group(4))

            if var_in != var_out:
                raise ValueError('x_i\' = x_j + c illegal with i != j')

            updates[var_in] = value

    # Add transition
    for p in range(len(places)):
        guard = guards[places[p]] if places[p] in guards  else 0
        update = updates[places[p]] if places[p] in updates else 0

        if update >= 0:
            pre, post = guard, guard + update
        elif update < 0:
            pre, post = max(guard, -update), max(0, guard + update)

        # Add value to sparse matrix if necessary
        if pre != 0:
            pre_matrix[p, transition] = pre

        if post != 0:
            post_matrix[p, transition] = post

def add_transition(petrinet, places, transition, rule):
    pre_matrix, post_matrix = petrinet
    pos = rule.find('->')
    guards_str = rule[:pos]
    updates_str = rule[pos + 2:]
    guards = {}
    updates = {}

    # Parse guards
    for guard in guards_str.split(','):
        var, value = guard.split('>=')

        guards[var.strip()] = int(value)

    # Parse updates
    for update in updates_str.split(','):
        match = re.search('\s*(.*)\'\s*=\s*(.*)\s*(\+|-)\s*(.*)\s*',
                          update)  # xi' = xj {+,-} value

        if match is not None:
            var_in = match.group(1).strip()
            var_out = match.group(2).strip()
            value = int(match.group(3) + match.group(4))

            if var_in != var_out:
                raise ValueError('x_i\' = x_j + c illegal with i != j')

            updates[var_in] = value

    # Add transition
    for p in range(len(places)):
        guard = guards[places[p]] if places[p] in guards  else 0
        update = updates[places[p]] if places[p] in updates else 0

        if update >= 0:
            pre, post = guard, guard + update
        elif update < 0:
            pre, post = max(guard, -update), max(0, guard + update)

        # Add value to sparse matrix if necessary
        if pre != 0:
            pre_matrix[p, transition] = pre

        if post != 0:
            post_matrix[p, transition] = post

def constrained_vector(constraint):
    return [value for (_, value) in constraint]


def add_constraints(data, places_indices, constraints_list):
    COMPARISONS = ['>=', '=']  # List order matters here.
    entries = data.split(',')

    # Parse constraints
    for rule in entries:
        for comparison in COMPARISONS:
            if comparison in rule:
                place, value = rule.strip().split(comparison)
                place = place.strip()
                value = int(value)

                constraints_list[places_indices[place]] = (comparison,
                                                           value)

                break  # Important, '=' appears in '>=' so would parse twice

    # Return trailing incomplete constraint
    if len([comp for comp in COMPARISONS if comp in entries[-1]]) == 0:
        return entries[-1]
    else:
        return ''

def load_petrinet_from_population_protocol(filename):
    input_file = open(filename)
    for row in input_file:
        data = row.strip()
    params = json.loads(data)
    print(params)

    places = []
    init = []
    targets = []

    pre_matrix, post_matrix = None, None
    places_indices = []
    num_transitions = params["protocol"]["transitions"].__len__()
    num_places = params["protocol"]["states"].__len__()
    places = params["protocol"]["states"]
    true_states = params["protocol"]["trueStates"]
    curr_transition = 0

    print params["protocol"]["trueStates"].__len__()
    print params["protocol"]["states"].__len__()

    pre_matrix = np.matlib.zeros((len(places),
                                  num_transitions),
                                 dtype=np.int8)
    post_matrix = np.matlib.zeros((len(places),
                                   num_transitions),
                                  dtype=np.int8)

    initial_states = params["protocol"]["initialStates"]
    for state in places:
        if state in initial_states:
            init.append(('>=', 3))
        else:
            init.append(('>=', 0))

    places_indices = {value: key for key, value in
                      enumerate(places)}

    for state1 in true_states:
        for state2 in places:
            if state2 not in true_states:
                target_mismatch = [('>=', 0)] * len(places)
                target_mismatch[places_indices[state1]] = ('>=', 1)
                target_mismatch[places_indices[state2]] = ('>=', 1)
                targets.append(target_mismatch)

    add_transition_from_protocol((pre_matrix, post_matrix), places_indices, num_transitions, params["protocol"]["transitions"], true_states, targets)

    #print((pre_matrix, post_matrix))
    print targets.__len__()
    return ((pre_matrix, post_matrix), init, targets)

def load_petrinet(filename):
    MODES = ['vars', 'rules', 'init', 'target', 'invariants']

    places = []
    init = []
    targets = []

    pre_matrix, post_matrix = None, None
    places_indices = []
    num_transitions = 0

    # Precompute number of transitions
    with open(filename) as input_file:
        for row in input_file:
            if ';' in row:
                num_transitions += 1

    # Load data
    with open(filename) as input_file:
        mode = 'none'
        rules_acc = ''
        acc = ''
        curr_transition = 0

        for row in input_file:
            data = row.strip()

            # Ignore empty/commented lines
            if len(data) == 0 or data[0] == '#':
                continue

            # Mode detection
            if data in MODES:
                mode = data

                # Allocate matrix for the Petri net, and places
                if mode == MODES[1]:

                    pre_matrix = np.matlib.zeros((len(places),
                                              num_transitions),
                                             dtype=np.int8)
                    post_matrix = np.matlib.zeros((len(places),
                                               num_transitions),
                                              dtype=np.int8)
                    init = [('>=', 0)] * len(places)
                    places_indices = {value: key for key, value in
                                      enumerate(places)}
            else:
                # Places
                if mode == MODES[0]:
                    places.extend(data.split(' '))
                # Rules
                elif mode == MODES[1]:
                    rules_acc += data
                    pos = rules_acc.find(';')

                    if pos >= 0:
                        add_transition((pre_matrix, post_matrix),
                                       places, curr_transition,
                                       rules_acc[:pos])
                        curr_transition += 1
                        rules_acc = rules_acc[pos + 1:]
                # Initial values
                elif mode == MODES[2]:
                    acc = add_constraints(acc + data, places_indices, init)
                # Target values
                elif mode == MODES[3]:
                    new_target = [('>=', 0)] * len(places)
                    trailing = add_constraints(data, places_indices,
                                               new_target)
                    targets.append(new_target)

                    if len(trailing.strip()) > 0:
                        raise ValueError('Incomplete target constraint.')
                        # # Invariants (not supported)
                        # #elif mode == MODES[4]:
                        # #

    # Finish rules parsing (if necessary)
    while True:
        pos = rules_acc.find(';')

        if pos >= 0:
            add_transition((pre_matrix, post_matrix), places,
                           curr_transition, rules_acc[:pos])
            curr_transition += 1
            rules_acc = rules_acc[pos + 1:]
        else:
            break

    return ((pre_matrix, post_matrix), init, targets)


def pre_upward(petrinet, markings, precomputed=None):
    # pre_matrix, post_matrix = petrinet
    # num_places, num_transitions = pre_matrix.shape
    # basis = set()
    #
    # for m in markings:
    #     if precomputed is not None and m in precomputed:
    #         to_merge = {pre_m for pre_m in precomputed[m] if not
    #         in_upward(pre_m, markings)}
    #         merge_upward(basis, to_merge)
    #         continue
    #     else:
    #         precomputed[m] = set()
    #
    #     for t in range(num_transitions):
    #         pre_m = [0] * num_places
    #
    #         for p in range(num_places):
    #             pre, post = int(pre_matrix[p, t]), int(post_matrix[p, t])
    #             pre_m[p] = max(pre, m[p] + pre - post)
    #
    #         pre_m = tuple(pre_m)
    #
    #         if precomputed is not None:
    #             update_upward(precomputed[m], pre_m)
    #
    #         if not in_upward(pre_m, markings):
    #             update_upward(basis, pre_m)
    #
    # return basis
    pre_matrix, post_matrix = petrinet
    num_places, num_transitions = pre_matrix.shape
    basis = set()

    for m in markings:
        if precomputed is not None and m in precomputed:
            to_merge = {pre_m for pre_m in precomputed[m] if not
            in_upward(pre_m, markings)}
            merge_upward(basis, to_merge)
            continue
        else:
            precomputed[m] = set()

        for t in range(num_transitions):
            pre_m = [0] * num_places

            for p in range(num_places):
                pre, post = int(pre_matrix[p, t]), int(post_matrix[p, t])
                pre_m[p] = max(pre, m[p] + pre - post)

            pre_m = tuple(pre_m)

            if precomputed is not None:
                update_upward(precomputed[m], pre_m)

            if not in_upward(pre_m, markings):
                update_upward(basis, pre_m)

    return basis

def backward_algorithm(petrinet, init, targets):

    post_matrix, pre_matrix = petrinet
    # for this, we construct the reverse net and try to obtain the initial marking from the final one.
    # the reverse petri net is just the pre and post matrix reversed.
    #Step 1 : reverse matrix
    #Step 2 : Start from the final marking (target) and compute the marking required to fire all transitions.
    #Step 3 : Pick the minimum of that and the rest and recurse until no new ones are found.
    M = []
    #M.append(targets)
    init_marking = [x[1] for x in init]
    basis = {tuple(constrained_vector(m)) for m in targets}
    precomputed = {}
    covered = False
    #num_iter = 0

    while not covered:

        def sum_norm(v):
            return sum(v)

        def smallest_elems(x):
            return set(sorted(x, key=sum_norm)[:int(10 + 0.2 * len(x))])
        # Compute prebasis
        prebasis = pre_upward(petrinet, basis, precomputed)

        # Continue?
        if len(prebasis) == 0:
            break
        else:
            prebasis = smallest_elems(prebasis)
            merge_upward(basis, prebasis)
            covered = in_upward(init_marking, basis)

    return (covered, basis)
#     targetset=[]
#     for x in range (0, targets.__len__()):
#         targetset = targets[x]
#         marking = [x[1] for x in init]
#         M.append(marking)
#         while upward_is_not(init_marking, M):
#             B = compute_pb(M, petrinet)
#             if B.equals(upward(M)):
#                 return False
#             else:
#                 M = minbase(M, B)
#             return True
#
# def upward_is_not(m, M):
#     for marking in M:
#         for i in range(1,m.__len__()):
#             if m[i]>marking[i]:
#                 break
#         return False
#     return True
#
# def compute_pb(M, petrinet):











