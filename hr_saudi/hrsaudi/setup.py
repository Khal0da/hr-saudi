import frappe


def before_install():
	pass


def after_install():
	create_roles()
	create_salary_components()
	create_default_attendance_settings()


def after_migrate():
	pass


def create_roles():
	roles = [
		"HR Director",
		"HR Officer",
		"Recruitment Officer",
		"Payroll Manager",
		"Camp Manager",
		"Training Coordinator",
		"HSE Officer",
		"Employee (Self Service)",
	]
	for role in roles:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role}).insert()
			frappe.db.commit()


def create_salary_components():
	earnings = [
		("Basic Salary", "Basic salary amount"),
		("Housing Allowance", "Housing allowance per month"),
		("Transportation", "Transportation allowance"),
		("Food Allowance", "Food allowance per month"),
		("Site Allowance", "Site work allowance"),
		("Risk Allowance", "High risk work allowance"),
		("Equipment Operator Allowance", "Equipment operator allowance"),
		("Night Shift Allowance", "Night shift allowance"),
		("Overtime", "Overtime payment"),
		("Performance Bonus", "Performance-based bonus"),
		("Service Charge", "Hotel service charge share"),
		("Tips Share", "Tips distribution share"),
	]

	deductions = [
		("GOSI Employee", "Employee GOSI contribution"),
		("Absence Deduction", "Deduction for absence days"),
		("Late Deduction", "Deduction for late arrivals"),
		("Loan Installment", "Monthly loan installment"),
		("Advance Deduction", "Employee advance deduction"),
		("Penalty", "Disciplinary penalty deduction"),
		("Housing Deduction", "Company housing deduction"),
		("Food Deduction", "Company food deduction"),
	]

	for component, desc in earnings:
		if not frappe.db.exists("Salary Component", component):
			frappe.get_doc({
				"doctype": "Salary Component",
				"salary_component": component,
				"type": "Earning",
				"description": desc,
			}).insert()

	for component, desc in deductions:
		if not frappe.db.exists("Salary Component", component):
			frappe.get_doc({
				"doctype": "Salary Component",
				"salary_component": component,
				"type": "Deduction",
				"description": desc,
			}).insert()

	frappe.db.commit()


def create_default_attendance_settings():
	if not frappe.db.exists("Attendance Settings"):
		frappe.get_doc({
			"doctype": "Attendance Settings",
			"late_threshold": 15,
			"half_day_threshold": 60,
			"ot_multiplier": 1.5,
			"auto_generate_attendance": 1,
		}).insert()
		frappe.db.commit()
