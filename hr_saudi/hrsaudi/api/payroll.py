import frappe
from frappe import _


def calculate_gosi(basic_salary, housing_allowance, is_saudi=True):
	"""
	حساب GOSI للموظفين السعوديين والوافدين
	
	للسعوديين:
	- الموظف: 9.75% من الراتب الأساسي + بدل السكن
	- صاحب العمل: 11.25% من الراتب الأساسي + بدل السكن
	- خطر المهنة: 2% (صاحب العمل فقط)
	
	للوافدين:
	- خطر المهنة: 2% من الراتب الأساسي (صاحب العمل فقط)
	- لا يوجد اشتراك للموظف
	"""
	total_salary = basic_salary + housing_allowance
	
	if is_saudi:
		employee_contribution = total_salary * 0.0975
		employer_pension = total_salary * 0.1125
		employer_hazard = total_salary * 0.02
		employer_total = employer_pension + employer_hazard
	else:
		employee_contribution = 0
		employer_hazard = basic_salary * 0.02
		employer_total = employer_hazard
	
	return {
		"employee_amount": round(employee_contribution, 2),
		"employer_amount": round(employer_total, 2),
		"total_amount": round(employee_contribution + employer_total, 2)
	}


@frappe.whitelist()
def calculate_employee_gosi(employee, salary_slip=None):
	"""
	حساب GOSI لموظف معين
	"""
	emp = frappe.get_doc("Employee", employee)
	
	# Get salary details
	if salary_slip:
		ss = frappe.get_doc("Salary Slip", salary_slip)
		basic = ss.get("base") or 0
		housing = 0
		for d in ss.earnings:
			if d.salary_component == "Housing Allowance":
				housing = d.amount
				break
	else:
		# Get from salary structure
		basic = frappe.db.get_value("Salary Detail", {
			"parent": frappe.db.get_value("Salary Structure Assignment", {"employee": employee}, "salary_structure"),
			"salary_component": "Basic Salary"
		}, "amount") or 0
		housing = frappe.db.get_value("Salary Detail", {
			"parent": frappe.db.get_value("Salary Structure Assignment", {"employee": employee}, "salary_structure"),
			"salary_component": "Housing Allowance"
		}, "amount") or 0
	
	is_saudi = emp.nationality == "Saudi"
	result = calculate_gosi(basic, housing, is_saudi)
	
	return result


@frappe.whitelist()
def generate_wps_batch(payroll_entry):
	"""
	توليد ملف WPS لدفعة رواتب
	"""
	pe = frappe.get_doc("Payroll Entry", payroll_entry)
	
	salary_slips = frappe.get_all("Salary Slip",
		filters={"payroll_entry": payroll_entry, "docstatus": 1},
		fields=["name", "employee", "employee_name", "net_pay", "bank_account_no", "branch"]
	)
	
	if not salary_slips:
		frappe.throw(_("No submitted salary slips found"))
	
	# Generate WPS file content
	wps_lines = []
	wps_lines.append("SIF")  # Start of file
	
	for i, ss in enumerate(salary_slips, 1):
		emp = frappe.get_doc("Employee", ss.employee)
		
		# WPS format: Employee ID, IBAN, Amount, Name
		employee_id = emp.get("custom_employee_id") or emp.name
		iban = emp.get("bank_account_no") or ""
		amount = f"{ss.net_pay:.2f}"
		name = ss.employee_name or ""
		
		wps_lines.append(f"{employee_id}|{iban}|{amount}|{name}")
	
	wps_lines.append("EOF")  # End of file
	
	# Create WPS Batch record
	batch = frappe.new_doc("WPS Batch")
	batch.payroll_entry = payroll_entry
	batch.batch_date = frappe.utils.today()
	batch.total_amount = sum(ss.net_pay for ss in salary_slips)
	batch.employee_count = len(salary_slips)
	batch.wps_file_content = "\n".join(wps_lines)
	batch.status = "Generated"
	batch.insert()
	
	frappe.db.commit()
	
	return batch.name
