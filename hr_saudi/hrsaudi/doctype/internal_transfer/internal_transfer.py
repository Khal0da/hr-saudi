import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, getdate


class InternalTransfer(Document):
	def validate(self):
		self.validate_transfer_details()
		self.auto_populate_clearance()
		self.validate_clearance_completion()

	def validate_transfer_details(self):
		if self.transfer_type == "Branch Transfer" and not self.to_branch:
			frappe.throw("To Branch is required for Branch Transfer")
		if self.transfer_type == "Project Transfer" and not self.to_project:
			frappe.throw("To Project is required for Project Transfer")
		if self.transfer_type == "Department Transfer" and not self.to_department:
			frappe.throw("To Department is required for Department Transfer")

	def auto_populate_clearance(self):
		if not self.clearance_checklist:
			default_tasks = [
				{"task": "IT Equipment Return", "department": "IT"},
				{"task": "ID Card / Access Card Return", "department": "Security"},
				{"task": "Uniform Return", "department": "Store"},
				{"task": "Accommodation Clearance", "department": "HR"},
				{"task": "Salary Advance Settlement", "department": "Accounts"},
				{"task": "Tool/Equipment Handover", "department": "Store"},
				{"task": "Project Handover", "department": "Projects"},
			]
			for task in default_tasks:
				self.append("clearance_checklist", {
					"task": task["task"],
					"department": task["department"],
					"status": "Pending"
				})

	def validate_clearance_completion(self):
		if self.status == "Approved":
			pending = [c for c in self.clearance_checklist if c.status == "Pending"]
			if pending:
				pending_tasks = ", ".join([c.task for c in pending])
				frappe.throw(f"Following clearance tasks are pending: {pending_tasks}")

	def on_submit(self):
		self.db_set("status", "Completed")
		self.update_employee_details()

	def update_employee_details(self):
		employee = frappe.get_doc("Employee", self.employee)
		if self.to_branch:
			employee.branch = self.to_branch
		if self.to_department:
			employee.department = self.to_department
		if self.to_cost_center:
			employee.cost_center = self.to_cost_center
		employee.save()

		frappe.msgprint(f"Employee {self.employee_name} transferred successfully")


@frappe.whitelist()
def approve_transfer(transfer_name, approved_by=None):
	"""Approve internal transfer"""
	if not approved_by:
		approved_by = frappe.session.user

	transfer = frappe.get_doc("Internal Transfer", transfer_name)
	transfer.status = "Approved"
	transfer.approved_by = approved_by
	transfer.approval_date = nowdate()
	transfer.save()
	transfer.submit()

	return transfer.name


@frappe.whitelist()
def clear_clearance_task(transfer_name, task_index, remarks=None):
	"""Clear a specific clearance task"""
	transfer = frappe.get_doc("Internal Transfer", transfer_name)
	clearance = transfer.clearance_checklist[int(task_index)]
	clearance.status = "Cleared"
	clearance.remarks = remarks or clearance.remarks
	clearance.cleared_by = frappe.session.user
	clearance.cleared_on = frappe.utils.now()
	transfer.save()

	# Check if all tasks are cleared
	all_cleared = all(c.status in ["Cleared", "Not Required"] for c in transfer.clearance_checklist)
	if all_cleared:
		transfer.status = "Approved"
		transfer.save()

	return transfer.name
