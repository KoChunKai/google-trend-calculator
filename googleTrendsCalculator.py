# -*- coding: utf8 -*-
# coding: utf8
import urllib
import csv
import threading, time
import Queue
import StringIO
import json, requests
import time
import threading
from loadStockList import parserCSV
import random
import calTime

URL_EXPLORE = ''
URL_MULTLINE = ''

class check:

	def __init__(self, stock, name, time):
		self.stock = stock
		self.name = name
		self.time = time
		self.calData = []

	def do(self):
		array = self.getMultiline()
		if(len(array) == 0):
			return
		self.cal(array, 0)
		self.cal(array, 1)
		return len(self.calData)

	def getExplore(self):
		obj = {}
		response = requests.get(URL_EXPLORE % (self.stock, self.time, self.name, self.time))
		print self.name + 'getExplore:' + str(response)
		d = response.text
		try:
			j = json.loads(d.replace(StringIO.StringIO(d).readline(), ""))
			obj['request'] = json.dumps(j['widgets'][0]['request'])
			obj['token'] = j['widgets'][0]['token']
		except Exception, e:
			print d
		return obj

	def getMultiline(self):
		try:
			explore = self.getExplore()
			response = requests.get(URL_MULTLINE % (explore['request'], explore['token']))
			print self.name + 'getMultiline:' + str(response)
			d = response.text
			data = d.replace(StringIO.StringIO(d).readline(), "")
			obj = json.loads(data)
			return obj['default']['timelineData']
		except Exception, e:
			return []

	def cal(self, data, position):
		value = []
		for d in data:
			o = {}
			o['value'] = d['value'][position]
			o['time'] = d['time']
			value.append(o)
		# for index in range(len(data) - 5, len(data)):
		# 	d = data[index]
		# 	o = {}
		# 	o['value'] = d['value'][position]
		# 	o['time'] = d['time']
		# 	value.append(o)
		rates = []
		for index in range(1, len(value)):
			try:
				rates.append((value[index]['value'] - value[index-1]['value']) * 1.0 / value[index-1]['value'])
			except Exception, e:
				rates.append(((value[index]['value'] - value[index-1]['value']) * 1.0 / 50))

		for rate in range(2, len(rates)):
			v = ((1.0 + rates[rate]) * (1.0 + rates[rate-1]) * (1.0 + rates[rate - 2])) ** (1.0 / 3.0) - 1.0
			if(v >= 0.3):
				obj = {'name': self.name.decode('utf-8'),'time':value[rate]['time'], 'value':v}
				self.calData.append(obj)

def doJob(*args):
	queue = args[0]
	while queue.qsize() > 0:
		time.sleep(random.randint(1,10))
		job = queue.get()
		job.do()

t1 = check('stockID', 'stockName', 'time') #7~11
print t1.do()

