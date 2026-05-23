import frappe
from frappe.model.document import Document


class SiteDeployment(Document):
	def validate(self):
		if self.expected_end_date and self.deployment_date:
			if self.expected_end_date < self.deployment_date:
				frappe.throw("Expected End Date cannot be before Deployment Date")

	def on_update(self):
		if self.approval_status == "Approved" and self.status == "Planned":
			self.db_set("status", "Active")


@frappe.whitelist()
def deploy_crew_to_site(crew, project, site, deployment_date, work_description=None):
	deployment = frappe.new_doc("Site Deployment")
	deployment.crew = crew
	deployment.project = project
	deployment.site = site
	deployment.deployment_date = deployment_date
	deployment.work_description = work_description
	deployment.status = "Active"
	deployment.approval_status = "Approved"
	deployment.insert()
	frappe.msgprint(f"Crew {crew} deployed to site {site}")
	return deployment.name


@frappe.whitelist()
def get_active_deployments(site=None, project=None, date=None):
	if not date:
		date = frappe.utils.today()

	filters = {
		"status": "Active",
		"deployment_date": ["<=", date]
	}
	if site:
		filters["site"] = site
	if project:
		filters["project"] = project

	deployments = frappe.get_all("Site Deployment",
		filters=filters,
		fields=["name", "crew", "project", "site", "deployment_date", "expected_end_date", "work_description"]
	)

	for d in deployments:
		crew = frappe.get_doc("Crew", d.crew)
		d["member_count"] = len(crew.members)
		d["supervisor"] = crew.supervisor

	return deployments
