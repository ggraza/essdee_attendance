import{O as s}from"./frappe-ui-DZDZpt4w.js";import{e as t,G as r}from"./index-BxNz1Obz.js";const o=e=>e.map(a=>(a.leave_dates=n(a),a.doctype="Essdee Permission Application",a)),n=e=>`${r(e.start_date).format("D MMM")} ${e.start_time}- ${r(e.end_date).format("D MMM")} ${e.end_time}`,p=s({url:"essdee_attendance.api.get_permission_applications",params:{employee:t.data.name,limit:10},auto:!0,cache:"hrms:my_permissions",transform(e){return o(e)}}),c=s({url:"essdee_attendance.api.get_permission_applications",params:{employee:t.data.name,approver_id:t.data.user_id,for_approval:!0,limit:10},auto:!0,cache:"hrms:team_permissions",transform(e){return console.log(e),o(e)}}),_=s({url:"essdee_attendance.api.get_personal_permission_balance",params:{employee:t.data.name},auto:!0,cache:"hrms:permission_balance",transform:e=>e});export{n as g,p as m,_ as p,c as t};
//# sourceMappingURL=permissions-DOYaNnKb.js.map
