import frappe
from datetime import date
from dateutil.relativedelta import relativedelta
from frappe.utils import date_diff



def overtime(self, method):
	amt = 0.0
	overtime_days = float(self.overtime_days)
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

@frappe.whitelist()
def bonus(start_date, end_date):
	employee = frappe.get_list("Employee", pluck='name', filters={'status':'Active','date_of_joining':["<=",start_date]})
	print(employee)
	for i in employee:
		total_leave = 0.0
		# end_date = date(2022,5,26)
		# start_date = end_date - relativedelta(months=+1)
		# end_date = end_date - relativedelta(days=+1)
		working_days = date_diff(end_date ,start_date) +1
		leave_without_pay = frappe.db.sql_list("""SELECT total_leave_days FROM `tabLeave Application` WHERE employee = %s""",i)
		for l in leave_without_pay:
			total_leave = total_leave + l
		payment_days = working_days - total_leave
		if payment_days >= working_days * .85:
			amt = frappe.get_value('Salary Structure Assignment',{'employee':i},'base')
			if amt == None:
				frappe.throw("Salary Structure Not Assigned To "+i)
			bonus = round((amt/working_days*payment_days)*0.0833)
			additional_salary= frappe.get_doc({
				'doctype': 'Additional Salary',
				'employee': i,
				'salary_component':'Bonus',
				'type':'Earning',
				'payroll_date': start_date,
				'amount': bonus,
				'overwrite_salary_structure_amount':1,
				'naming_series': 'HR-ADS-.YY.-.MM.-',
				})
			additional_salary.insert()
			additional_salary.submit()