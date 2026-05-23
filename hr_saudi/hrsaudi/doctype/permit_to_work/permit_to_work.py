import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class PermittoWork(Document):
	def validate(self):
		if self.employee:
			self.employee_name = frappe.db.get_value("Employee", self.employee, "employee_name")
			
		if self.expiry_date and self.issue_date:
			if self.expiry_date < self.issue_date:
				frappe.throw("Expiry Date cannot be before Issue Date")

	def on_update(self):
		if self.status == "Approved" and not self.approved_on:
			self.db_set("approved_on", now_datetime())


@frappe.whitelist()
def check_permit_status(employee, permit_type=None):
	"""
	Check if employee has valid permits
	"""
	filters = {
		"employee": employee,
		"status": "Approved",
		"expiry_date": [">=", frappe.utils.today()]
	}
	
	if permit_type:
		filters["permit_type"] = permit_type
		
	permits = frappe.get_all("Permit to Work",
		filters=filters,
		fields=["name", "permit_type", "expiry_date", "project", "site"]
	)
	
	return {
		"has_valid_permit": len(permits) > 0,
		"permits": permits
	}


@frappe.whitelist()
def validate_permit_for_assignment(employee, project=None):
	"""
	Validate if employee has required permits for assignment
	"""
	result = check_permit_status(employee)
	
	if not result["has_valid_permit"]:
		return {
			"allowed": False,
			"message": "Employee does not have valid work permits"
		}
		
	return {
		"allowed": True,
		"message": "Employee has valid permits",
		"permits": result["permits"]
	}
