import frappe
from frappe.model.document import Document


class SubcontractorWorker(Document):
	def validate(self):
		# Ensure ID number is unique for this subcontractor
		if self.id_number and self.subcontractor:
			existing = frappe.db.exists("Subcontractor Worker", {
				"id_number": self.id_number,
				"subcontractor": self.subcontractor,
				"name": ("!=", self.name)
			})
			if existing:
				frappe.throw(f"Worker with ID {self.id_number} already exists for this subcontractor")

	def on_update(self):
		# If status changes to Demobilized, set date
		if self.status == "Demobilized" and not self.demobilization_date:
			self.db_set("demobilization_date", frappe.utils.today())


@frappe.whitelist()
def get_active_workers(subcontractor=None, project=None, trade=None):
	"""
	Get active subcontractor workers with filters
	"""
	filters = {"status": "Active"}
	if subcontractor:
		filters["subcontractor"] = subcontractor
	if project:
		filters["assigned_project"] = project
	if trade:
		filters["trade"] = trade
		
	return frappe.get_all("Subcontractor Worker",
		filters=filters,
		fields=["name", "worker_name", "subcontractor", "trade", "assigned_project", "daily_rate"]
	)
