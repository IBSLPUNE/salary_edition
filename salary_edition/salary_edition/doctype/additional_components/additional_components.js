// Copyright (c) 2022, IBSL-IT and contributors
// For license information, please see license.txt

frappe.ui.form.on('Additional Components', {
	on_submit:function(frm){
		frappe.call({
			method:"salary_edition.salary_edition.ac.overtime",
			args:{employee: frm.doc.employee, date:frm.doc.date, overtime_days:frm.doc.overtime_days,incentive_days:frm.doc.incentive_days}
		})
	},
	overtime_days: function(frm){
	    let otd = frm.doc.overtime_days
	    if (otd > 6){
	        let id = otd - 6
	       frm.set_value('incentive_days',id)
	       frm.set_value('overtime_days',6)
	    }
	    
	}
});
