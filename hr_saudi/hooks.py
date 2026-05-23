from . import __version__ as app_version

app_name = "hr_saudi"
app_title = "HR Saudi"
app_publisher = "Al Metaeb Investment"
app_description = "Enterprise Workforce Platform for Construction & Hotel Operations on ERPNext"
app_icon = "octicon octicon-organization"
app_color = "green"
app_email = "info@almetaeb.com.sa"
app_license = "MIT"
app_version = "1.0.0"

required_apps = ["erpnext", "construction_app"]

before_install = "hr_saudi.hrsaudi.setup.before_install"
after_install = "hr_saudi.hrsaudi.setup.after_install"
after_migrate = "hr_saudi.hrsaudi.setup.after_migrate"

app_include_js = ["hr_saudi.bundle.js"]

scheduler_events = {
	"daily": [
		"hr_saudi.hrsaudi.attendance.generator.generate_daily_attendance",
		"hr_saudi.hrsaudi.notification.document_expiry.check_expiring_documents",
		"hr_saudi.hrsaudi.doctype.saudization_settings.saudization_settings.update_daily_compliance",
		"hr_saudi.hrsaudi.attendance.ot_calculator.calculate_daily_ot",
	],
	"hourly": [
		"hr_saudi.hrsaudi.attendance.ot_calculator.calculate_pending_ot",
	],
	"cron": {
		"0 23 * * *": [
			"hr_saudi.hrsaudi.attendance.generator.generate_end_of_day_attendance",
		],
	},
}

custom_fields = {
	"Employee": [
		{
			"fieldname": "passport_number",
			"label": "Passport Number",
			"fieldtype": "Data",
			"insert_after": "national_id_expiry"
		},
		{
			"fieldname": "passport_expiry",
			"label": "Passport Expiry Date",
			"fieldtype": "Date",
			"insert_after": "passport_number"
		},
		{
			"fieldname": "work_permit_number",
			"label": "Work Permit Number",
			"fieldtype": "Data",
			"insert_after": "passport_expiry"
		},
		{
			"fieldname": "work_permit_expiry",
			"label": "Work Permit Expiry",
			"fieldtype": "Date",
			"insert_after": "work_permit_number"
		},
		{
			"fieldname": "health_certificate_no",
			"label": "Health Certificate No",
			"fieldtype": "Data",
			"insert_after": "work_permit_expiry"
		},
		{
			"fieldname": "health_certificate_expiry",
			"label": "Health Certificate Expiry",
			"fieldtype": "Date",
			"insert_after": "health_certificate_no"
		},
		{
			"fieldname": "employee_grade",
			"label": "Employee Grade",
			"fieldtype": "Select",
			"options": "\nA-Executive\nB-Management\nC-Professional\nD-Technical\nE-Skilled\nF-Unskilled",
			"insert_after": "designation"
		},
		{
			"fieldname": "labor_camp",
			"label": "Labor Camp",
			"fieldtype": "Link",
			"options": "Labor Camp",
			"insert_after": "branch"
		},
		{
			"fieldname": "bed_number",
			"label": "Bed Number",
			"fieldtype": "Data",
			"insert_after": "labor_camp"
		}
	],
	"Attendance": [
		{
			"fieldname": "custom_project",
			"label": "Project",
			"fieldtype": "Link",
			"options": "Project",
			"insert_after": "employee"
		},
		{
			"fieldname": "custom_shift_type",
			"label": "Shift Type",
			"fieldtype": "Link",
			"options": "Shift Type",
			"insert_after": "custom_project"
		},
		{
			"fieldname": "custom_late_minutes",
			"label": "Late Minutes",
			"fieldtype": "Int",
			"insert_after": "custom_shift_type"
		},
		{
			"fieldname": "custom_ot_hours",
			"label": "OT Hours",
			"fieldtype": "Float",
			"insert_after": "custom_late_minutes"
		},
		{
			"fieldname": "custom_source",
			"label": "Source",
			"fieldtype": "Select",
			"options": "\nBiometric Device\nMobile GPS\nManual\nSystem",
			"insert_after": "custom_ot_hours"
		},
		{
			"fieldname": "custom_geo_fence",
			"label": "Geo Fence",
			"fieldtype": "Link",
			"options": "Geo Fence",
			"insert_after": "custom_source"
		}
	],
	"Salary Slip": [
		{
			"fieldname": "custom_project",
			"label": "Project",
			"fieldtype": "Link",
			"options": "Project",
			"insert_after": "employee"
		},
		{
			"fieldname": "custom_gosi_employee_amount",
			"label": "GOSI Employee Amount",
			"fieldtype": "Currency",
			"insert_after": "custom_project",
			"read_only": 1
		},
		{
			"fieldname": "custom_gosi_employer_amount",
			"label": "GOSI Employer Amount",
			"fieldtype": "Currency",
			"insert_after": "custom_gosi_employee_amount",
			"read_only": 1
		},
		{
			"fieldname": "custom_wps_batch",
			"label": "WPS Batch",
			"fieldtype": "Link",
			"options": "WPS Batch",
			"insert_after": "custom_gosi_employer_amount",
			"read_only": 1
		}
	],
	"Payroll Entry": [
		{
			"fieldname": "custom_branch",
			"label": "Branch",
			"fieldtype": "Link",
			"options": "Branch",
			"insert_after": "company",
			"description": "Leave empty to include all branches"
		},
		{
			"fieldname": "custom_branch_cost_center",
			"label": "Branch Cost Center",
			"fieldtype": "Link",
			"options": "Cost Center",
			"insert_after": "custom_branch",
			"read_only": 1
		}
	]
}

doc_events = {
	"Employee": {
		"validate": "hr_saudi.hrsaudi.doctype.document_expiry_tracker.document_expiry_tracker.validate_expiry_dates",
	},
	"Attendance": {
		"validate": "hr_saudi.hrsaudi.attendance.validator.validate_attendance",
	},
	"Payroll Entry": {
		"before_submit": "hr_saudi.hrsaudi.api.payroll.validate_branch_payroll",
	}
}
