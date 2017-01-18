import os, errno
import sys
import argparse

CALL = "call"
DEL = "del"

class InstanceGenerator(object):

    def __init__(self, folder, floors, elevators, reqs):
        """
        This constructor can be used when its not being called with command line arguments.

        :param folder: folder where the instance will be created. Pass "." to create in the same folder.
        :param floors: floor amount in the instance
        :param elevators: Elevator starting positions. Should be a list of ints.
        :param reqs: list of strings where each string is formatted as a request. They have the form: call,D,F or del,E,F
                     where D is either "up" or "down", E an int that represents the elevator id and F the floor destination.
        """

        # elevators is a list of floors of where each elevator starts
        # reqs is
        self.floors = floors
        self.elevators = elevators
        self.reqs = reqs

        self.folder = folder

    def __init__(self, arguments):
        """
        This constructor is used for command line arguments. Type -h for info.
        :param arguments: list of arguments as passed in the command line. If using sys.argv pass "sys.argv[:1]"
        """
        args = self.parseArgs(arguments)

        if args.prompt:
            self.prompt(args.folder)

        else:
            self.folder = args.folder

            if args.floors is None:
                print "Floor amount must be specified with the -f parameter!"
                return
            self.floors = args.floors

            if args.elevatorstarts is None and args.eAmt is None:
                print "Either the starting position of the elevator or the amount of elevators must be specified using -s or -e"
            if args.eAmt is not None:
                self.elevators = [ 1 for i in range(args.eAmt)]

            elif args.elevatorstarts is not None:
                self.elevators = args.elevatorstarts

            if args.requests is not None:
                self.reqs = [ r.split(",") for r in args.requests ]
                self.testRequests()
            else:
                self.reqs = []



    def parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Creates an instance for an elevator domain. It either prompts for the details or takes them in as arguments. " \
                                                     "Aside from creating the atoms it creates #const variables for the floor amount, agent amount and req amount.")

        parser.add_argument("-p", "--prompt", action="store_true",
                            help="prompt for the details instead of giving them with cmd arguments.")
        parser.add_argument("-f", "--floors", type=int, help="Amount of floors.")

        group = parser.add_mutually_exclusive_group()
        group.add_argument("-e", "--eAmt", type=int, help="Amount of elevators.")
        group.add_argument("-s", "--elevatorstarts", type=int, nargs="+",
                            help="Elevator starting positions.")

        parser.add_argument("-r", "--requests", nargs="+",
                            help="Requests with the form: call,D,F or del,E,F with D = up | down,  E = elevator number and F = target floor.")
        parser.add_argument("-o", "--folder", default=".")

        return parser.parse_args(args)

    def prompt(self, folder = "."):
        self.folder = folder

        self.promptFloors()
        self.promptElevator()
        self.promptRequests()

    def promptFloors(self):
        try:
            self.floors = int(raw_input("Enter the amount of floors: "))
        except ValueError:
            print "ERROR : Floor amount must be an integer!\nExiting..."
            sys.exit()

    def promptElevator(self):
        try:
            elevAmt = int(raw_input("Enter the amount of elevators: ").strip())
        except ValueError:
            print "ERROR : Elevator amount must be an integer!\nExiting..."
            sys.exit()

        elevators = raw_input("Enter the starting positions of the elevators(separate with commas): ").split(",")
        if len(elevators) != elevAmt:
            print "ERROR : There must be exactly one starting position for every elevator.\nExiting..."
            sys.exit()

        try:
            self.elevators = [int(n, 10) for n in elevators]
        except ValueError:
            print "ERROR : Elevator starting positions must be integers!\nExiting..."
            sys.exit()

    def promptRequests(self):
        self.reqs = raw_input("Enter requests(e.g. call,up,4 ; del,3,1): ").split(";")
        self.reqs = [ r.strip().split(",") for r in self.reqs ]

        #               this is what the var has if the input is empty, if the input has spaces, the strip() in the second parsing step deletes them
        if self.reqs != [[""]]:
            self.testRequests()

    def testRequests(self):

        #test the requests
        for req in self.reqs:
            # test for presence of arguments
            if len(req) != 3:
                print "Error in " + str(req) + "Requests must have 3 arguments separated by a comma!"

            # test for the up and down in second part of call request
            if req[0] == CALL:
                if req[1] != "up" and req[1] != "down":
                    print "Error in call request: " + req[0]+"," + req[1]+"," + req[2] + " .Call request must have \"up\" or \"down\" after the first comma.\nExiting..."
                    sys.exit()

            # test for integer in second part of deliver request
            elif req[0] == "del":
                try:
                    int(req[1])
                except ValueError:
                    print "Error in deliver request: " + req[0]+"," + req[1]+"," + req[2] + " .Deliver request must have an interger after the first comma.\nExiting..."
                    sys.exit()

            else:
                print "Error in " + req[0]+"," + req[1]+"," + req[2] + "! Requests must be either \"call\" or \"del\" \nExiting..."
                sys.exit()

            #test last argument of requests
            try:
                int(req[2])
            except ValueError:
                print "Error in " + req[0]+"," + req[1]+"," + req[2] + "! Requests must have an integer as last argument!\nExiting..."
                sys.exit()

    def createFolder(self, path):
        """
        from http://stackoverflow.com/posts/5032238/revisions

        :param path: folder to be created
        """
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def writeInstance(self):
        """
        Writes the instance into a file.

        :return file name
        """
        outFile = "instance{f}_{epos}".format(f = self.floors, epos = tuple(self.elevators))


        self.createFolder(self.folder)

        if os.name == "posix" and self.folder != "":
            # posix is the same for mac and linux
            self.folder = self.folder + "/"
        elif self.folder != "":
            self.folder = self.folder + "\\"


        outname = self.folder + outFile + ".lp"

        with open(outname, "w") as out:

            out.write("#program base.\n")
            out.write("\n")
            out.write("#const floors = {f}.\n".format(f = self.floors))
            out.write("floor(1..floors).\n")
            out.write("\n")

            out.write("#const agents = {a}.\n".format(a = len(self.elevators)))
            out.write("agent(elevator(1..agents)).\n")
            out.write("\n")

            for i in range(1, len(self.elevators)+1):
                num = i
                value = self.elevators[i - 1]
                out.write("#const start{id} = {val}.\n".format(id = num, val = value))
                out.write("init(at(elevator({id}), {val})).\n".format(id = num, val = value))


            out.write("\n")
            out.write("\n")

            out.write("#const startingReqs={}.\n\n".format(len(self.reqs)))

            for r in self.reqs:
                if r[0] == "call":
                    out.write("init(request(call({}),{})).\n".format(r[1], r[2]))
                if r[0] == "del" or r[0] == "deliver":
                    out.write("init(request(deliver({}),{})).\n".format(r[1], r[2]))

        return outFile

def main():

    g = InstanceGenerator(sys.argv[1:])
    g.writeInstance()

if __name__ == "__main__":
    main()
