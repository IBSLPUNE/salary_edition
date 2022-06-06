import frappe
from erpnext.payroll.doctype.salary_slip.salary_slip import SalarySlip



def overtime(self, method):
	amt = 0.0
	overtime_days = float(self.overtime_days)
	print(overtime_days)
	amt = frappe.get_value('Salary Structure Assignment',{'employee':self.employee},'base')
	if amt == None:
		frappe.throw("Salary Structure Not Assigned To The"+self.employee)
	per_day = (amt/365)*12
	ot = round(per_day*(overtime_days*2))

	additional_salary= frappe.get_doc({
		'doctype': 'Additional Salary',
		'employee': self.employee,
		'salary_component':'Over Time',
		'type':'Earning',
		'payroll_date': self.date,
		'amount': ot,
		'overwrite_salary_structure_amount':1,
		'naming_series': 'HR-ADS-.YY.-.MM.-',
		})
	additional_salary.insert()
	additional_salary.submit()
