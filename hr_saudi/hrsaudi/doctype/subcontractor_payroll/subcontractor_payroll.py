import frappe
from frappe.model.document import Document
from frappe.utils import flt, get_first_day, get_last_day


class SubcontractorPayroll(Document):
	def validate(self):
		if not self.workers:
			self.fetch_attendance_data()

		self.calculate_totals()

	def fetch_attendance_data(self):
		"""Fetch attendance data for the specified month/year and populate workers"""
		from_date = get_first_day(f"{self.year}-{self.month}-01")
		to_date = get_last_day(f"{self.year}-{self.month}-01")

		filters = {
			"subcontractor": self.subcontractor,
			"attendance_date": ["between", [from_date, to_date]],
			"docstatus": 1
		}

		if self.project:
			filters["project"] = self.project

		attendance = frappe.get_all(
			"Subcontractor Attendance",
			filters=filters,
			fields=["worker", "worker_name", "attendance_date", "status", "working_hours", "overtime_hours"]
		)

		# Group by worker
		worker_data = {}
		for record in attendance:
			if record.worker not in worker_data:
				worker_data[record.worker] = {
					"worker_name": record.worker_name,
					"present_days": 0,
					"absent_days": 0,
					"total_hours": 0.0,
					"overtime_hours": 0.0
				}

			if record.status == "Present":
				worker_data[record.worker]["present_days"] += 1
			elif record.status == "Absent":
				worker_data[record.worker]["absent_days"] += 1

			worker_data[record.worker]["total_hours"] += flt(record.working_hours)
			worker_data[record.worker]["overtime_hours"] += flt(record.overtime_hours)

		# Create worker rows
		self.workers = []
		for worker_id, data in worker_data.items():
			worker_doc = frappe.get_doc("Subcontractor Worker", worker_id)
			self.append("workers", {
				"worker": worker_id,
				"worker_name": data["worker_name"],
				"trade": worker_doc.trade,
				"present_days": data["present_days"],
				"absent_days": data["absent_days"],
				"total_hours": data["total_hours"],
				"daily_rate": worker_doc.daily_rate,
				"overtime_rate": worker_doc.overtime_rate,
				"overtime_hours": data["overtime_hours"]
			})

	def calculate_totals(self):
		"""Calculate total amounts from worker rows"""
		self.total_workers = len(self.workers)
		self.total_present_days = sum(w.present_days for w in self.workers)
		self.total_absent_days = sum(w.absent_days for w in self.workers)
		self.total_regular_amount = sum(w.regular_amount for w in self.workers)
		self.total_overtime_amount = sum(w.overtime_amount for w in self.workers)
		self.grand_total = self.total_regular_amount + self.total_overtime_amount

	def on_submit(self):
		self.db_set("status", "Submitted")
		self.create_purchase_invoice()

	def create_purchase_invoice(self):
		"""Create Purchase Invoice for subcontractor payment"""
		if self.status != "Submitted":
			return

		invoice = frappe.get_doc({
			"doctype": "Purchase Invoice",
			"supplier": self.subcontractor,
			"posting_date": frappe.utils.today(),
			"due_date": frappe.utils.add_days(frappe.utils.today(), 30),
			"project": self.project,
			"items": [{
				"item_code": "Subcontractor Services",
				"description": f"Subcontractor workforce services for {self.month}/{self.year}",
				"qty": 1,
				"rate": self.grand_total,
				"project": self.project
			}],
			"remarks": f"Generated from Subcontractor Payroll {self.name}"
		})
		invoice.insert()
		invoice.submit()

		frappe.msgprint(f"Purchase Invoice {invoice.name} created successfully")


@frappe.whitelist()
def generate_payroll(subcontractor, month, year, project=None):
	"""Generate subcontractor payroll for the given period"""
	payroll = frappe.get_doc({
		"doctype": "Subcontractor Payroll",
		"subcontractor": subcontractor,
		"month": month,
		"year": year,
		"project": project
	})
	payroll.insert()
	return payroll.name
