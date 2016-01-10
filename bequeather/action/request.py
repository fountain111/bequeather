#Request File
#Request HTTP/HTTPS
from .base import BaseAction
from bequeather.settings import get as getSettings
import logging

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

class RequestFileStream(BaseAction):

	def parseTargetPath(self):
		return self.getArgument('targetFile')

	def execute(self):
		bufferSize = getSettings().get('chunkSize')
		targetFile = self.parseTargetPath()
		try:
			f = open(targetFile, 'rb')
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
			self.getConnection()().send(part)

			#Read another chunk from the file
			part = f.read(bufferSize)

		#Flush and close the file stream
		f.close()

		#Return the file handler
		f

		self.setResponse(file = targetFile, bytes = totalBytes)

class RequestWeb(BaseAction):
	pass