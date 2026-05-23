import frappe
from frappe.model.document import Document


class Crew(Document):
	def validate(self):
		self.validate_members()

	def validate_members(self):
		for member in self.members:
			if frappe.db.exists("Crew Member", {"employee": member.employee, "parent": ("!=", self.name)}):
				existing_crew = frappe.db.get_value("Crew Member", {"employee": member.employee}, "parent")
				frappe.throw(f"Employee {member.employee} is already assigned to crew {existing_crew}")


@frappe.whitelist()
def get_crew_attendance(crew_name, date=None):
	if not date:
		date = frappe.utils.today()

	crew = frappe.get_doc("Crew", crew_name)
	attendance_data = []

	for member in crew.members:
		attendance = frappe.db.get_value("Attendance", {
			"employee": member.employee,
			"attendance_date": date
		}, ["status", "check_in", "check_out", "custom_source"], as_dict=True)

		attendance_data.append({
			"employee": member.employee,
			"employee_name": frappe.db.get_value("Employee", member.employee, "employee_name"),
			"status": attendance.status if attendance else "Not Marked",
			"check_in": attendance.check_in if attendance else None,
			"check_out": attendance.check_out if attendance else None,
			"source": attendance.custom_source if attendance else None
		})

	return attendance_data
