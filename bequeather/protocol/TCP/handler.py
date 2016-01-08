import socketserver, re, json, threading, logging

bufferSize = 1024 * 100
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

class TCPRequestHandler(socketserver.BaseRequestHandler):

    def matchAction(self, message):
        if message == False:
            return False

        # IDEA: Convert 'possible actions' into a modular system
        self.possibleActions = {"requestFile": lambda: self.requestFile(self.data)}

        for key, action in self.possibleActions.items(): # TODO: Convert to list comprehension
            if(key == message):
                return action

        return False

    def handle(self):
        data = self.request.recv(bufferSize)
        logger.info('Received data: (%s) %dB', data, len(data))

        try:
            self.data = json.loads(str(data, 'ascii'))

            action = self.matchAction(self.data.get('action', False))
            if(action):
                #cur_thread = threading.current_thread()
                ##if self.requestFile(data):
                result = action()
                if result:
                    logger.debug("Success!")
                else:
                    logger.error("Action failed to execute")

            else:
                logger.warning('Unable to match action "%s"', action)


        except json.decoder.JSONDecodeError:
            logger.warning('Client data received was malformed (not JSON)')

        self.request.close()


    def requestFile(self, data):
        """Send a chunk of binary file over the socket

        Args:
            data: Dictionary of data received from client
                  must at least contain key 'file'

        Returns:
            Class io.BufferedReader - https://docs.python.org/3.5/library/io.html#io.BufferedReader

        Raises:
            KeyError: if 'file' key is missing from arg 'data'
            #FileNotFoundError: Not really.

        """
        try:
            f = open(data['file'], 'rb')
        except FileNotFoundError:
            logger.warning('[!] FILE NOT FOUND')
            return False

        part = f.read(bufferSize)
        totalBytes = 0

        #Providing there is a chunk of data to read let us loop until fin.
        while(part):
            responseSize = len(part)
            totalBytes += responseSize
            logger.info("Sending %d (%d received) bytes", responseSize, totalBytes)

            #Send off the chunk to the socket client 
            self.request.send(part)

            #Read another chunk from the file
            part = f.read(bufferSize)

        #Flush and close the file stream
        f.close()

        #Return the file handler
        return f