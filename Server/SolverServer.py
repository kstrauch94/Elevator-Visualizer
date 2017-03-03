import SocketServer
import argparse
import json

import EncodingManager
import SolverConfig
from ServerConfig import *


class SolverHandler(SocketServer.StreamRequestHandler):

    def __init__(self, request, client_address, server):
        self.replyFunction = {SOLVE : self.solve, BASE : self.sendBase, ADDREQS : self.addRequest, RESET : self.reset,
                              ENCODING: self.setEncoding}

        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)


    def handle(self):

        reply = self.rfile.readline().strip()
        print "Message received: " + reply

        if reply in self.replyFunction:
            self.replyFunction[reply]()
        else:
            msg = "Received Message : " + reply + " is not a valid request.\n" + DONE + "\n"
            self.request.sendall(msg)

        print "Finishing connection..."
        print " ---------------------------------------"
        print " |-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|"
        print " ---------------------------------------"

    def receive(self):
        reply = ""
        while 1:
            line = self.rfile.readline().strip()
            if line == DONE:
                break
            reply += line + "\n"

        return reply

    def setEncoding(self):

        encoding = self.rfile.readline().strip()
        print "Encoding change request received: " + encoding
        prevencoding = self.server.solver.encoding
        self.server.solver.encoding = encoding
        try:
            self.server.solver.reset()
            print "Encoding has been set and instance has been reset"
            msg = SUCCESS + "\n" + DONE + "\n"
        except RuntimeError:
            print "There was an error with the given file, encoding not set."
            msg = FAIL + "\n" + DONE + "\n"

        print "Sending reply: " + msg.replace("\n", " ").replace(DONE, "")
        self.request.sendall(msg)




    def sendBase(self):
        # Receive instance
        reply = self.receive()

        print "Instance received!"

        self.server.solver.loadInstanceStr(reply)
        self.server.solver.groundStart()

        # Get the values for the reply
        reply = {}
        self.server.solver.getBaseValues()
        reply[FLOORAMT] = self.server.solver.floors
        reply[STARTPOS] = self.server.solver.startPos
        reply[REQUESTS] = self.server.solver.getRequestInfo()

        print "Sending base information..."
        msg = json.dumps(reply) + "\n" + DONE + "\n"
        self.request.sendall(msg)
        print "Base sent."

    def solve(self):

        step = int(self.rfile.readline().strip())
        print "step received " + str(step)
        self.server.solver.callSolver(step)
        actions = self.server.solver.getFullPlan()
        reqs = self.server.solver.getRequestInfo()
        stats = self.server.solver.getStats()

        ans = {ACTIONS: actions, REQUESTS: reqs, STATS: stats}
        print ans
        msg = json.dumps(ans) + "\n" + DONE + "\n"

        print "Sending solve reply...\n"
        self.request.sendall(msg)
        print "Reply sent.\n"

    def addRequest(self):

        print "Reading request..."
        type = self.rfile.readline().strip()
        time = int(self.rfile.readline().strip())
        param1 = self.rfile.readline().strip()
        if type == REQ_DELIVER:
            param1 = int(param1)
        param2 = int(self.rfile.readline().strip())

        self.server.solver.addRequest(type, time, [param1, param2])
        print "Request added"

        msg  = SUCCESS + "\n" + DONE + "\n"
        self.request.sendall(msg)

    def reset(self):
        mode = self.rfile.readline().strip()

        print "Acknowledged " + mode + " Reset"

        if mode == "soft":
            self.server.solver.reset()
        elif mode == "hard":
            self.server.solver = EncodingManager.Solver(self.server.solver.encoding)

        msg = SUCCESS + "\n" + DONE + "\n"
        self.request.sendall(msg)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Server for a clingo solver")

    parser.add_argument("-e", "--encoding", help="Encoding file name to use initially.", default=SolverConfig.encoding)
    parser.add_argument("-H", "--host", help="Host IP address", default=HOST)
    parser.add_argument("-P", "--port", help="Port for the server", default=PORT)

    args = parser.parse_args()
    host = args.host
    port = args.port
    encoding = args.encoding

    print "Initializing server with host: " + host + " and port: " + str(port)
    server = SocketServer.TCPServer((host, port), SolverHandler)
    server.solver = EncodingManager.Solver(encoding)

    server.serve_forever()