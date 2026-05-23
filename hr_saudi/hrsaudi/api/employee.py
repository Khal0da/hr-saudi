import frappe
from frappe.utils import flt


@frappe.whitelist()
def validate_employee_id(doc, method=None):
	"""
	Validate National ID/Iqama number and auto-determine Saudi status
	- National ID starts with 1 (Saudi)
	- Iqama starts with 2 (Non-Saudi)
	"""
	if doc.custom_id_number:
		id_number = str(doc.custom_id_number).strip()
		
		# Validate length (Saudi IDs are 10 digits)
		if len(id_number) != 10:
			frappe.throw("ID Number must be 10 digits")
		
		# Validate it's all numbers
		if not id_number.isdigit():
			frappe.throw("ID Number must contain only digits")
		
		# Determine Saudi status based on first digit
		if id_number.startswith("1"):
			doc.custom_is_saudi = 1
			doc.custom_id_type = "National ID"
		elif id_number.startswith("2"):
			doc.custom_is_saudi = 0
			doc.custom_id_type = "Iqama"
		else:
			frappe.throw("ID Number must start with 1 (Saudi) or 2 (Non-Saudi)")
	
	# Validate IBAN format if provided
	if doc.custom_iban:
		iban = str(doc.custom_iban).strip().upper()
		if not iban.startswith("SA"):
			frappe.throw("IBAN must start with 'SA' for Saudi banks")
		if len(iban) != 24:
			frappe.throw("Saudi IBAN must be 24 characters long")


@frappe.whitelist()
def get_employee_gosi_status(employee):
	"""
	Get GOSI applicability for an employee
	Returns: {"is_saudi": bool, "gosi_applicable": bool, "employee_rate": float, "employer_rate": float}
	"""
	emp = frappe.get_doc("Employee", employee)
	
	if emp.custom_is_saudi:
		# Saudi employees: 9.75% employee, 11.75% employer
		return {
			"is_saudi": True,
			"gosi_applicable": True,
			"employee_rate": 0.0975,
			"employer_rate": 0.1175
		}
	else:
		# Non-Saudi employees: 9.75% employee, 2% employer (occupational hazard only)
		return {
			"is_saudi": False,
			"gosi_applicable": True,
			"employee_rate": 0.0975,
			"employer_rate": 0.02
		}


@frappe.whitelist()
def calculate_gosi(basic_salary, housing_allowance, employee_id):
	"""
	Calculate GOSI contributions based on employee nationality
	For Saudis: 9.75% employee, 11.75% employer (on basic + housing)
	For Non-Saudis: 9.75% employee, 2% employer (occupational hazard)
	"""
	emp = frappe.get_doc("Employee", employee_id)
	total_salary = flt(basic_salary) + flt(housing_allowance)
	
	if emp.custom_is_saudi:
		employee_gosi = total_salary * 0.0975
		employer_gosi = total_salary * 0.1175
	else:
		employee_gosi = total_salary * 0.0975
		employer_gosi = total_salary * 0.02
	
	return {
		"employee_gosi": employee_gosi,
		"employer_gosi": employer_gosi,
		"total_gosi": employee_gosi + employer_gosi,
		"is_saudi": emp.custom_is_saudi
	}
