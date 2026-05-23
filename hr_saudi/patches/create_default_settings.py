import frappe


def execute():
    """Create default Attendance Settings if not exists"""
    
    if not frappe.db.exists("DocType", "Attendance Settings"):
        print("Attendance Settings DocType not found")
        return
    
    if not frappe.db.exists("Attendance Settings", "Attendance Settings"):
        settings = frappe.new_doc("Attendance Settings")
        settings.late_threshold = 15
        settings.half_day_threshold = 60
        settings.ot_multiplier = 1.5
        settings.auto_generate_attendance = 1
        settings.insert()
        frappe.db.commit()
        print("✅ Created default Attendance Settings")
    else:
        print("Attendance Settings already exists")
    
    # Create default Saudization Settings
    if not frappe.db.exists("DocType", "Saudization Settings"):
        print("Saudization Settings DocType not found")
        return
    
    if not frappe.db.exists("Saudization Settings", "Saudization Settings"):
        saudization = frappe.new_doc("Saudization Settings")
        saudization.activity_type = "Construction"
        saudization.nitaqat_category = "Mid Green"
        saudization.target_saudi_ratio = 20.0
        saudization.insert()
        frappe.db.commit()
        print("✅ Created default Saudization Settings")
    else:
        print("Saudization Settings already exists")
    
    print("✅ Default setup complete!")
