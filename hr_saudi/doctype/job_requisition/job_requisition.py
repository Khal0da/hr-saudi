import frappe
from frappe.model.document import Document


class JobRequisition(Document):
	def validate(self):
		if self.salary_range_from and self.salary_range_to:
			if self.salary_range_from > self.salary_range_to:
				frappe.throw("Salary Range From cannot be greater than Salary Range To")

	def on_update(self):
		if self.approval_status == "Approved" and not self.approved_on:
			self.db_set("approved_on", frappe.utils.today())


@frappe.whitelist()
def approve_requisition(name, approved_by):
	doc = frappe.get_doc("Job Requisition", name)
	doc.approval_status = "Approved"
	doc.approved_by = approved_by
	doc.approved_on = frappe.utils.today()
	doc.save()
	frappe.msgprint(f"Job Requisition {name} has been approved")


@frappe.whitelist()
def create_job_opening_from_requisition(requisition_name):
	req = frappe.get_doc("Job Requisition", requisition_name)
	opening = frappe.new_doc("Job Opening")
	opening.job_title = req.job_title
	opening.department = req.department
	opening.designation = req.designation
	opening.employment_type = req.employment_type
	opening.job_description = req.qualifications
	opening.no_of_positions = req.no_of_positions
	opening.status = "Open"
	opening.insert()
	frappe.msgprint(f"Job Opening {opening.name} created from requisition")
	return opening.name
