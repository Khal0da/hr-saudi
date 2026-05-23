import requests
import logging

logger = logging.getLogger(__name__)


class ERPNextClient:
	def __init__(self, config):
		self.url = config["url"].rstrip("/")
		self.timeout = config.get("timeout", 30)
		self.session = requests.Session()
		self.session.headers.update({
			"Authorization": f"token {config['api_key']}:{config['api_secret']}",
			"Content-Type": "application/json"
		})

	def get_mapping(self):
		"""جلب جدول الربط من ERPNext"""
		response = self.session.get(
			f"{self.url}/api/method/hr_saudi.api.attendance.get_biometric_mapping",
			timeout=self.timeout
		)
		response.raise_for_status()
		return response.json()["message"]

	def push_attendance(self, logs):
		"""إرسال بصمات للسيرفر"""
		response = self.session.post(
			f"{self.url}/api/method/hr_saudi.api.attendance.bulk_push",
			json={"logs": logs},
			timeout=self.timeout
		)
		response.raise_for_status()
		return response.json()["message"]

	def health_check(self):
		"""التحقق من اتصال السيرفر"""
		try:
			response = self.session.get(
				f"{self.url}/api/method/ping",
				timeout=10
			)
			return response.status_code == 200
		except Exception:
			return False
