import frappe
from frappe import _


def validate_attendance(doc, method=None):
	"""
	التحقق من سجل الحضور
	"""
	if doc.employee and doc.attendance_date:
		existing = frappe.db.get_value(
			"Attendance",
			{
				"employee": doc.employee,
				"attendance_date": doc.attendance_date,
				"name": ["!=", doc.name]
			},
			"name"
		)

		if existing:
			frappe.throw(
				_("Attendance already exists for employee {0} on {1}").format(
					doc.employee, doc.attendance_date
				)
			)

	if doc.employee:
		branch = frappe.db.get_value("Employee", doc.employee, "branch")
		if branch:
			doc.branch = branch
