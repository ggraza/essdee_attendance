import frappe
from frappe.utils import getdate

def validate(doc, action):
    if action != "validate": return
    if doc.is_new():
        doc.sd_bank_account_status = ''
        return
    old_doc = frappe.get_doc("Employee", doc.name)
    if (old_doc.bank_ac_no != doc.bank_ac_no) or (old_doc.ifsc_code != doc.ifsc_code):
        doc.sd_bank_account_status = 'Pending Approval'

    last_salary = 0
    for row in doc.sd_increment_records:
        if row.idx == 1:
            if not row.current_wages:
                frappe.throw("Enter the Current Wages")
            last_salary = row.current_wages
        else:
            if not row.effective_from or not row.previous_wages or not row.increment or not row.current_wages:
                frappe.throw("Enter value for all fields to save the document")
            if row.previous_wages != last_salary:
                frappe.throw("Previous Salary Mismatch")
            if (row.previous_wages + row.increment) != row.current_wages:
                frappe.throw("Current Wages Total Mismatch")
            last_salary = row.current_wages
    doc.sd_shift_wages = last_salary    

    if doc.sd_shift_wages != None:
        if doc.sd_shift_wages < doc.sd_minimum_wages:
           frappe.throw("Shift Wages is less than Minimum Wages") 

@frappe.whitelist()
def get_date(from_date):
	from_date = getdate(from_date)
	date = from_date.day
	month = from_date.month
	year = from_date.year 
	return str(date)+"/"+str(month)+"/"+str(year)