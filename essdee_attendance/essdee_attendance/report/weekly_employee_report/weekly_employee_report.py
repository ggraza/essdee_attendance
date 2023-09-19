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
		{
			"label": _("Employee"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 115,
		},
		{"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 120},
	]
	if not filters.summarized_view:
		columns.extend(get_columns_for_days(filters))
	else:
		columns.extend([
			{"label": _("Shift"), "fieldname": "shift", "fieldtype": "Data", "width": 65},
			{"label": _("No. of Shifts"), "fieldname": "shift_count", "fieldtype": "Float", "width": 120},
			{"label": _("Rate"), "fieldname": "rate", "fieldtype": "Float", "width": 120},
			{"label": _("Amount"), "fieldname": "amount", "fieldtype": "Float", "width": 120},
		])
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
			'employee_name': employee.employee_name
		}
		if not filters.summarized_view:
			get_employee_detail(d, filters, employee, attendance_records.get(employee.name))
		else:
			get_summarized_detail(d, filters, employee, attendance_records.get(employee.name))
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
			'amount': total_shift * (employee.sd_shift_rate or 0)
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
				detail.append("{} - {}".format(value.get('status') or '', value.get('working_hours') or 0))
			if filters.show_shift:
				detail.append(str(value.get('sd_no_of_shifts') or 0))
			data[date] = "<br>".join(detail)

def get_employees(filters):
	Employee = frappe.qb.DocType("Employee")
	
	query = frappe.qb.from_(Employee).select(Employee.name, Employee.employee_name, Employee.sd_shift_rate)
	if filters.employee:
		query = query.where(Employee.name == filters.employee)
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
		}

	return attendance_map

def get_attendance_records(filters):
	Attendance = frappe.qb.DocType("Attendance")
	
	query = (
		frappe.qb.from_(Attendance)
		.select(
			Attendance.employee,
			Attendance.attendance_date,
			Attendance.status,
			Attendance.shift,
			Attendance.sd_no_of_shifts,
			Attendance.in_time,
			Attendance.out_time,
			Attendance.working_hours,
		).where(
			(Attendance.docstatus == 1)
			& (Attendance.company == filters.company)
			& (Attendance.attendance_date >= filters.from_date)
			& (Attendance.attendance_date <= filters.to_date)
		)
	)
	
	if filters.employee:
		query = query.where(Attendance.employee == filters.employee)
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
	
	query = (
		frappe.qb.from_(EmployeeCheckin)
		.select(
			EmployeeCheckin.employee,
			EmployeeCheckin.time,
		).where(
			(EmployeeCheckin.attendance.notnull())
			& (EmployeeCheckin.time >= filters.from_date)
			& (EmployeeCheckin.time <= filters.to_date)
		)
	)
	
	if filters.employee:
		query = query.where(EmployeeCheckin.employee == filters.employee)
	query = query.orderby(EmployeeCheckin.employee, EmployeeCheckin.time)

	return query.run(as_dict=1)
