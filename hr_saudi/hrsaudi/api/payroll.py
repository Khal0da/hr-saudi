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


@frappe.whitelist()
def export_payroll_by_project(project, month, year):
	"""
	Export payroll for a specific project as PDF
	Returns HTML content for PDF generation
	"""
	from frappe.utils import get_first_day, get_last_day
	
	first_day = get_first_day(f"{year}-{month}-01")
	last_day = get_last_day(f"{year}-{month}-01")
	
	# Get all salary slips for the project in the given month
	salary_slips = frappe.get_all("Salary Slip",
		filters={
			"custom_project": project,
			"start_date": ["between", [first_day, last_day]],
			"docstatus": 1
		},
		fields=["employee", "employee_name", "designation", "branch", "base", "gross_pay", 
				"total_deduction", "net_pay", "custom_gosi_employee_amount", "custom_gosi_employer_amount"]
	)
	
	if not salary_slips:
		frappe.throw(f"No payroll records found for project {project} in {month}/{year}")
	
	# Calculate totals
	total_basic = sum(ss.base for ss in salary_slips)
	total_gross = sum(ss.gross_pay for ss in salary_slips)
	total_deductions = sum(ss.total_deduction for ss in salary_slips)
	total_net = sum(ss.net_pay for ss in salary_slips)
	total_gosi_employee = sum(ss.custom_gosi_employee_amount or 0 for ss in salary_slips)
	total_gosi_employer = sum(ss.custom_gosi_employer_amount or 0 for ss in salary_slips)
	
	# Generate HTML for PDF
	html = f"""
	<!DOCTYPE html>
	<html>
	<head>
		<style>
			body {{ font-family: Arial, sans-serif; margin: 20px; }}
			h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
			table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
			th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
			th {{ background-color: #3498db; color: white; }}
			tr:nth-child(even) {{ background-color: #f2f2f2; }}
			.totals {{ font-weight: bold; background-color: #e8e8e8; }}
			.summary {{ margin-top: 20px; padding: 15px; background-color: #f9f9f9; border: 1px solid #ddd; }}
			.summary p {{ margin: 5px 0; }}
		</style>
	</head>
	<body>
		<h1>Payroll Report - {project}</h1>
		<p>Period: {first_day} to {last_day}</p>
		<p>Total Employees: {len(salary_slips)}</p>
		
		<table>
			<thead>
				<tr>
					<th>Employee ID</th>
					<th>Employee Name</th>
					<th>Designation</th>
					<th>Basic Salary</th>
					<th>Gross Pay</th>
					<th>GOSI (Employee)</th>
					<th>Total Deductions</th>
					<th>Net Pay</th>
				</tr>
			</thead>
			<tbody>
	"""
	
	for ss in salary_slips:
		html += f"""
			<tr>
				<td>{ss.employee}</td>
				<td>{ss.employee_name}</td>
				<td>{ss.designation or '-'}</td>
				<td>{ss.base:,.2f}</td>
				<td>{ss.gross_pay:,.2f}</td>
				<td>{ss.custom_gosi_employee_amount or 0:,.2f}</td>
				<td>{ss.total_deduction:,.2f}</td>
				<td>{ss.net_pay:,.2f}</td>
			</tr>
		"""
	
	html += f"""
			<tr class="totals">
				<td colspan="3">TOTALS</td>
				<td>{total_basic:,.2f}</td>
				<td>{total_gross:,.2f}</td>
				<td>{total_gosi_employee:,.2f}</td>
				<td>{total_deductions:,.2f}</td>
				<td>{total_net:,.2f}</td>
			</tr>
			</tbody>
		</table>
		
		<div class="summary">
			<h3>Summary</h3>
			<p><strong>Total Gross Pay:</strong> SAR {total_gross:,.2f}</p>
			<p><strong>Total GOSI (Employee):</strong> SAR {total_gosi_employee:,.2f}</p>
			<p><strong>Total GOSI (Employer):</strong> SAR {total_gosi_employer:,.2f}</p>
			<p><strong>Total Deductions:</strong> SAR {total_deductions:,.2f}</p>
			<p><strong>Total Net Pay:</strong> SAR {total_net:,.2f}</p>
		</div>
	</body>
	</html>
	"""
	
	return html


@frappe.whitelist()
def download_payroll_pdf(project, month, year):
	"""
	Generate and download payroll PDF for a project
	"""
	html = export_payroll_by_project(project, month, year)
	
	frappe.local.response.filename = f"Payroll_{project}_{month}_{year}.pdf"
	frappe.local.response.type = "pdf"
	frappe.local.response.content = frappe.utils.pdf.get_pdf(html)
