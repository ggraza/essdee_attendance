# Copyright (c) 2025, Aerele and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days, getdate, flt
from frappe.query_builder.functions import Sum
from essdee_attendance.essdee_attendance.hrms_logger import get_module_logger

class EssdeeShiftCalculation(Document):
	pass

@frappe.whitelist()
def calculate_wages(doc_name):
	doc = frappe.get_doc("Essdee Shift Calculation", doc_name)
	doc.calculating = 1
	doc.save()
	# calc(doc_name)
	frappe.enqueue(calc, doc_name=doc_name, timeout=600)

def calc(doc_name):
	try:
		logger = get_module_logger()
		doc = frappe.get_doc("Essdee Shift Calculation", doc_name)
		employee_list = frappe.get_list("Employee", filters=doc.filters_json, pluck="name")
		logger.debug(employee_list)
		from_date = str(getdate(doc.start_date))
		to_date = str(getdate(doc.end_date))
		employeeTab = frappe.qb.DocType("Employee")
		attendanceTab = frappe.qb.DocType("Attendance")
		employees = (
			frappe.qb.from_(employeeTab).select(employeeTab.name)
			.join(attendanceTab)
			.on(attendanceTab.employee == employeeTab.name)
			.where(
				# (employeeTab.default_shift == shift_type)
				(attendanceTab.attendance_date >= from_date)
				& (attendanceTab.attendance_date <= to_date)
				& (attendanceTab.status.notin(["Absent", "On Leave"]))
				& (employeeTab.name.isin(employee_list))
			)
			.groupby(employeeTab.name)
			.having(Sum(attendanceTab.sd_no_of_shifts) > 0)
			.run(as_list=True)
		)
		logger.debug(employees)
		# employee_list = frappe.get_list("Employee", filters={"default_shift":shift_type}, pluck="name")
		no_shift_rate = []
		no_shift_wages = []
		if not employees:
			frappe.throw("No employess had attendance on this selected range")
		for employee in employees:
			employee = employee[0]
			shift_rate, shift_wages = frappe.get_value("Employee",employee,["sd_shift_rate", "sd_shift_wages"])
			if not shift_rate:
				no_shift_rate.append(employee)
			if not shift_wages:
				no_shift_wages.append(employee)

		if no_shift_rate:
			x = ", ".join(no_shift_rate)
			frappe.throw(f"These employees has Shift rate as Zero\n{x}")
		if no_shift_wages:
			x = ", ".join(no_shift_wages)
			frappe.throw(f"These employees has Shift Wages as Zero\n{x}")
			
		logger.debug(f"{len(employees)} Employees")
		total_attendance_list = []
		for employee in employees:
			employee = employee[0]
			shift_type = frappe.get_value("Employee",employee,"default_shift")
			logger.debug(f"<---------{employee}--------->")
			attendance_list = frappe.db.sql(
				f"""
					SELECT name FROM `tabAttendance` WHERE employee = '{employee}' AND attendance_date >= '{from_date}' AND attendance_date <= '{to_date}' AND docstatus = 1
					ORDER BY attendance_date ASC
				""", as_list= True
			)
			holiday = frappe.get_value("Shift Type", shift_type, "holiday_list")
			holiday_doc = frappe.get_doc("Holiday List", holiday)
			holiday_data = {}
			for day in holiday_doc.holidays:
				d = getdate(day.holiday_date)
				d1 = getdate(from_date)
				d2 = getdate(to_date)
				if d >= d1 and d <= d2:
					holiday_data[str(d)] = day.weekly_off
			attendance_date_list = []
			for attendance in attendance_list:
				attendance_date = frappe.get_value("Attendance", attendance, "attendance_date")
				d = getdate(attendance_date)
				attendance_date_list.append(str(d))
			
			additional_reduce = 0
			for holiday in holiday_data:
				x = str(holiday)
				if x not in attendance_date_list and not holiday_data[x]:
					create_fl_attendance(holiday, employee)	
					additional_reduce += 1				

			extra_shifts = 0
			attendance_data = {}
			dates = []
			main_shifts = 0
			total_days = 0
			for attendance in attendance_list:
				shifts, attendance_date = frappe.get_value("Attendance", attendance,["sd_no_of_shifts","attendance_date"])
				main_shifts += shifts
				d = getdate(attendance_date)
				if holiday_data.get(str(d)):
					total_days += 1
					att_doc = frappe.get_doc("Attendance", attendance)
					att_doc.sd_general_shifts = 0
					att_doc.sd_ot_shifts = 0
					att_doc.save()
					extra_shifts += shifts
				elif str(d) in holiday_data:
					total_days += 1
					if shifts > 1:
						extra_shifts = extra_shifts + shifts - 1
						att_doc = frappe.get_doc("Attendance", attendance)
						att_doc.sd_general_shifts = 1
						att_doc.sd_ot_shifts = 0
						att_doc.save()
					elif shifts < 1:
						x = 1 - shifts
						extra_shifts = extra_shifts - x	
						att_doc = frappe.get_doc("Attendance", attendance)
						att_doc.sd_general_shifts = 1
						att_doc.sd_ot_shifts = 0
						att_doc.save()
				else:
					if shifts > 0:
						total_days += 1
					dates.append(attendance)
					attendance_data[str(d)] = shifts
			
			attendance_list = dates		
			date = from_date
			original_shifts = []
			complete_alter_shifts = []
			alter_shifts = []
			total_shifts = 0
			total_alter_shifts = 0
			while date <= to_date:
				if attendance_data.get(date):
					original_shifts.append(attendance_data[date])
					total_shifts += attendance_data[date]
					if attendance_data[date] > 1:
						alter_shifts.append(0)
						complete_alter_shifts.append(1)
						total_alter_shifts += 1
					else:
						alter_shifts.append(None)
						total_alter_shifts += attendance_data[date]
						complete_alter_shifts.append(attendance_data[date])
				
				elif attendance_data.get(date) == 0:
					original_shifts.append(attendance_data[date])
					alter_shifts.append(None)
					complete_alter_shifts.append(None)
				date = add_days(date, 1)	
		
			total_shifts = total_shifts + extra_shifts
			shift_rate, shift_wages, minimum_wages = frappe.get_value("Employee",employee,["sd_shift_rate", "sd_shift_wages","sd_minimum_wages"])
			old_value = total_shifts * shift_rate
			new_shifts = old_value/ shift_wages
			additional_shifts = new_shifts - total_alter_shifts
			additional_shifts -= additional_reduce
			changed_indexes = []
			max_total_salary = main_shifts * shift_rate
			max_one_shift_salary = max_total_salary / total_days
			index = 0
			length = 0
			for alt in alter_shifts:
				if alt not in [None]:
					length += 1
			if alter_shifts and additional_shifts > 0:
				greater_than_two = 0
				equal_to_two = 0
				less_than_two = 0
				for og in original_shifts:
					if og > flt(2):
						greater_than_two += 1
					elif flt(og) == 2:
						equal_to_two += 1
					elif flt(og) < 2 and flt(og) > 1:
						less_than_two += 1
				x = True
				changed_indexes = []
				while True:
					if alter_shifts[index] not in [None]:
						index, additional_shifts, x, check = update_shift(index, changed_indexes, alter_shifts, additional_shifts, x)
						if check:
							break
					else:
						index, x = update_index(index, alter_shifts, x)
					if len(changed_indexes) >= length:
						break
				
				if additional_shifts:
					total_attendance_list.append({
						"employee": employee,
						"shifts": additional_shifts,
						"required_extra": max_one_shift_salary,
					})

				for idx, attendance in enumerate(attendance_list):
					x = alter_shifts[idx] or 0.0
					if complete_alter_shifts[idx] not in [None]:
						frappe.db.sql(
							f"""
								Update `tabAttendance` set sd_general_shifts = '{complete_alter_shifts[idx]}', sd_ot_shifts = '{x}',
								sd_shift_rate = {shift_rate}, sd_shift_wages = {shift_wages}, sd_minimum_wages = {minimum_wages}
								where name = '{attendance[0]}'
							"""
						)
				logger.debug("IF Part Process Completed")	
			else:
				for idx, attendance in enumerate(attendance_list):
					if complete_alter_shifts[idx] not in [None]:
						ot = complete_alter_shifts[idx] - 1
						x = 0
						if ot > 0:
							x = ot
						frappe.db.sql(
							f"""
								Update `tabAttendance` set sd_general_shifts = '{complete_alter_shifts[idx]}', sd_ot_shifts = '{x}',
								sd_shift_rate = {shift_rate}, sd_shift_wages = {shift_wages}, sd_minimum_wages = {minimum_wages}
								where name = '{attendance[0]}'
							"""
						)
				logger.debug("ELSE Part Process Completed")	
				
		doc.status = "Success"	
		doc.set("essdee_shift_calculation_extra_ot_details", total_attendance_list)	
		doc.calculating = 0
		doc.last_error = None
		doc.error_reason = None
		doc.save()	
	except Exception as e:
		err_doc = frappe.log_error("Essdee Shift Calculation Failed")
		doc = frappe.get_doc("Essdee Shift Calculation", doc_name)
		doc.status = "Failed"							
		doc.calculating = 0
		doc.essdee_shift_calculation_extra_ot_details = []
		doc.last_error = err_doc.name
		doc.error_reason = e
		doc.save()

def update_shift(index, changed_indexes, alter_shifts, additional_shifts, x):
	if index not in changed_indexes:
		changed_indexes.append(index)
		alter_shifts[index] += 0.25
		additional_shifts -= 0.25
		if additional_shifts < 0:
			return index, additional_shifts, x, True
		index = index + 2
	else:
		index = index + 1
	if index >= len(alter_shifts):
		if x:
			index = 1
			x = False
		else:
			index = 0
			x = True	
	return index, additional_shifts, x, False	

def update_index(index, alter_shifts, x):
	index = index + 1		
	if index >= len(alter_shifts):
		if x:
			index = 1
			x = False
		else:
			index = 0
			x = True
	return index, x

def create_fl_attendance(holiday, employee):
	att_doc = frappe.new_doc("Attendance")
	att_doc.employee = employee
	att_doc.status = "Present"
	att_doc.attendance_date = holiday
	cmpy, dept, shift, shift_rate, shift_wages, min_wages = frappe.get_value("Employee", employee, ['company','department','default_shift', 'sd_shift_rate', 'sd_shift_wages', 'sd_minimum_wages'])
	att_doc.shift = shift
	att_doc.sd_no_of_shifts = 0
	att_doc.sd_general_shifts = 1
	att_doc.sd_ot_shifts = 0
	att_doc.sd_shift_rate = shift_rate
	att_doc.sd_shift_wages =  shift_wages
	att_doc.sd_minimum_wages = min_wages
	att_doc.company = cmpy
	att_doc.sd_festival_leave = 1
	att_doc.department = dept
	att_doc.save()
	att_doc.submit()

# while additional_shifts > -0.25:
# 	check = False
# 	index = 0
# 	x = True
# 	if greater_than_two > 0:
# 		changed_indexes = []
# 		while True:
# 			if alter_shifts[index] not in [None] and original_shifts[index] > flt(2):
# 				index, additional_shifts, x, check = update_shift(index, changed_indexes, alter_shifts, additional_shifts, x)
# 				if check:
# 					break
# 			else:
# 				index, x = update_index(index, alter_shifts, x)
# 			if len(changed_indexes) >= greater_than_two:
# 				break
# 	if check:
# 		break
# 	x = True
# 	if equal_to_two > 0:
# 		index = 0
# 		changed_indexes = []
# 		while True:
# 			if alter_shifts[index] not in [None] and original_shifts[index] == flt(2):
# 				index, additional_shifts, x, check = update_shift(index, changed_indexes, alter_shifts, additional_shifts, x)
# 				if check:
# 					break
# 			else:
# 				index, x = update_index(index, alter_shifts, x)
# 			if len(changed_indexes) >= equal_to_two:
# 				break
	
# 	if check:
# 		break
# 	x = True
# 	if less_than_two > 0:
# 		index = 0
# 		changed_indexes = []
# 		while True:
# 			if alter_shifts[index] not in [None] and original_shifts[index] < flt(2) and original_shifts[index] > flt(1):
# 				index, additional_shifts, x, check = update_shift(index, changed_indexes, alter_shifts, additional_shifts, x)
# 				if check:
# 					break	
# 			else:
# 				index, x = update_index(index, alter_shifts, x)
# 			if len(changed_indexes) >= less_than_two:
# 				break
# 	if check:
# 		break