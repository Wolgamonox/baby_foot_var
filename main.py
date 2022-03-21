import getopt
import sys

from core.gui import Gui


def main(argv):
    nb_camera = 1

    try:
        opts, args = getopt.getopt(argv, "hc:", "nb_cam=")
    except getopt.GetoptError:
        print('Usage: main.py -c <number_of_camera [1-3]>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('Usage: main.py -c <number_of_camera [1-3]>')
            sys.exit()

        elif opt in ("-c", "--nb_cam"):
            nb_camera = int(arg)

    gui = Gui(nb_camera)
    gui.run()


if __name__ == "__main__":
    main(sys.argv[1:])
