import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class SaudizationSettings(Document):
	def validate(self):
		self.update_compliance_status()

	def update_compliance_status(self):
		total_employees = self.current_saudi_employees + self.current_expat_employees
		if total_employees > 0:
			self.current_saudi_ratio = (self.current_saudi_employees / total_employees) * 100
		else:
			self.current_saudi_ratio = 0

		if self.current_saudi_ratio >= self.target_saudi_ratio:
			self.compliance_status = "Compliant"
		elif self.current_saudi_ratio >= (self.target_saudi_ratio * 0.8):
			self.compliance_status = "At Risk"
		else:
			self.compliance_status = "Non-Compliant"

		self.last_updated = now_datetime()

	@frappe.whitelist()
	def refresh_employee_counts(self):
		self.current_saudi_employees = frappe.db.count("Employee", {
			"status": "Active",
			"nationality": "Saudi"
		})
		self.current_expat_employees = frappe.db.count("Employee", {
			"status": "Active",
			"nationality": ["!=", "Saudi"]
		})
		total = self.current_saudi_employees + self.current_expat_employees
		if total > 0 and self.target_saudi_ratio:
			self.min_saudi_employees = int((self.target_saudi_ratio / 100) * total)
		self.update_compliance_status()
		self.save()


@frappe.whitelist()
def get_saudization_status():
	settings = frappe.get_single("Saudization Settings")
	settings.refresh_employee_counts()
	return {
		"current_saudi_employees": settings.current_saudi_employees,
		"current_expat_employees": settings.current_expat_employees,
		"current_saudi_ratio": settings.current_saudi_ratio,
		"target_saudi_ratio": settings.target_saudi_ratio,
		"compliance_status": settings.compliance_status,
		"nitaqat_category": settings.nitaqat_category
	}


@frappe.whitelist()
def calculate_nitaqat_category():
	settings = frappe.get_single("Saudization Settings")
	ratio = settings.current_saudi_ratio

	if ratio >= 30:
		return "Platinum"
	elif ratio >= 20:
		return "High Green"
	elif ratio >= 15:
		return "Mid Green"
	elif ratio >= 10:
		return "Low Green"
	else:
		return "Red"


def update_daily_compliance():
	"""Daily scheduler job to update saudization compliance"""
	settings = frappe.get_single("Saudization Settings")
	settings.refresh_employee_counts()
	
	if settings.compliance_status == "Non-Compliant":
		frappe.sendmail(
			recipients=[frappe.db.get_value("User", {"role_profile_name": "HR Manager"}, "email")],
			subject="Saudization Compliance Alert",
			message=f"Your company is currently non-compliant with Nitaqat requirements. Current Saudi ratio: {settings.current_saudi_ratio}%, Target: {settings.target_saudi_ratio}%"
		)
