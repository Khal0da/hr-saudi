import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class LocalQueue:
	def __init__(self, db_path="attendance_queue.db"):
		self.conn = sqlite3.connect(db_path)
		self._init_db()

	def _init_db(self):
		self.conn.execute("""
			CREATE TABLE IF NOT EXISTS queue (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				device_name TEXT NOT NULL,
				employee_id TEXT NOT NULL,
				timestamp TEXT NOT NULL,
				direction TEXT,
				status TEXT DEFAULT 'pending',
				retry_count INTEGER DEFAULT 0,
				error_message TEXT,
				created_at TEXT DEFAULT CURRENT_TIMESTAMP
			)
		""")
		self.conn.execute("""
			CREATE INDEX IF NOT EXISTS idx_status
			ON queue(status, retry_count)
		""")
		self.conn.commit()

	def enqueue(self, log_entry):
		"""إضافة بصمة للقائمة"""
		try:
			self.conn.execute("""
				INSERT INTO queue (device_name, employee_id, timestamp, direction)
				VALUES (?, ?, ?, ?)
			""", (
				log_entry["device_name"],
				log_entry["erp_employee_id"],
				log_entry["timestamp"],
				log_entry.get("direction", "Unknown")
			))
			self.conn.commit()
		except Exception as e:
			logger.error(f"Failed to enqueue: {e}")

	def get_pending(self, limit=100):
		"""جلب البصمات المعلقة"""
		cursor = self.conn.execute(
			"""SELECT id, device_name, employee_id, timestamp, direction
			   FROM queue
			   WHERE status='pending' AND retry_count < 3
			   ORDER BY created_at ASC
			   LIMIT ?""",
			(limit,)
		)
		rows = cursor.fetchall()
		return [
			{
				"id": r[0],
				"device_name": r[1],
				"erp_employee_id": r[2],
				"timestamp": r[3],
				"direction": r[4]
			}
			for r in rows
		]

	def mark_sent(self, ids):
		"""تحديد كمرسل"""
		if not ids:
			return
		placeholders = ",".join("?" * len(ids))
		self.conn.execute(
			f"UPDATE queue SET status='sent' WHERE id IN ({placeholders})",
			ids
		)
		self.conn.commit()

	def mark_failed(self, failed_ids, error_msg=""):
		"""تحديد كفشل"""
		if not failed_ids:
			return
		placeholders = ",".join("?" * len(failed_ids))
		self.conn.execute(
			f"""UPDATE queue
				SET status='failed', retry_count=retry_count+1, error_message=?
				WHERE id IN ({placeholders})""",
			(error_msg, *failed_ids)
		)
		self.conn.commit()

	def get_stats(self):
		"""إحصائيات القائمة"""
		cursor = self.conn.execute(
			"""SELECT status, COUNT(*) FROM queue GROUP BY status"""
		)
		return dict(cursor.fetchall())
