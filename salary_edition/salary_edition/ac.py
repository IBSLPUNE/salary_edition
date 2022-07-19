import frappe
from datetime import date
from dateutil.relativedelta import relativedelta
from frappe.utils import date_diff
from erpnext.hr.utils import get_holiday_dates_for_employee, validate_active_employee



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
	if self.incentive_days != 0:
		incentive_days = float(self.incentive_days)
		incentive = round(per_day*(incentive_days))
		additional_salary= frappe.get_doc({
			'doctype': 'Additional Salary',
			'employee': self.employee,
			'salary_component':'Special Incentive',
			'type':'Earning',
			'payroll_date': self.date,
			'amount': incentive,
			'overwrite_salary_structure_amount':1,
			'naming_series': 'HR-ADS-.YY.-.MM.-',
			})
		additional_salary.insert()
		additional_salary.submit()

@frappe.whitelist()
def bonus(start_date, end_date):
	employee = frappe.get_list("Employee", pluck='name', filters={'status':'Active','date_of_joining':["<=",start_date]})
	for i in employee:
		additional_salary = frappe.get_list('Additional Salary', filters={'docstatus':1,'employee':i,'salary_component':'Bonus','payroll_date':["Between",[start_date,end_date]]})
		if additional_salary:
			continue
		total_leave = 0.0
		working_days = date_diff(end_date ,start_date) +1
		payment_days = working_days
		holidays = get_holidays_for_employee(i,start_date, end_date)
		absent, lwp = cal_absent(i,start_date,end_date)

		marked_days = frappe.get_all("Attendance", filters = {
					'attendance_date': ["between", [start_date, end_date]],
					"employee": i,
					"docstatus": 1
				}, fields = ["COUNT(*) as marked_days"])[0].marked_days
		unmarked_days = working_days - marked_days
		payment_days = working_days - absent - lwp
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

def get_holidays_for_employee(employee,start_date, end_date):
	return get_holiday_dates_for_employee(employee, start_date, end_date)

def cal_absent(employee, start_date, end_date):
	absent = 0
	lwp = 0
	leave_types = frappe.get_all("Leave Type",
			or_filters=[["is_ppl", "=", 1], ["is_lwp", "=", 1]],
			fields =["name", "is_lwp", "is_ppl", "fraction_of_daily_salary_per_leave", "include_holiday"])
	leave_type_map = {}
	for leave_type in leave_types:
		leave_type_map[leave_type.name] = leave_type
	attendances = frappe.db.sql('''
			SELECT attendance_date , status , leave_type
			FROM `tabAttendance`
			WHERE
				status in ("Absent", "On Leave")
				AND employee = %s
				AND docstatus = 1
				AND attendance_date between %s and %s
		''', values=(employee, start_date, end_date), as_dict=1)
	for d in attendances:
		if d.status =='Absent':
			absent += 1
		elif d.status == "On Leave" and d.leave_type =='Leave Without Pay':
			equivalent_lwp = 1
			if leave_type_map[d.leave_type]["is_ppl"]:
				equivalent_lwp *= fraction_of_daily_salary_per_leave if fraction_of_daily_salary_per_leave else 1
			lwp += equivalent_lwp


	return absent , lwp


# if flt(payment_days) > flt(lwp):
# 			self.payment_days = flt(payment_days) - flt(lwp)

# 			if payroll_based_on == "Attendance":
# 				self.payment_days -= flt(absent)

# 			unmarked_days = self.get_unmarked_days()
# 			consider_unmarked_attendance_as = frappe.db.get_value("Payroll Settings", None, "consider_unmarked_attendance_as") or "Present"

# 			if payroll_based_on == "Attendance" and consider_unmarked_attendance_as =="Absent":
# 				self.absent_days += unmarked_days #will be treated as absent
# 				self.payment_days -= unmarked_days
# 				if include_holidays_in_total_working_days:
# 					for holiday in holidays:
# 						if not frappe.db.exists("Attendance", {"employee": self.employee, "attendance_date": holiday, "docstatus": 1 }):
# 							self.payment_days += 1

# def get_unmarked_days(employee, start_date, end_date):
# 		marked_days = frappe.get_all("Attendance", filters = {
# 					"attendance_date": ["Between", [start_date, end_date]],
# 					"employee": employee,
# 					"docstatus": 1
# 				}, fields = ["COUNT(*) as marked_days"])[0].marked_days

# 		return total_working_days - marked_days

def calculate_lwp_ppl_and_absent_days_based_on_attendance(holidays):
		lwp = 0
		absent = 0

		daily_wages_fraction_for_half_day = \
			flt(frappe.db.get_value("Payroll Settings", None, "daily_wages_fraction_for_half_day")) or 0.5

		leave_types = frappe.get_all("Leave Type",
			or_filters=[["is_ppl", "=", 1], ["is_lwp", "=", 1]],
			fields =["name", "is_lwp", "is_ppl", "fraction_of_daily_salary_per_leave", "include_holiday"])

		leave_type_map = {}
		for leave_type in leave_types:
			leave_type_map[leave_type.name] = leave_type

		attendances = frappe.db.sql('''
			SELECT attendance_date, status, leave_type
			FROM `tabAttendance`
			WHERE
				status in ("Absent", "Half Day", "On leave")
				AND employee = %s
				AND docstatus = 1
				AND attendance_date between %s and %s
		''', values=(self.employee, self.start_date, self.end_date), as_dict=1)

		for d in attendances:
			if d.status in ('Half Day', 'On Leave') and d.leave_type and d.leave_type not in leave_type_map.keys():
				continue

			if formatdate(d.attendance_date, "yyyy-mm-dd") in holidays:
				if d.status == "Absent" or \
					(d.leave_type and d.leave_type in leave_type_map.keys() and not leave_type_map[d.leave_type]['include_holiday']):
						continue

			if d.leave_type:
				fraction_of_daily_salary_per_leave = leave_type_map[d.leave_type]["fraction_of_daily_salary_per_leave"]

			if d.status == "Half Day":
				equivalent_lwp =  (1 - daily_wages_fraction_for_half_day)

				if d.leave_type in leave_type_map.keys() and leave_type_map[d.leave_type]["is_ppl"]:
					equivalent_lwp *= fraction_of_daily_salary_per_leave if fraction_of_daily_salary_per_leave else 1
				lwp += equivalent_lwp
			elif d.status == "On Leave" and d.leave_type == 'Leave Without Pay':
				lwp += 1
			elif d.status == "Absent":
				absent += 1
			print(d.status)
		return lwp, absent