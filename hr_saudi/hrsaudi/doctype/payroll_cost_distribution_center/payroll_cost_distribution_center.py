import frappe
from frappe.model.document import Document
from frappe.utils import flt


class PayrollCostDistributionCenter(Document):
	def validate(self):
		self.calculate_amounts()

	def calculate_amounts(self):
		parent = self.parent_doc if hasattr(self, 'parent_doc') else None
		if not parent:
			return

		total_gross = flt(parent.total_gross_pay)
		total_deductions = flt(parent.total_deductions)
		percentage = flt(self.percentage) / 100

		self.gross_pay = flt(total_gross * percentage, 2)
		self.deductions = flt(total_deductions * percentage, 2)
		self.net_pay = flt(self.gross_pay - self.deductions, 2)

		# GOSI calculation (Saudi: 9.75% employee, 11.75% employer for Saudis)
		self.gosi_employee = flt(self.gross_pay * 0.0975, 2)
		self.gosi_employer = flt(self.gross_pay * 0.1175, 2)
