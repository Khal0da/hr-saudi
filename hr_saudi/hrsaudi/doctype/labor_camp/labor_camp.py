import frappe
from frappe.model.document import Document


class LaborCamp(Document):
	def validate(self):
		self.calculate_occupancy()

	def calculate_occupancy(self):
		if self.capacity:
			self.current_occupancy = frappe.db.count("Employee", {
				"labor_camp": self.name,
				"status": "Active"
			})
			self.available_beds = self.capacity - self.current_occupancy


@frappe.whitelist()
def get_camp_occupancy(camp_name):
	camp = frappe.get_doc("Labor Camp", camp_name)
	employees = frappe.get_all("Employee",
		filters={"labor_camp": camp_name, "status": "Active"},
		fields=["name", "employee_name", "designation", "branch"]
	)
	return {
		"camp_name": camp.camp_name,
		"capacity": camp.capacity,
		"current_occupancy": camp.current_occupancy,
		"available_beds": camp.available_beds,
		"employees": employees
	}
