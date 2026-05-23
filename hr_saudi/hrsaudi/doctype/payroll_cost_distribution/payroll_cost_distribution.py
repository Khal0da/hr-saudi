import frappe
from frappe.model.document import Document
from frappe.utils import flt


class PayrollCostDistribution(Document):
	def validate(self):
		self.validate_percentage_total()
		self.calculate_totals()
		self.distribute_costs()

	def validate_percentage_total(self):
		total_percentage = sum(flt(cc.percentage) for cc in self.cost_centers)
		if abs(total_percentage - 100) > 0.01:
			frappe.throw(f"Total percentage must equal 100%. Current total: {total_percentage}%")

	def calculate_totals(self):
		if not self.payroll_entry:
			return

		payroll = frappe.get_doc("Payroll Entry", self.payroll_entry)
		salary_slips = frappe.get_all("Salary Slip",
			filters={"payroll_entry": self.payroll_entry, "docstatus": 1},
			fields=["sum(gross_pay) as gross", "sum(total_deduction) as deductions", "count(*) as employees"]
		)

		if salary_slips:
			self.total_employees = salary_slips[0].employees
			self.total_gross_pay = flt(salary_slips[0].gross, 2)
			self.total_deductions = flt(salary_slips[0].deductions, 2)
			self.total_net_pay = flt(self.total_gross_pay - self.total_deductions, 2)

	def distribute_costs(self):
		for cc in self.cost_centers:
			percentage = flt(cc.percentage) / 100
			cc.gross_pay = flt(self.total_gross_pay * percentage, 2)
			cc.deductions = flt(self.total_deductions * percentage, 2)
			cc.net_pay = flt(cc.gross_pay - cc.deductions, 2)
			cc.gosi_employee = flt(cc.gross_pay * 0.0975, 2)
			cc.gosi_employer = flt(cc.gross_pay * 0.1175, 2)

			# Auto-fetch employee count from salary slips assigned to this cost center/project
			if cc.cost_center:
				filters = {"payroll_entry": self.payroll_entry, "docstatus": 1, "cost_center": cc.cost_center}
				if cc.project:
					filters["project"] = cc.project
				cc.employee_count = frappe.db.count("Salary Slip", filters)

	def on_submit(self):
		self.db_set("status", "Submitted")
		self.create_journal_entry()

	def on_cancel(self):
		self.db_set("status", "Cancelled")
		self.cancel_journal_entries()

	def create_journal_entry(self):
		"""Create Journal Entry to distribute payroll costs to cost centers"""
		if not self.cost_centers:
			return

		je = frappe.get_doc({
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"posting_date": self.posting_date,
			"company": frappe.db.get_single_value("Global Defaults", "default_company"),
			"cheque_no": self.name,
			"cheque_date": self.posting_date,
			"user_remark": f"Payroll Cost Distribution for {self.month}/{self.year}"
		})

		# Debit entries for each cost center
		for cc in self.cost_centers:
			if flt(cc.gross_pay) > 0:
				je.append("accounts", {
					"account": frappe.db.get_single_value("HR Settings", "salary_component_account") or "Salary - H",
					"cost_center": cc.cost_center,
					"project": cc.project,
					"debit_in_account_currency": cc.gross_pay,
					"credit_in_account_currency": 0
				})

			if flt(cc.gosi_employer) > 0:
				je.append("accounts", {
					"account": "GOSI Expense - H",
					"cost_center": cc.cost_center,
					"project": cc.project,
					"debit_in_account_currency": cc.gosi_employer,
					"credit_in_account_currency": 0
				})

		# Credit entry for total payroll liability
		total_debit = sum(flt(a.debit_in_account_currency) for a in je.accounts)
		je.append("accounts", {
			"account": "Payroll Payable - H",
			"cost_center": self.cost_centers[0].cost_center if self.cost_centers else None,
			"debit_in_account_currency": 0,
			"credit_in_account_currency": total_debit
		})

		je.insert()
		je.submit()

		frappe.msgprint(f"Journal Entry {je.name} created successfully")

	def cancel_journal_entries(self):
		"""Cancel related Journal Entries"""
		je_names = frappe.get_all("Journal Entry Account",
			filters={"reference_type": "Payroll Cost Distribution", "reference_name": self.name},
			pluck="parent"
		)

		for je_name in je_names:
			try:
				je = frappe.get_doc("Journal Entry", je_name)
				if je.docstatus == 1:
					je.cancel()
			except Exception as e:
				frappe.log_error(f"Failed to cancel JE {je_name}: {str(e)}")


@frappe.whitelist()
def create_cost_distribution(payroll_entry, month, year, branch=None):
	"""Create Payroll Cost Distribution from Payroll Entry"""
	distribution = frappe.get_doc({
		"doctype": "Payroll Cost Distribution",
		"payroll_entry": payroll_entry,
		"month": month,
		"year": year,
		"branch": branch
	})
	distribution.insert()
	return distribution.name


@frappe.whitelist()
def get_employee_cost_centers(payroll_entry, branch=None):
	"""Get employees grouped by cost center/project for a payroll entry"""
	filters = {"payroll_entry": payroll_entry, "docstatus": 1}
	if branch:
		filters["branch"] = branch

	salary_slips = frappe.get_all("Salary Slip",
		filters=filters,
		fields=["employee", "employee_name", "cost_center", "project", "gross_pay", "total_deduction"]
	)

	cost_center_data = {}
	for slip in salary_slips:
		key = slip.cost_center or "Unassigned"
		if key not in cost_center_data:
			cost_center_data[key] = {
				"cost_center": key,
				"project": slip.project,
				"employee_count": 0,
				"total_gross": 0,
				"total_deductions": 0,
				"employees": []
			}

		cost_center_data[key]["employee_count"] += 1
		cost_center_data[key]["total_gross"] += flt(slip.gross_pay)
		cost_center_data[key]["total_deductions"] += flt(slip.total_deduction)
		cost_center_data[key]["employees"].append({
			"employee": slip.employee,
			"employee_name": slip.employee_name,
			"gross_pay": slip.gross_pay
		})

	return cost_center_data
