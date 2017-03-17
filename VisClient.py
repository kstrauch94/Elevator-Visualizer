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
    Socket class that holds socket information and provides a close and connect functionality
    """

    def __init__(self):

        self._socket = None
        self._host = VisConfig.host
        self._port = VisConfig.port
        # Amount of failed connections until it stops trying
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
        """
        Attemps to connect with the server.
        :param host: optional host
        :param port: optinal port
        :return: int -> success or fail
        """
        if self.is_connected and host == self._host and port == self._port:
            return 0
        if host is not None:
            self.setHost(host)
        if port is not None:
            self.setPort(port)
        if self._socket is not None:
            # Close a socket if it was already open (in case we want a new connection, say to another server)
            self._socket.close()

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(2)

        for i in range(self.tries):
            try:
                self._socket.connect((self._host, self._port))
                if VisConfig.verbose:
                    print "Connected with host: " + self._host + " and port: " + str(self._port)
                return 1
            except(socket.error, socket.timeout):
                if VisConfig.verbose:
                    print "Failed to connect with server\nRetrying in 5 seconds"
                time.sleep(5)

        if VisConfig.verbose:
            print "Failed to connect with server"
        self._socket = None
        return 0


class VisSocket(MySocket):
    """
    Extends the socket class. Implements the sending of messages to make it simpler to use. Also has variables for the
    information that will be gathered from the solver.
    """

    def __init__(self):
        super(VisSocket, self).__init__()

        # After sending a message, the correct function to handle the reply will be called using this dict
        self.replyHandler = {SOLVE: self.solve, BASE: self.baseInfo, ADDREQS : self.checkSuccess,
                             RESET : self.checkSuccess, ENCODING : self.checkSuccess}

        self.actions = None
        self.reqs = None
        self.stats = None
        self.floors = None
        self.startPos = None
        self.elevAmt = None

        self.setInstance(VisConfig.instance)

    def setInstance(self, instance):
        """
        Store instance path name and convert it to string so that it can be sent via sockets
        :param instance: instance file path
        """
        self.instance = instance
        with open(self.instance, 'r') as myfile:
            self.instanceStr = myfile.read()

    def communicate(self, msg, *args):
        """
        takes the msg type and arguments and formats them into a string with the proper separator "\n". Then, it sends
        the string to the server and receives the reply. Finally it calls the correct function to handle the reply
        :param msg: message type as defined in the constants at the beginning of this file.
        :param args: any arguments in string form
        :return: int -> success or fail
        """
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
        if VisConfig.verbose:
            print "Waiting for reply..."

        reply = self.receive()
        if VisConfig.verbose:
            print "reply received: " + reply

        # Message is considered successful if reply is received unless the reply handler says otherwise
        success = 1
        if msg in self.replyHandler:
            success = self.replyHandler[msg](reply)
        self.close()

        return success

    def receive(self):
        """
        Function to read the handle receiving any reply. Keeps the "\n" separator.
        :return: reply message
        """
        rfile = self._socket.makefile("r+b")
        reply = ""
        while 1:
            line = rfile.readline().strip()
            if line == DONE:
                break
            reply += line + "\n"

        return reply

    def solve(self, reply):
        """
        Handler for the solve message reply. Extracts the actions, request and stats dict. Returns failure if actions
        dict is not present.
        :param reply: reply string
        :return: int -> success or fail
        """
        dict = json.loads(reply)

        self.actions = {}
        self.reqs = {}
        if ACTIONS in dict:
            self.actions = {int(k): v for k, v in dict[ACTIONS].items()}
        else:
            return 0
        if REQUESTS in dict:
            self.reqs = {int(k): v for k, v in dict[REQUESTS].items()}
        if STATS in dict:
            self.stats = dict[STATS]

        return 1

    def baseInfo(self, reply):
        """
        Handler for the base message. Extract information from the received dictionary. Fails if any information is
        missing
        :param reply: reply string
        :return: int -> success or fail
        """
        dict = json.loads(reply.decode())

        if FLOORAMT in dict:
            self.floors = dict[FLOORAMT]
        else:
            return 0
        if STARTPOS in dict:
            self.startPos = dict[STARTPOS]
            self.elevAmt = len(self.startPos)
        else:
            return 0
        if REQUESTS in dict:
            self.reqs = dict[REQUESTS]
        else:
            return 0

        return 1

    def checkSuccess(self, reply):
        """
        Some message only return a fail or success message. This handles those replies and returns it
        :param reply: reply string
        :return: int -> success or fail
        """
        if reply.strip() == SUCCESS:
            return 1
        elif reply.strip() == FAIL:
            return 0

    def sendEncoding(self, encoding):
        """
        Connect to server and send the encoding
        :param encoding: encoding string (user input)
        :return: int -> success or fail
        """
        self.connect()
        return self.communicate(ENCODING, encoding)

    def sendBaseRequest(self, instance):
        """
        Connects to server and sends the base message and the instance string
        :param instance: instance in string form
        :return: int -> success or fail
        """
        self.connect()
        return self.communicate(BASE, instance)

    def getElevatorAmt(self):
        return self.elevAmt

    def getFloorAmt(self):
        return self.floors

    def startingPosition(self, elev):
        return self.startPos[elev-1]

    def nextMoves(self, step):
        """
        Connect to server and send a solve message. Return the dictionary if everything goes well
        :param step: step at which the solving should start (int)
        :return: int -> success or fail
        """
        self.connect()
        if self.communicate(SOLVE, step):
            return self.actions
        return 0

    def getRequests(self):
        return self.reqs

    def getStats(self):
        return self.stats

    def addRequest(self, type, time, params):
        """
        Connects to server and adds a request.
        :param type: request type
        :param time: request time
        :param params: request params
        :return: int -> success or fail
        """
        self.connect()
        if VisConfig.verbose:
            print "sending request...", type, time, params
        return self.communicate(ADDREQS, type, time, params[0], params[1])


    def reset(self, mode):
        """
        Connects to the server and sends a reset message.
        :param mode: "soft" or "hard"
        :return: int -> success or fail
        """
        self.connect()
        if VisConfig.verbose:
            print "Sending " + mode + " reset."
        return self.communicate(RESET, mode)
