import logging
from zk import ZK

logger = logging.getLogger(__name__)


class ZKTecoDevice:
	def __init__(self, config):
		self.name = config["name"]
		self.ip = config["ip"]
		self.port = config.get("port", 4370)
		self.timeout = config.get("timeout", 5)
		self.conn = None
		self.last_sync = None

	def connect(self):
		try:
			zk = ZK(self.ip, port=self.port, timeout=self.timeout)
			self.conn = zk.connect()
			self.conn.disable_device()
			self.conn.enable_device()
			logger.info(f"Connected to ZKTeco device: {self.name} ({self.ip})")
			return True
		except Exception as e:
			logger.error(f"Failed to connect to {self.name}: {e}")
			return False

	def disconnect(self):
		if self.conn:
			try:
				self.conn.disconnect()
			except Exception:
				pass
			self.conn = None

	def get_attendance_logs(self):
		"""جلب البصمات الجديدة من الجهاز"""
		logs = []
		try:
			attendance = self.conn.get_attendance()

			for record in attendance:
				if self.last_sync is None or record.timestamp > self.last_sync:
					from datetime import datetime
					logs.append({
						"device_name": self.name,
						"employee_id": str(record.user_id),
						"timestamp": record.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
						"direction": "In" if record.status == 0 else "Out",
					})

			if logs:
				from datetime import datetime
				self.last_sync = max(
					datetime.strptime(l["timestamp"], "%Y-%m-%d %H:%M:%S")
					for l in logs
				)

			logger.info(f"Pulled {len(logs)} logs from {self.name}")
			return logs

		except Exception as e:
			logger.error(f"Error pulling logs from {self.name}: {e}")
			return []

	def sync_device_time(self):
		"""مزامنة وقت الجهاز"""
		try:
			from datetime import datetime
			self.conn.set_time(datetime.now())
			logger.info(f"Synced time for {self.name}")
		except Exception as e:
			logger.error(f"Failed to sync time for {self.name}: {e}")

	def get_status(self):
		"""حالة الجهاز"""
		try:
			return {
				"name": self.name,
				"ip": self.ip,
				"connected": True,
				"user_count": self.conn.get_user_count(),
				"last_sync": self.last_sync
			}
		except Exception:
			return {
				"name": self.name,
				"ip": self.ip,
				"connected": False
			}
