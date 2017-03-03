import socket
import time
import json

import VisConfig

MSG_SIZE = 4096

# Message types
# From client
BASE = "base"
SOLVE = "solve"
ADDREQS = "addreqs"
RESET = "reset"
ENCODING = "encoding"
# From server
SUCCESS = "success"
FAIL = "failure"
# Message end marker
DONE = "147258369"


# Dictionary Keys
ACTIONS = "actions"
REQUESTS = "requests"
STATS = "stats"
ELEVAMT = "elevamt"
FLOORAMT = "flooramt"
STARTPOS = "startpos"

# Request types
REQ_CALL     = "call"
REQ_DELIVER  = "deliver"



class MySocket(object):
    """
    A lot of the functionality was taken from the KiwaSocket.py class used in the Kiwa Robots logistics programm from Uni potsdam
    """

    def __init__(self):

        self._socket = None
        self._host = VisConfig.host
        self._port = VisConfig.port
        self.tries = 5

    def setHost(self, host):
        self._host = socket.gethostbyname(host)

    def setPort(self, port):
        self._port = port

    def close(self):
        if self._socket!= None: self._socket.close()
        self._socket = None

    def __del__(self):
        self._socket.close()

    @property
    def is_connected(self):
        return self._socket is not None

    def connect(self, host=None, port=None):
        if self.is_connected and host == self._host and port == self._port:
            return 0
        if host is not None:
            self._host = host
        if port is not None:
            self._port = port
        if self._socket is not None:
            self._socket.close()

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(2)

        for i in range(self.tries):
            try:
                self._socket.connect((self._host, self._port))
                print "Connected with host: " + self._host + " and port: " + str(self._port)
                return 1
            except(socket.error, socket.timeout):
                print "Failed to connect with server\nRetrying in 5 sek"
                time.sleep(5)

        print "Failed to connect with server"
        self._socket = None
        return 0


class VisSocket(MySocket):


    def __init__(self):
        super(VisSocket, self).__init__()

        self.replyHandler = {SOLVE: self.solve, BASE: self.baseInfo, ADDREQS : self.checkSuccess,
                             RESET : self.checkSuccess, ENCODING : self.checkSuccess}

        self.actions = None
        self.reqs = None
        self.stats = None
        self.floors = None
        self.startPos = None
        self.elevAmt = None

        self.instance = VisConfig.instance
        with open(self.instance, 'r') as myfile:
            self.instanceStr = myfile.read()

    def setInstance(self, instance):
        self.instance = instance
        with open(self.instance, 'r') as myfile:
            self.instanceStr = myfile.read()

    def communicate(self, msg, *args):

        if not self.is_connected:
            print "Cannot send message. No connection to a server!"
            return 0
        fullmsg = msg + "\n"
        if args != []:
            argmsg = ""
            for arg in args:
                argmsg += str(arg) + "\n"

            fullmsg += argmsg
        fullmsg += DONE + "\n"

        self._socket.sendall(fullmsg)

        print "Waiting for reply..."

        reply = self.receive()

        print "reply received: " + reply

        success = 0
        if msg in self.replyHandler:
            success = self.replyHandler[msg](reply)
        self.close()

        return success

    def receive(self):
        rfile = self._socket.makefile("r+b")
        reply = ""
        while 1:
            line = rfile.readline().strip()
            if line == DONE:
                break
            reply += line + "\n"

        return reply

    def solve(self, reply):
        dict = json.loads(reply)

        self.actions = {}
        self.reqs = {}
        if ACTIONS in dict:
            self.actions = {int(k): v for k, v in dict[ACTIONS].items()}
        if REQUESTS in dict:
            self.reqs = {int(k): v for k, v in dict[REQUESTS].items()}
        if STATS in dict:
            self.stats = dict[STATS]

        return 1

    def baseInfo(self, reply):
        dict = json.loads(reply.decode())

        if FLOORAMT in dict:
            self.floors = dict[FLOORAMT]
        if STARTPOS in dict:
            self.startPos = dict[STARTPOS]
            self.elevAmt = len(self.startPos)
        if REQUESTS in dict:
            self.reqs = dict[REQUESTS]

        return 1

    def checkSuccess(self, reply):

        if reply.strip() == SUCCESS:
            return 1
        elif reply.strip() == FAIL:
            return 0

    def sendEncoding(self, encoding):
        self.connect()
        return self.communicate(ENCODING, encoding)

    def sendBaseRequest(self, instance):

        self.connect()
        return self.communicate(BASE, instance)

    def getElevatorAmt(self):
        return self.elevAmt

    def getFloorAmt(self):
        return self.floors

    def startingPosition(self, elev):
        return self.startPos[elev-1]

    def nextMoves(self, step):
        self.connect()
        if self.communicate(SOLVE, step):
            return self.actions
        return 0

    def getRequests(self):
        return self.reqs

    def getStats(self):
        # TODO: Should be returned with the solve call in the dict, still have to implement that
        # also, still need to change how it is used. Have to switch from using the stat object to plain lists or dicts
        return self.stats

    def addRequest(self, type, time, params):
        print "preparing message"
        paramstr = type + "\n"
        paramstr += str(time) + "\n"
        for p in params:
            paramstr += str(p) + "\n"

        self.connect()
        print "sending request..." + paramstr.replace("\n", " ")
        return self.communicate(ADDREQS, paramstr)


    def reset(self, mode):
        self.connect()
        print "Sending " + mode + " reset."
        return self.communicate(RESET, mode)




if __name__ == "__main__":
    s = MySocket()
    s.connect()
    s.send()
