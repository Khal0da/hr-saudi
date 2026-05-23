import frappe
from frappe.model.document import Document


class Incident(Document):
	def validate(self):
		if self.employee:
			self.employee_name = frappe.db.get_value("Employee", self.employee, "employee_name")
			self.department = frappe.db.get_value("Employee", self.employee, "department")

	def on_update(self):
		if self.status == "Closed" and not self.investigation_date:
			self.investigation_date = frappe.utils.today()


@frappe.whitelist()
def create_incident(employee, incident_type, severity, description, location=None, project=None):
	"""
	Create a new incident record
	"""
	incident = frappe.new_doc("Incident")
	incident.employee = employee
	incident.incident_type = incident_type
	incident.severity = severity
	incident.description = description
	incident.location = location
	incident.project = project
	incident.insert()
	
	frappe.msgprint(f"Incident {incident.name} created successfully")
	return incident.name


@frappe.whitelist()
def get_incident_statistics(employee=None, project=None, from_date=None, to_date=None):
	"""
	Get incident statistics
	"""
	filters = {}
	if employee:
		filters["employee"] = employee
	if project:
		filters["project"] = project
	if from_date:
		filters["incident_date"] = [">=", from_date]
	if to_date:
		if "incident_date" in filters:
			filters["incident_date"] = ["between", [from_date, to_date]]
		else:
			filters["incident_date"] = ["<=", to_date]
			
	incidents = frappe.get_all("Incident",
		filters=filters,
		fields=["incident_type", "severity", "status"]
	)
	
	stats = {
		"total": len(incidents),
		"by_type": {},
		"by_severity": {},
		"by_status": {}
	}
	
	for inc in incidents:
		stats["by_type"][inc.incident_type] = stats["by_type"].get(inc.incident_type, 0) + 1
		stats["by_severity"][inc.severity] = stats["by_severity"].get(inc.severity, 0) + 1
		stats["by_status"][inc.status] = stats["by_status"].get(inc.status, 0) + 1
		
	return stats
