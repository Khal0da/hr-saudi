frappe.ui.form.on('Attendance', {
	refresh: function(frm) {
		if (frm.doc.custom_late_minutes) {
			frm.set_df_property('custom_late_minutes', 'description',
				`Late by ${frm.doc.custom_late_minutes} minutes`);
		}
	},
	validate: function(frm) {
		if (frm.doc.custom_ot_hours && frm.doc.custom_ot_hours < 0) {
			frappe.throw('OT Hours cannot be negative');
		}
	}
});

frappe.ui.form.on('Payroll Entry', {
	custom_branch: function(frm) {
		if (frm.doc.custom_branch) {
			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Branch',
					filters: { name: frm.doc.custom_branch },
					fieldname: 'cost_center'
				},
				callback: function(r) {
					if (r.message && r.message.cost_center) {
						frm.set_value('custom_branch_cost_center', r.message.cost_center);
					}
				}
			});
		}
	}
});
