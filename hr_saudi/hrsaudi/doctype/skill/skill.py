import frappe
from frappe.model.document import Document


class Skill(Document):
	pass


@frappe.whitelist()
def get_employees_with_skill(skill_name, proficiency_level=None):
	"""
	Get all employees who have a specific skill
	"""
	filters = {"skill": skill_name}
	if proficiency_level:
		filters["proficiency"] = proficiency_level
		
	mappings = frappe.get_all("Employee Skill",
		filters=filters,
		fields=["employee", "proficiency"]
	)
	
	employees = []
	for m in mappings:
		emp = frappe.get_doc("Employee", m.employee)
		employees.append({
			"employee": m.employee,
			"employee_name": emp.employee_name,
			"designation": emp.designation,
			"proficiency": m.proficiency
		})
		
	return employees
