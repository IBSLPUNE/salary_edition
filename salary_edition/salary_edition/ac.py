import frappe
from erpnext.payroll.doctype.salary_slip.salary_slip import SalarySlip

@frappe.whitelist()
def overtime(employee, date,overtime_days,incentive_days):
	amt = 0.0
	print(overtime_days)
	overtime_days = float(overtime_days)
	print(overtime_days)
	amt = frappe.get_value('Salary Structure Assignment',{'employee':employee},'base')
	if amt == None:
		frappe.throw("Salary Structure Not Assigned To The"+employee)
	per_day = (amt/301)*12
	ot = round(per_day*(overtime_days*2))

	additional_salary= frappe.get_doc({
		'doctype': 'Additional Salary',
		'employee': employee,
		'salary_component':'Over Time',
		'type':'Earning',
		'payroll_date': date,
		'amount':ot,
		'overwrite_salary_structure_amount':1,
		'naming_series': 'HR-ADS-.YY.-.MM.-',
		})
	additional_salary.insert()
	additional_salary.submit()