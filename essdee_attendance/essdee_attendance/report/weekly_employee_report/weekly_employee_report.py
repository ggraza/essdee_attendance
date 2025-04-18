# Copyright (c) 2013, Aerele and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, add_days, cstr, get_datetime

day_abbr = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns, data = [], []
	if not filters.from_date or not filters.to_date:
		frappe.throw("Set Date Range")
	
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data
	
def get_columns(filters):
	columns = [
		{"label": _("Employee"),"fieldname": "employee","fieldtype": "Link","options": "Employee","width": 115},
		{"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 120},
		{"label": _("Department"), "fieldname":"department","fieldtype":"Link","options":"Department","width": 120},
		{"label": _("Designation"), "fieldname":"designation","fieldtype":"Link","options":"Designation","width": 120},
		{"label": _("Employment Type"), "fieldname":"employment_type","fieldtype":"Link","options":"Employment Type","width": 120},
		{"label": _("Branch"), "fieldname":"branch","fieldtype":"Link","options":"Branch","width": 120},
	]
	if filters.select == "PF View":
		columns.extend([
			{"label": _("ESIC"), "fieldname": "esic", "fieldtype": "Data", "width": 100},
			{"label": _("UAN"), "fieldname": "uan", "fieldtype": "Data", "width": 100},
		])
		columns.extend(get_columns_for_days(filters))
		columns.extend([
			{"label": _("Total Working Days"), "fieldname": "total_working_days", "fieldtype": "Float", "width": 120},
			{"label": _("FL"), "fieldname": "fl", "fieldtype": "Float", "width": 120},
			{"label": _("Present Days"), "fieldname": "present_days", "fieldtype": "Float", "width": 120},
			{"label": _("CL"), "fieldname": "cl", "fieldtype": "Float", "width": 120},
			{"label": _("LOP Days"), "fieldname": "lop_days", "fieldtype": "Float", "width": 120},
			{"label": _("Payable Days"), "fieldname": "payable_days", "fieldtype": "Float", "width": 120},
			{"label": _("OT Shift"), "fieldname": "ot_shifts", "fieldtype": "Float", "width": 120},
			{"label": _("Fixed Salary"), "fieldname": "fixed_salary", "fieldtype": "Currency", "width": 120},
			{"label":_("Basic + DA"),"fieldname":"basic_da","fieldtype":"Currency","width":100},
			{"label":_("HRA"),"fieldname":"hra","fieldtype":"Currency","width":100},
			{"label":_("Others"),"fieldname":"others","fieldtype":"Currency","width":100},
			{"label":_("Payable Basic + DA"),"fieldname":"payable_basic_da","fieldtype":"Currency","width":100},
			{"label":_(" Payable HRA"),"fieldname":"payable_hra","fieldtype":"Currency","width":100},
			{"label":_("Payable Others"),"fieldname":"payable_others","fieldtype":"Currency","width":100},
			{"label":_("PF Salary"),"fieldname":"pf_salary","fieldtype":"Currency","width":100},
			{"label":_("OT Salary"),"fieldname":"ot_salary","fieldtype":"Currency","width":100},
			{"label":_("Gross Salary"),"fieldname":"gross_salary","fieldtype":"Currency","width":100},
			{"label":_("ESI"),"fieldname":"esi","fieldtype":"Currency","width":100},
			{"label":_("PF"),"fieldname":"pf","fieldtype":"Currency","width":100},
			{"label":_("PT"),"fieldname":"pt","fieldtype":"Currency","width":100},
			{"label":_("Welfare Fund"),"fieldname":"welfare_fund","fieldtype":"Currency","width":100},
			{"label":_("Lunch"),"fieldname":"lunch","fieldtype":"Currency","width":100},
			{"label":_("CUG"),"fieldname":"cug","fieldtype":"Currency","width":100},
			{"label":_("Advance"),"fieldname":"advance","fieldtype":"Currency","width":100},
			{"label":_("LIC"),"fieldname":"lic","fieldtype":"Currency","width":100},
			{"label":_("Total Deduction"),"fieldname":"total_deduction","fieldtype":"Currency","width":100},
			{"label":_("Take Home"),"fieldname":"take_home","fieldtype":"Currency","width":100},
		])
	elif filters.select == "Summarized Report":
		columns.extend([
			{"label": _("Shift"), "fieldname": "shift", "fieldtype": "Data", "width": 100},
			{"label": _("No. of Shifts"), "fieldname": "shift_count", "fieldtype": "Float", "width": 120},
			{"label": _("Rate"), "fieldname": "rate", "fieldtype": "Float", "width": 120},
			{"label": _("Amount"), "fieldname": "amount", "fieldtype": "Float", "width": 120},
		])
	else:
		columns.extend(get_columns_for_days(filters))	
	return columns

def get_columns_for_days(filters):
	days = []
	date = getdate(filters.from_date)
	to_date = getdate(filters.to_date)
	
	while date <= to_date:
		weekday = day_abbr[date.weekday()]
		label = "{} {}".format(cstr(date.day), weekday)
		days.append({"label": label, "fieldtype": "Data", "fieldname": date.isoformat(), "width": 145})
		date = add_days(date, 1)
	return days

def get_data(filters):
	data = []
	employees = get_employees(filters)
	attendance_records = get_attendance_map(filters)
	attendance_records = get_checkin_map(attendance_records, filters)
	for employee in employees:
		d = {
			'employee': employee.name,
			'employee_name': employee.employee_name,
			"department":employee.department,
			"designation":employee.designation,
			"employment_type":employee.employment_type,
			"branch":employee.branch,
		}
		if filters.select == "PF View":
			get_pf_detail(d, filters, employee, attendance_records.get(employee.name))
		elif filters.select == "Summarized Report":
			get_summarized_detail(d, filters, employee, attendance_records.get(employee.name))
		elif filters.select == "Day Wise Report":
			get_employee_detail(d, filters, employee, attendance_records.get(employee.name))	
		data.append(d)
	return data

def get_summarized_detail(data, filters, employee, attendance_records):
	if attendance_records:
		total_shift = 0
		for date, value in attendance_records.items():
			total_shift += (value.get('sd_no_of_shifts') or 0)
		data.update({
			'shift_count': total_shift,
			'rate': employee.sd_shift_rate,
			"shift": employee.default_shift,
			'amount': total_shift * (employee.sd_shift_rate or 0)
		})
	else:
		data.update({
			'rate': employee.sd_shift_rate,
			"shift": employee.default_shift,
			'amount': 0
		})	

def get_pf_detail(data, filters, employee, attendance_records):
	if attendance_records:
		general_shift = 0
		ot_shift = 0
		no_of_shifts = 0
		for date, value in attendance_records.items():
			no_of_shifts += (value.get('sd_no_of_shifts') or 0)
			general_shift += (value.get('general_shifts') or 0)
			ot_shift += (value.get('ot_shifts') or 0)
			data[date] = str(value.get('sd_no_of_shifts') or 0)

		holiday = frappe.get_value("Shift Type", employee.default_shift, "holiday_list")
		holiday_doc = frappe.get_doc("Holiday List", holiday)
		week_offs = 0
		fl = 0		
		for day in holiday_doc.holidays:
			d = getdate(day.holiday_date)
			d1 = getdate(filters.from_date)
			d2 = getdate(filters.to_date)
			if d >= d1 and d <= d2 and day.weekly_off:
				week_offs += 1
			elif d >= d1 and d <= d2:
				fl += 1

		total_days = getdate(filters.to_date) - getdate(filters.from_date)
		total_days = total_days.days
		total_working_days = total_days - week_offs
		present_days = general_shift
		cl = 0
		payable_days = present_days + cl
		lop_days = total_working_days - payable_days
		fixed_salary = employee.sd_shift_wages
		basic_da = employee.sd_minimum_wages
		hra = fixed_salary - basic_da
		others = 0
		payable_basic_da = payable_days * basic_da
		payable_hra = payable_days * hra
		payable_others = payable_days * others
		pf_salary = payable_basic_da + payable_hra
		ot_salary = ot_shift * fixed_salary
		gross_salary = pf_salary + ot_salary + payable_others
		esi = gross_salary / 100
		esi = esi * 0.75
		pf = pf_salary / 100
		pf = pf * 12
		month_count = round(total_days/30)
		welfare_fund = frappe.db.get_single_value("Essdee Attendance Settings", "welfare_fund")
		welfare_fund = welfare_fund * month_count
		pt = 0
		lunch = 0
		cug = 0
		advance = 0
		lic = 0
		total_deduction = esi + pf + pt + welfare_fund
		take_home = gross_salary - total_deduction
		data.update({
			"uan": employee.sd_uan,
			"esic": employee.sd_esic,
			"total_working_days": total_working_days,
			"fl": fl,
			"present_days": present_days,
			"cl": cl,
			"lop_days": lop_days,
			"payable_days": payable_days,
			"ot_shifts": ot_shift,
			"fixed_salary": fixed_salary,
			"basic_da": basic_da,
			"hra": hra,
			"others": others,
			"payable_basic_da": payable_basic_da,
			"payable_hra": payable_hra,
			"payable_others": payable_others,
			"pf_salary": pf_salary,
			"ot_salary": ot_salary,
			"gross_salary": gross_salary,
			"esi": esi,
			"pf": pf,
			"pt": pt,
			"welfare_fund": welfare_fund,
			"lunch": lunch,
			"cug": cug,
			"advance": advance,
			"lic": lic,
			"total_deduction": total_deduction,
			"take_home": take_home,
		})

def get_employee_detail(data, filters, employee, attendance_records):
	if attendance_records:
		for date, value in attendance_records.items():
			detail = []
			if filters.show_in_out:
				in_time = None
				out_time = None
				if value.get('in_time'):
					in_time = value['in_time'].strftime("%H:%M")
				if value.get('out_time'):
					out_time = value['out_time'].strftime("%H:%M")
				detail.append("{} - {}".format(in_time, out_time))
			if filters.show_time_logs:
				detail.append(", ".join(value.get('checkin') or []))
			if filters.show_hours:
				detail.append("{} - {} hrs".format(value.get('status') or '', value.get('working_hours') or 0))
			if filters.show_shift:
				detail.append(str(value.get('sd_no_of_shifts') or 0))
			if filters.show_general_ot_shift:
				str1 = str(value.get('general_shifts') or 0) 
				str2 = str(value.get('ot_shifts') or 0)
				str3 = str1 + "-" + str2
				detail.append(str3)
			data[date] = "<br>".join(detail)

def get_employees(filters):
	Employee = frappe.qb.DocType("Employee")
	
	query = frappe.qb.from_(Employee).select(
		Employee.name, 
		Employee.employee_name, 
		Employee.default_shift,
		Employee.sd_shift_rate, 
		Employee.sd_shift_wages,
		Employee.sd_minimum_wages,
		Employee.department,
		Employee.designation,
		Employee.employment_type,
		Employee.sd_uan,
		Employee.sd_esic,
		Employee.branch
	)
	query = apply_employee_filters(query, filters, Employee)
	return query.run(as_dict = 1)

def get_attendance_map(filters):
	attendance_list = get_attendance_records(filters)
	attendance_map = {}

	for d in attendance_list:
		attendance_map.setdefault(d.employee, {})
		attendance_map[d.employee][d.attendance_date.isoformat()] = {
			'employee_name': d.employee_name,
			'status': d.status,
			'shift': d.shift,
			'sd_no_of_shifts': d.sd_no_of_shifts,
			'in_time': d.in_time,
			'out_time': d.out_time,
			'working_hours': d.working_hours,
			'general_shifts': d.sd_general_shifts,
			'ot_shifts':d.sd_ot_shifts,
		}

	return attendance_map

def get_attendance_records(filters):
	Attendance = frappe.qb.DocType("Attendance")
	Employee = frappe.qb.DocType("Employee")
	
	query = (
		frappe.qb.from_(Attendance).from_(Employee)
		.select(
			Attendance.employee,
			Attendance.attendance_date,
			Attendance.status,
			Attendance.shift,
			Attendance.sd_no_of_shifts,
			Attendance.in_time,
			Attendance.out_time,
			Attendance.working_hours,
			Attendance.sd_general_shifts,
			Attendance.sd_ot_shifts,
		).where(
			(Attendance.docstatus == 1)
			& (Attendance.company == filters.company)
			& (Attendance.attendance_date >= filters.from_date)
			& (Attendance.attendance_date <= filters.to_date)
			& (Attendance.employee == Employee.name)
		)
	)

	query = apply_employee_filters(query, filters, Employee)
	query = query.orderby(Attendance.employee, Attendance.attendance_date)

	return query.run(as_dict=1)

def get_checkin_map(attendance_records, filters):
	if not filters.show_time_logs:
		return attendance_records
	checkin_list = get_check_in_records(filters)

	for d in checkin_list:
		date = getdate(d.time).isoformat()
		attendance_records.setdefault(d.employee, {}).setdefault(date, {}).setdefault('checkin', [])
		attendance_records[d.employee][date]['checkin'].append(d.time.strftime("%H:%M"))

	return attendance_records

def get_check_in_records(filters):
	EmployeeCheckin = frappe.qb.DocType("Employee Checkin")
	Employee = frappe.qb.DocType("Employee")
	
	query = (
		frappe.qb.from_(EmployeeCheckin).from_(Employee)
		.select(
			EmployeeCheckin.employee,
			EmployeeCheckin.time,
		).where(
			(EmployeeCheckin.attendance.notnull())
			& (EmployeeCheckin.time >= filters.from_date)
			& (EmployeeCheckin.time <= filters.to_date)
			& (EmployeeCheckin.employee == Employee.name)
		)
	)

	query = apply_employee_filters(query, filters, Employee)
	query = query.orderby(EmployeeCheckin.employee, EmployeeCheckin.time)

	return query.run(as_dict=1)

def apply_employee_filters(query, filters, Employee):
	if filters.employee:
		query = query.where(Employee.name == filters.employee)
	if filters.shift:
		query = query.where(Employee.default_shift == filters.shift)
	if filters.department:
		query = query.where(Employee.department == filters.department)
	if filters.branch:
		query = query.where(Employee.branch == filters.branch)
	if filters.employment_type:
		query = query.where(Employee.employment_type == filters.employment_type)
	if filters.status:
		if filters.status == "Active":
			query = query.where(Employee.status == "Active")
		else:
			query = query.where(Employee.status != "Active")
	return query
