import sqlite3
import datetime

class database(object):

	def __init__(self):
		self.db = sqlite3.connect('blacklist.db')

	def setup(self):
		with self.db:
			self.db.execute('CREATE TABLE IF NOT EXISTS blacklist(id INTEGER PRIMARY KEY, ip TEXT, created DATETIME)')

	def close(self):
		self.db.close()

	def add_blacklist(self,ip):
		dt = datetime.datetime.now()
		with self.db:
			self.db.execute('INSERT INTO blacklist(ip, created) VALUES(:ip,:created)',{'ip':ip, 'created':dt})

	def get_blacklist(self,ip=None):
		self.db.row_factory = lambda C, R: { c[0]: R[i] for i, c in enumerate(C.description) }
		cur = self.db.cursor()

		if not ip:
			cur.execute('SELECT ip, created FROM blacklist')
		else:
			cur.execute('SELECT ip, created FROM blacklist WHERE ip=:ip', {'ip':ip})

		result = cur.fetchall()

		return result

	def del_blacklist(self,ip):
		with self.db:
			self.db.execute('DELETE FROM blacklist WHERE ip=:ip',{'ip':ip})

