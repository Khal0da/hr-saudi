import time
import logging
import signal
import sys
import yaml
from devices.zkteco import ZKTecoDevice
from queue.local_queue import LocalQueue
from client.erpnext_client import ERPNextClient

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
	handlers=[
		logging.FileHandler("bridge.log"),
		logging.StreamHandler()
	]
)
logger = logging.getLogger(__name__)


class BiometricBridge:
	def __init__(self, config_path="config.yaml"):
		with open(config_path, "r") as f:
			self.config = yaml.safe_load(f)

		self.erp = ERPNextClient(self.config["server"])
		self.queue = LocalQueue()
		self.devices = []
		self.running = False
		self.device_user_map = {}

	def initialize(self):
		logger.info("Initializing Biometric Bridge...")

		self.load_mapping()

		for dev_cfg in self.config["devices"]:
			device = ZKTecoDevice(dev_cfg)
			if device.connect():
				self.devices.append(device)
				logger.info(f"Connected to device: {dev_cfg['name']}")
			else:
				logger.error(f"Failed to connect to: {dev_cfg['name']}")

		logger.info(f"Initialized {len(self.devices)} devices")
		logger.info(f"Loaded {len(self.device_user_map)} user mappings")

	def load_mapping(self):
		"""تحميل جدول الربط من ERPNext"""
		try:
			response = self.erp.get_mapping()
			for item in response:
				key = (item["biometric_device"], item["device_user_id"])
				self.device_user_map[key] = item["employee"]
			logger.info(f"Mapping loaded: {len(self.device_user_map)} entries")
		except Exception as e:
			logger.error(f"Failed to load mapping: {e}")

	def resolve_employee(self, device_name, user_id):
		"""تحويل رقم الجهاز لرقم موظف"""
		key = (device_name, str(user_id))
		return self.device_user_map.get(key)

	def sync_devices(self):
		for device in self.devices:
			try:
				logs = device.get_attendance_logs()

				for log in logs:
					employee_id = self.resolve_employee(
						log["device_name"], log["employee_id"]
					)

					if employee_id:
						log["erp_employee_id"] = employee_id
						self.queue.enqueue(log)
					else:
						logger.warning(
							f"Unknown user {log['employee_id']} "
							f"on device {log['device_name']}"
						)

			except Exception as e:
				logger.error(f"Error syncing device {device.name}: {e}")

	def push_to_erp(self):
		pending = self.queue.get_pending(self.config.get("batch_size", 100))

		if not pending:
			return

		logs_to_push = [
			{
				"employee_id": log["erp_employee_id"],
				"device_name": log["device_name"],
				"timestamp": log["timestamp"],
				"direction": log["direction"]
			}
			for log in pending
		]

		try:
			result = self.erp.push_attendance(logs_to_push)

			sent_ids = [log["id"] for log in pending]
			self.queue.mark_sent(sent_ids)

			logger.info(
				f"Pushed {len(pending)} logs. "
				f"Success: {result.get('success', 0)}, "
				f"Failed: {result.get('failed', 0)}, "
				f"Duplicates: {result.get('duplicates', 0)}"
			)

		except Exception as e:
			failed_ids = [log["id"] for log in pending]
			self.queue.mark_failed(failed_ids, str(e))
			logger.error(f"Push failed: {e}")

	def run(self):
		self.running = True
		self.initialize()

		poll_interval = self.config.get("poll_interval", 60)
		mapping_refresh = self.config.get("mapping_refresh_interval", 3600)
		last_mapping_load = time.time()

		logger.info(f"Bridge running. Poll: {poll_interval}s, Mapping refresh: {mapping_refresh}s")

		while self.running:
			try:
				if time.time() - last_mapping_load > mapping_refresh:
					self.load_mapping()
					last_mapping_load = time.time()

				self.sync_devices()
				self.push_to_erp()
			except Exception as e:
				logger.error(f"Error in main loop: {e}")

			time.sleep(poll_interval)

	def stop(self):
		self.running = False
		for device in self.devices:
			device.disconnect()
		logger.info("Bridge stopped")


def main():
	bridge = BiometricBridge()

	def signal_handler(sig, frame):
		logger.info("Received shutdown signal")
		bridge.stop()
		sys.exit(0)

	signal.signal(signal.SIGINT, signal_handler)
	signal.signal(signal.SIGTERM, signal_handler)

	bridge.run()


if __name__ == "__main__":
	main()
