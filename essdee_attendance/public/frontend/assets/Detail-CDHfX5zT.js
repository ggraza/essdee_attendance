var h=(_,f,r)=>new Promise((c,n)=>{var i=o=>{try{u(r.next(o))}catch(a){n(a)}},y=o=>{try{u(r.throw(o))}catch(a){n(a)}},u=o=>o.done?c(o.value):Promise.resolve(o.value).then(i,y);u((r=r.apply(_,f)).next())});import{b as k,c as S}from"./index-BxNz1Obz.js";import{a as w,O as C,w as R,f as D,j as b,y as g,n as d,l as m,q as p,ag as x,v as B,a5 as O}from"./frappe-ui-DZDZpt4w.js";import P from"./FormView-CS-B2Mga.js";import F from"./SalaryDetailTable-3P6Ki1VK.js";import{g as T}from"./currencies-SJR35BQj.js";import"./FormField-7rSNy-En.js";import"./Link-WtJjedfJ.js";import"./FileUploaderView-C4tMF-0v.js";import"./WorkflowActionSheet-tSPgpAX-.js";import"./workflow-CgWnsJgA.js";import"./formatters-Ch330Bw1.js";const A={__name:"Detail",props:{id:{type:String,required:!0}},setup(_){const f=_,r=w(""),c=w(!1),n=w({}),i=C({url:"essdee_attendance.api.get_doctype_fields",params:{doctype:"Salary Slip"},transform(a){return u(a)}});i.reload();const y=[{name:"Details",lastField:"payment_days"},{name:"Earnings & Deductions",lastField:"base_total_deduction"},{name:"Net Pay Info",lastField:"base_total_in_words"},{name:"Income Tax Breakup",lastField:"total_income_tax"},{name:"Bank Details",lastField:"bank_account_no"}];R(()=>n.value.company,a=>h(this,null,function*(){var t;if(!a)return;const l=yield T(a);(t=i.data)==null||t.map(e=>{var s;(s=e.label)!=null&&s.includes("Company Currency")&&(n.value.currency===l?e.hidden=!0:e.label=e.label.replace("Company Currency",l))})}),{immediate:!0});function u(a){var e,s;if((s=(e=n.value)==null?void 0:e.timesheets)==null?void 0:s.length)return a;const t=["timesheets_section","timesheets","total_working_hours","hour_rate","base_hour_rate","help_section","earning_deduction_sb"];return a.filter(v=>!t.includes(v.fieldname))}function o(){const a=n.value.name;c.value=!0;let l={"X-Frappe-Site-Name":window.location.hostname};window.csrf_token&&(l["X-Frappe-CSRF-Token"]=window.csrf_token),fetch("/api/method/essdee_attendance.api.download_salary_slip",{method:"POST",headers:l,body:new URLSearchParams({name:a}),responseType:"blob"}).then(t=>{if(t.ok)return t.blob();r.value="Failed to download PDF"}).then(t=>{if(!t)return;const e=window.URL.createObjectURL(t),s=document.createElement("a");s.href=e,s.download=`${a}.pdf`,s.click(),setTimeout(()=>{window.URL.revokeObjectURL(e)},3e3)}).catch(t=>{r.value=`Failed to download PDF: ${t.message}`}).finally(()=>{c.value=!1})}return(a,l)=>{const t=D("Button");return b(),g(p(S),null,{default:d(()=>[m(p(k),{fullscreen:!0},{default:d(()=>[p(i).data?(b(),g(P,{key:0,doctype:"Salary Slip",modelValue:n.value,"onUpdate:modelValue":l[0]||(l[0]=e=>n.value=e),fields:p(i).data,id:f.id,tabbedView:!0,tabs:y,showFormButton:!1},{earnings:d(({isFormReadOnly:e})=>[m(F,{type:"Earnings",salarySlip:n.value,isReadOnly:e},null,8,["salarySlip","isReadOnly"])]),deductions:d(({isFormReadOnly:e})=>[m(F,{type:"Deductions",salarySlip:n.value,isReadOnly:e},null,8,["salarySlip","isReadOnly"])]),formButton:d(()=>[m(p(x),{message:r.value,class:"mt-2"},null,8,["message"]),m(t,{class:"w-full rounded py-5 text-base disabled:bg-gray-700 disabled:text-white",onClick:o,variant:"solid",loading:c.value},{default:d(()=>[B(" Download PDF ")]),_:1},8,["loading"])]),_:1},8,["modelValue","fields","id"])):O("",!0)]),_:1})]),_:1})}}};export{A as default};
//# sourceMappingURL=Detail-CDHfX5zT.js.map
