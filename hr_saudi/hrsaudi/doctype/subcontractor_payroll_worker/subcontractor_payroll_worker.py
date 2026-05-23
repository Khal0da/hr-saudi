import frappe
from frappe.model.document import Document
from frappe.utils import flt


class SubcontractorPayrollWorker(Document):
	def validate(self):
		# Auto-fetch worker details
		if self.worker:
			worker = frappe.get_doc("Subcontractor Worker", self.worker)
			self.worker_name = worker.worker_name
			self.trade = worker.trade
			if not self.daily_rate:
				self.daily_rate = worker.daily_rate
			if not self.overtime_rate:
				self.overtime_rate = worker.overtime_rate

		# Calculate amounts
		self.regular_amount = flt(self.present_days) * flt(self.daily_rate)
		self.overtime_amount = flt(self.overtime_hours) * flt(self.overtime_rate)
		self.total_amount = flt(self.regular_amount) + flt(self.overtime_amount)
