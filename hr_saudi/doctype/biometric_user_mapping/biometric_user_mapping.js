frappe.ui.form.on('Biometric User Mapping', {
	refresh: function(frm) {
		if (!frm.doc.registered_date) {
			frm.set_value('registered_date', frappe.datetime.get_today());
		}
	}
});
