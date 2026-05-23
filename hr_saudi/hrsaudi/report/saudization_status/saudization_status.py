import frappe
from frappe import _


def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	summary = get_summary(data)

	return columns, data, None, chart, summary


def get_columns():
	return [
		{
			"label": _("Company"),
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"width": 120
		},
		{
			"label": _("Department"),
			"fieldname": "department",
			"fieldtype": "Link",
			"options": "Department",
			"width": 120
		},
		{
			"label": _("Total Employees"),
			"fieldname": "total_employees",
			"fieldtype": "Int",
			"width": 120
		},
		{
			"label": _("Saudi Employees"),
			"fieldname": "saudi_employees",
			"fieldtype": "Int",
			"width": 120
		},
		{
			"label": _("Expat Employees"),
			"fieldname": "expat_employees",
			"fieldtype": "Int",
			"width": 120
		},
		{
			"label": _("Saudi Ratio (%)"),
			"fieldname": "saudi_ratio",
			"fieldtype": "Percent",
			"width": 120
		},
		{
			"label": _("Target Ratio (%)"),
			"fieldname": "target_ratio",
			"fieldtype": "Percent",
			"width": 120
		},
		{
			"label": _("Compliance Status"),
			"fieldname": "compliance_status",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Nitaqat Category"),
			"fieldname": "nitaqat_category",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Required to Meet Target"),
			"fieldname": "required_to_meet_target",
			"fieldtype": "Int",
			"width": 150
		}
	]


def get_data(filters):
	conditions = get_conditions(filters)
	
	companies = frappe.get_all("Company", filters={"is_group": 0})
	
	data = []
	
	for company in companies:
		# Get settings
		settings = frappe.get_doc("Saudization Settings")
		target_ratio = settings.target_saudi_ratio or 0
		nitaqat_category = settings.nitaqat_category or "N/A"
		
		# Get employee counts
		total = frappe.db.count("Employee", {"company": company.name, "status": "Active"})
		saudi = frappe.db.count("Employee", {"company": company.name, "status": "Active", "nationality": "Saudi"})
		expat = total - saudi
		
		saudi_ratio = (saudi / total * 100) if total > 0 else 0
		
		# Determine compliance
		if saudi_ratio >= target_ratio:
			compliance_status = "Compliant"
		elif saudi_ratio >= (target_ratio * 0.8):
			compliance_status = "At Risk"
		else:
			compliance_status = "Non-Compliant"
			
		# Calculate required
		required = int((target_ratio / 100) * total) - saudi
		if required < 0:
			required = 0
			
		data.append({
			"company": company.name,
			"department": filters.get("department"),
			"total_employees": total,
			"saudi_employees": saudi,
			"expat_employees": expat,
			"saudi_ratio": saudi_ratio,
			"target_ratio": target_ratio,
			"compliance_status": compliance_status,
			"nitaqat_category": nitaqat_category,
			"required_to_meet_target": required
		})
		
	return data


def get_conditions(filters):
	conditions = ""
	if filters.get("company"):
		conditions += " AND company = %(company)s"
	if filters.get("department"):
		conditions += " AND department = %(department)s"
	return conditions


def get_chart_data(data):
	if not data:
		return None
		
	labels = [d["company"] for d in data]
	saudi = [d["saudi_employees"] for d in data]
	expat = [d["expat_employees"] for d in data]
	
	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": "Saudi Employees", "values": saudi},
				{"name": "Expat Employees", "values": expat}
			]
		},
		"type": "bar",
		"colors": ["#7cd6fd", "orange"]
	}


def get_summary(data):
	if not data:
		return []
		
	total_saudi = sum(d["saudi_employees"] for d in data)
	total_expat = sum(d["expat_employees"] for d in data)
	total = total_saudi + total_expat
	ratio = (total_saudi / total * 100) if total > 0 else 0
	
	return [
		{"value": total, "label": _("Total Employees"), "datatype": "Int"},
		{"value": total_saudi, "label": _("Saudi Employees"), "datatype": "Int"},
		{"value": f"{ratio:.1f}%", "label": _("Saudi Ratio"), "datatype": "Data"},
	]
