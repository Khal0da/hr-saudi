import frappe
from frappe.model.document import Document


class BiometricUserMapping(Document):
	def validate(self):
		self.set_registered_date()
		self.check_duplicate()
		self.validate_employee_or_subcontractor()

	def set_registered_date(self):
		if not self.registered_date:
			self.registered_date = frappe.utils.today()

	def check_duplicate(self):
		existing = frappe.db.exists("Biometric User Mapping", {
			"device_user_id": self.device_user_id,
			"biometric_device": self.biometric_device,
			"is_active": 1,
			"name": ["!=", self.name]
		})
		if existing:
			frappe.throw(
				f"Device User ID '{self.device_user_id}' is already mapped to another employee on this device"
			)

	def validate_employee_or_subcontractor(self):
		if self.employee and self.subcontractor_worker:
			frappe.throw("Cannot map both Employee and Subcontractor Worker")
		if not self.employee and not self.subcontractor_worker:
			frappe.throw("Please select either Employee or Subcontractor Worker")
