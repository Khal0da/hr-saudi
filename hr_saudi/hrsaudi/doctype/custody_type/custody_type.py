import frappe
from frappe.model.document import Document


class CustodyType(Document):
	def validate(self):
		if self.is_active == 0:
			self.check_if_used()

	def check_if_used(self):
		used = frappe.db.exists("Employee Custody Item", {"custody_type": self.custody_type})
		if used:
			frappe.throw("Cannot deactivate this custody type as it is used in existing custody records")
