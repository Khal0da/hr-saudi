import frappe


@frappe.whitelist()
def validate_branch_payroll(doc, method=None):
	"""
	التحقق من Payroll Entry حسب الفرع
	"""
	if doc.custom_branch:
		branch_cost_center = frappe.db.get_value(
			"Branch", doc.custom_branch, "cost_center"
		)
		if branch_cost_center:
			doc.custom_branch_cost_center = branch_cost_center
