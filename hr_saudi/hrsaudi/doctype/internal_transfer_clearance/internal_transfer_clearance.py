import frappe
from frappe.model.document import Document


class InternalTransferClearance(Document):
	def validate(self):
		if self.status == "Cleared" and not self.cleared_by:
			self.cleared_by = frappe.session.user
			self.cleared_on = frappe.utils.now()
