import frappe
from frappe.model.document import Document
from frappe.utils import getdate, flt, today


class SubcontractorAttendance(Document):
	def validate(self):
		# Auto-fetch worker details
		if self.worker:
			worker = frappe.get_doc("Subcontractor Worker", self.worker)
			self.worker_name = worker.worker_name
			self.subcontractor = worker.subcontractor
			self.trade = worker.trade
			if not self.project:
				self.project = worker.assigned_project
			if not self.site:
				self.site = worker.assigned_site

		# Calculate working hours from check-in/out
		if self.check_in and self.check_out:
			check_in = frappe.utils.get_datetime(self.check_in)
			check_out = frappe.utils.get_datetime(self.check_out)
			self.working_hours = flt((check_out - check_in).total_seconds() / 3600, 2)

			# Calculate overtime (standard 8 hours)
			if self.working_hours > 8:
				self.overtime_hours = flt(self.working_hours - 8, 2)
			else:
				self.overtime_hours = 0.0

		# Prevent duplicate attendance for same worker/date
		if self.attendance_date and self.worker:
			existing = frappe.db.exists("Subcontractor Attendance", {
				"worker": self.worker,
				"attendance_date": self.attendance_date,
				"name": ("!=", self.name),
				"docstatus": 1
			})
			if existing:
				frappe.throw(f"Attendance already submitted for worker {self.worker} on {self.attendance_date}")

	def on_submit(self):
		# Mark as processed for payroll
		self.db_set("status", "Submitted")


@frappe.whitelist()
def bulk_upload_attendance(attendance_data):
	"""
	Bulk upload subcontractor attendance
	attendance_data: list of dicts with worker, date, check_in, check_out, status
	"""
	import json
	if isinstance(attendance_data, str):
		attendance_data = json.loads(attendance_data)

	created = []
	errors = []

	for data in attendance_data:
		try:
			# Check for existing
			existing = frappe.db.exists("Subcontractor Attendance", {
				"worker": data.get("worker"),
				"attendance_date": data.get("attendance_date"),
				"docstatus": ("!=", 1)
			})
			
			if existing:
				doc = frappe.get_doc("Subcontractor Attendance", existing)
				doc.update({
					"check_in": data.get("check_in"),
					"check_out": data.get("check_out"),
					"status": data.get("status", "Present"),
					"source": data.get("source", "Manual")
				})
				doc.save()
				created.append(doc.name)
			else:
				doc = frappe.get_doc({
					"doctype": "Subcontractor Attendance",
					"worker": data.get("worker"),
					"attendance_date": data.get("attendance_date"),
					"check_in": data.get("check_in"),
					"check_out": data.get("check_out"),
					"status": data.get("status", "Present"),
					"source": data.get("source", "Manual")
				})
				doc.insert()
				created.append(doc.name)
		except Exception as e:
			errors.append(f"Worker {data.get('worker')}: {str(e)}")

	return {"created": created, "errors": errors}


@frappe.whitelist()
def get_monthly_summary(subcontractor, month, year):
	"""
	Get monthly attendance summary for a subcontractor
	"""
	from frappe.utils import get_last_day, get_first_day
	
	first_day = get_first_day(f"{year}-{month}-01")
	last_day = get_last_day(f"{year}-{month}-01")
	
	attendance = frappe.get_all("Subcontractor Attendance",
		filters={
			"subcontractor": subcontractor,
			"attendance_date": ["between", [first_day, last_day]],
			"docstatus": 1
		},
		fields=["worker", "worker_name", "attendance_date", "status", "working_hours", "overtime_hours"]
	)
	
	summary = {}
	for record in attendance:
		if record.worker not in summary:
			summary[record.worker] = {
				"worker_name": record.worker_name,
				"present_days": 0,
				"absent_days": 0,
				"total_hours": 0.0,
				"total_overtime": 0.0
			}
		
		if record.status == "Present":
			summary[record.worker]["present_days"] += 1
		elif record.status == "Absent":
			summary[record.worker]["absent_days"] += 1
			
		summary[record.worker]["total_hours"] += flt(record.working_hours)
		summary[record.worker]["total_overtime"] += flt(record.overtime_hours)
	
	return summary


def process_daily_subcontractor_attendance():
	"""
	Scheduler event: Auto-mark absent for workers with no attendance
	"""
	yesterday = getdate(today())
	
	active_workers = frappe.get_all("Subcontractor Worker",
		filters={"status": "Active"},
		fields=["name", "subcontractor", "assigned_project"]
	)
	
	for worker in active_workers:
		exists = frappe.db.exists("Subcontractor Attendance", {
			"worker": worker.name,
			"attendance_date": yesterday
		})
		
		if not exists:
			try:
				doc = frappe.get_doc({
					"doctype": "Subcontractor Attendance",
					"worker": worker.name,
					"subcontractor": worker.subcontractor,
					"attendance_date": yesterday,
					"status": "Absent",
					"source": "System"
				})
				doc.insert()
				frappe.db.commit()
			except Exception as e:
				frappe.log_error(f"Failed to mark absent for {worker.name}: {str(e)}")
