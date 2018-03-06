import argparse
from net import load_petrinet, load_petrinet_from_population_protocol
from net import backward_algorithm
#from coverability import coverability


def main(path):
    #petrinet, init, targets = load_petrinet(path)

    petrinet, init, targets = load_petrinet_from_population_protocol(path)
    print targets.__len__()
    # init = []
    # init_file = open("init.spec")
    # for row in init_file:
    #     data = row.strip()
    #     init.append(('=', data))
    # init_file.close()
    #
    # targets = []
    # targets_file = open("targets.spec")
    # for targ_row in targets_file:
    #     target_inst = []
    #     target_data = targ_row.strip()
    #     marking = target_data.split(',')
    #     for place in marking:
    #         if place is not '':
    #             target_inst.append((">=", int(place)))
    #     targets.append(target_inst)
    # targets_file.close()
    #
    result, basis = backward_algorithm(petrinet, init, targets)
    print basis.__len__()
    #
    # target_set = [y[0] for y in targets]
    # target_marking = [z[1] for z in target_set]
    #
    # result = False
    # if result is None:
    #     print 'Unknown'
    # elif result:
    #     print 'Unsafe'
    # else:
    #     print 'Safe'


# Entry point
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Performs coverability safety verification.')

    parser.add_argument('path', metavar='Filename', type=str,
                        help='File (.spec) to verify.')

    args = parser.parse_args()

    main(args.path)