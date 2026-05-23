import frappe
from frappe.model.document import Document
from frappe.utils import flt, today


class EmployeeCustody(Document):
	def validate(self):
		self.calculate_totals()
		self.validate_duplicate_custody()

	def calculate_totals(self):
		self.item_count = len(self.items)
		self.total_estimated_value = sum(flt(item.estimated_value) * flt(item.quantity) for item in self.items)

	def validate_duplicate_custody(self):
		# Check if employee already has active custody for same items
		if self.items:
			for item in self.items:
				existing = frappe.db.exists("Employee Custody", {
					"employee": self.employee,
					"status": ["in", ["Issued", "Partially Returned"]],
					"name": ("!=", self.name)
				})
				if existing:
					existing_doc = frappe.get_doc("Employee Custody", existing)
					for existing_item in existing_doc.items:
						if existing_item.item_code == item.item_code and existing_item.serial_number == item.serial_number:
							frappe.throw(f"Item {item.item_code} (Serial: {item.serial_number}) is already in custody under {existing_doc.name}")

	def on_submit(self):
		self.db_set("status", "Issued")

	def on_cancel(self):
		self.db_set("status", "Cancelled")


@frappe.whitelist()
def return_items(custody_name, return_items):
	"""
	Process return of custody items
	return_items: list of dicts with item_code, serial_number, return_condition, notes
	"""
	import json
	if isinstance(return_items, str):
		return_items = json.loads(return_items)

	custody = frappe.get_doc("Employee Custody", custody_name)
	
	for ret_item in return_items:
		for item in custody.items:
			if item.item_code == ret_item.get("item_code") and item.serial_number == ret_item.get("serial_number"):
				item.return_date = today()
				item.return_condition = ret_item.get("return_condition", "Returned - Good")
				if ret_item.get("notes"):
					item.notes = ret_item.get("notes")
				break

	# Update status based on returns
	returned_count = sum(1 for item in custody.items if item.return_date)
	total_count = len(custody.items)

	if returned_count == total_count:
		custody.status = "Fully Returned"
	elif returned_count > 0:
		custody.status = "Partially Returned"

	custody.save()
	frappe.db.commit()

	return custody.name


@frappe.whitelist()
def get_employee_custody_summary(employee):
	"""Get summary of all active custody items for an employee"""
	custodies = frappe.get_all("Employee Custody",
		filters={"employee": employee, "status": ["in", ["Issued", "Partially Returned"]]},
		fields=["name", "custody_date", "status", "project"]
	)

	summary = []
	for custody in custodies:
		custody_doc = frappe.get_doc("Employee Custody", custody.name)
		for item in custody_doc.items:
			if not item.return_date:
				summary.append({
					"custody": custody.name,
					"item_code": item.item_code,
					"item_name": item.item_name,
					"serial_number": item.serial_number,
					"custody_type": item.custody_type,
					"quantity": item.quantity,
					"condition": item.condition,
					"estimated_value": item.estimated_value,
					"custody_date": custody.custody_date,
					"project": custody.project
				})

	return summary
