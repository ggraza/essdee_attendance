# Copyright (c) 2025, Aerele and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days, getdate, flt

class EssdeeShiftCalculation(Document):
	pass

@frappe.whitelist()
def calculate_wages(doc_name):
	doc = frappe.get_doc("Essdee Shift Calculation", doc_name)
	from_date = str(getdate(doc.start_date))
	to_date = str(getdate(doc.end_date))
	shift_type = doc.shift_type
	employee_list = frappe.get_list("Employee", filters={"default_shift":shift_type}, pluck="name")
	total_attendance_list = []
	for employee in employee_list:
		attendance_list = frappe.db.sql(
			f"""
				SELECT name FROM `tabAttendance` WHERE employee = '{employee}' AND attendance_date >= '{from_date}' AND attendance_date <= '{to_date}'
				ORDER BY attendance_date ASC
			""", as_list= True
		)
		attendance_data = {}
		for attendance in attendance_list:
			shifts, attendance_date = frappe.get_value("Attendance", attendance,["sd_no_of_shifts","attendance_date"])
			d = getdate(attendance_date)
			attendance_data[str(d)] = shifts
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
				if attendance_data[date] == 2:
					alter_shifts.append(0)
					complete_alter_shifts.append(1)
					total_alter_shifts += 1
				elif attendance_data[date] > 1:
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
		shift_rate, shift_wages = frappe.get_value("Employee",employee,["sd_shift_rate", "sd_shift_wages"])
		old_value = total_shifts * shift_rate
		new_shifts = old_value/ shift_wages
		additional_shifts = new_shifts - total_alter_shifts
		changed_indexs = []
		i = 0
		length = 0
		for alt in alter_shifts:
			if alt not in [None]:
				length += 1
		if alter_shifts:
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
			while True:
				if alter_shifts[i] not in [None]:
					if i not in changed_indexs:
						changed_indexs.append(i)
						alter_shifts[i] += 0.25
						additional_shifts -= 0.25
						if additional_shifts < 0:
							break
						i = i + 2
					else:
						i = i + 1
					if i >= len(alter_shifts):
						i = int(i / len(alter_shifts)) 	
				else:
					i = i + 1		
					if i >= len(alter_shifts):
						i = int(i / len(alter_shifts))
				if len(changed_indexs) == length:
					break
			while additional_shifts > -0.25:
				check = False
				i = 0
				if greater_than_two > 0:
					changed_indexs = []
					while True:
						if alter_shifts[i] not in [None] and original_shifts[i] > flt(2):
							if i not in changed_indexs:
								changed_indexs.append(i)
								alter_shifts[i] += 0.25
								additional_shifts -= 0.25
								if additional_shifts < 0:
									check = True
									break
								i = i + 2
							else:
								i = i + 1
							if i >= len(alter_shifts):
								i = int(i / len(alter_shifts)) 	
						else:
							i = i + 1		
							if i >= len(alter_shifts):
								i = int(i / len(alter_shifts))
						if len(changed_indexs) >= greater_than_two:
							break
				if check:
					break

				if equal_to_two > 0:
					i = 0
					changed_indexs = []
					while True:
						if alter_shifts[i] not in [None] and original_shifts[i] == flt(2):
							if i not in changed_indexs:
								changed_indexs.append(i)
								alter_shifts[i] += 0.25
								additional_shifts -= 0.25
								if additional_shifts < 0:
									check = True
									break
								i = i + 2
							else:
								i = i + 1
							if i >= len(alter_shifts):
								i = int(i / len(alter_shifts)) 	
						else:
							i = i + 1		
							if i >= len(alter_shifts):
								i = int(i / len(alter_shifts))
						if len(changed_indexs) >= equal_to_two:
							break
				if check:
					break

				if less_than_two > 0:
					i = 0
					changed_indexs = []
					while True:
						if alter_shifts[i] not in [None] and original_shifts[i] < flt(2) and original_shifts[i] > flt(1):
							if i not in changed_indexs:
								changed_indexs.append(i)
								alter_shifts[i] += 0.25
								additional_shifts -= 0.25
								if additional_shifts < 0:
									check = True
									break
								i = i + 2
							else:
								i = i + 1
							if i >= len(alter_shifts):
								i = int(i / len(alter_shifts)) 	
						else:
							i = i + 1		
							if i >= len(alter_shifts):
								i = int(i / len(alter_shifts))
						if len(changed_indexs) >= less_than_two:
							break
				if check:
					break
			for idx, attendance in enumerate(attendance_list):
				x = alter_shifts[idx] or 0.0
				if x > 0.25:
					emp , no_of_shifts = frappe.get_value("Attendance", attendance[0],["employee","sd_no_of_shifts"])
					total_attendance_list.append({
						"attendance": attendance[0],
						"employee": emp,
						"no_of_shifts": no_of_shifts,
						"general_shifts": complete_alter_shifts[idx],
						"ot_shifts": x,
						"total_shifts": complete_alter_shifts[idx] + x
					})
				if complete_alter_shifts[idx] not in [None]:
					frappe.db.sql(
						f"""
							Update `tabAttendance` set sd_general_shifts = '{complete_alter_shifts[idx]}', sd_ot_shifts = '{x}'
							where name = '{attendance[0]}'
						"""
					)
	doc.set("essdee_shift_calculation_extra_ot_details", total_attendance_list)	
	doc.save()	