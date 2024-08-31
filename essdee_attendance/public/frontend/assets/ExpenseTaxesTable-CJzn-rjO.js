var H=Object.defineProperty;var q=Object.getOwnPropertySymbols;var K=Object.prototype.hasOwnProperty,L=Object.prototype.propertyIsEnumerable;var R=(t,i,a)=>i in t?H(t,i,{enumerable:!0,configurable:!0,writable:!0,value:a}):t[i]=a,N=(t,i)=>{for(var a in i||(i={}))K.call(i,a)&&R(t,a,i[a]);if(q)for(var a of q(i))L.call(i,a)&&R(t,a,i[a]);return t};var D=(t,i,a)=>new Promise((y,l)=>{var r=c=>{try{f(a.next(c))}catch(v){l(v)}},_=c=>{try{f(a.throw(c))}catch(v){l(v)}},f=c=>c.done?y(c.value):Promise.resolve(c.value).then(r,_);f((a=a.apply(t,i)).next())});import{a as O,O as z,c as I,w as j,f as G,j as d,k as p,x as s,K as m,q as x,y as w,a5 as g,F as E,H as S,l as h,t as $,n as b,v as A}from"./frappe-ui-DZDZpt4w.js";import J from"./FormField-7rSNy-En.js";import{_ as P}from"./index-BxNz1Obz.js";import Q from"./CustomIonModal-5G33LXxg.js";import{f as k}from"./formatters-Ch330Bw1.js";import"./Link-WtJjedfJ.js";const W={class:"flex flex-row justify-between items-center pt-4"},X=s("h2",{class:"text-base font-semibold text-gray-800"},"Taxes & Charges",-1),Y={class:"flex flex-row gap-3 items-center"},Z={class:"text-base font-semibold text-gray-800"},ee={key:0,class:"flex flex-col bg-white mt-5 rounded border overflow-auto"},te=["onClick"],ae={class:"flex flex-col w-full justify-center gap-2.5"},se={class:"flex flex-row items-center justify-between"},le={class:"flex flex-row items-start gap-3 grow"},ne={class:"flex flex-col items-start gap-1.5"},oe={class:"text-base font-normal text-gray-800"},ie={class:"text-xs font-normal text-gray-500"},re=s("span",{class:"whitespace-pre"}," · ",-1),de={class:"whitespace-nowrap"},ce={class:"flex flex-row justify-end items-center gap-2"},ue={class:"text-gray-700 font-normal rounded text-base"},xe={class:"bg-white w-full flex flex-col items-center justify-center pb-5"},me={class:"w-full pt-8 pb-5 border-b text-center"},fe={class:"text-gray-900 font-bold text-xl"},pe={class:"w-full flex flex-col items-center justify-center gap-5 p-4"},ye={class:"flex flex-col w-full space-y-4"},_e={key:0,class:"flex w-full flex-row items-center justify-between gap-3"},Fe={__name:"ExpenseTaxesTable",props:{expenseClaim:{type:Object,required:!0},currency:{type:String,required:!0},isReadOnly:{type:Boolean,default:!1}},emits:["add-expense-tax","update-expense-tax","delete-expense-tax"],setup(t,{emit:i}){const a=t,y=i,l=O({}),r=O(null),_=O(!1),f=(o,n)=>D(this,null,function*(){o&&(l.value=N({},o),r.value=n),_.value=!0}),c=()=>{y("delete-expense-tax",r.value),C()},v=()=>{r.value===null?y("add-expense-tax",l.value):y("update-expense-tax",l.value,r.value),C()};function C(){_.value=!1,l.value={},r.value=null}const T=z({url:"essdee_attendance.api.get_doctype_fields",params:{doctype:"Expense Taxes and Charges"},transform(o){const n=["description_sb"];return o.map(u=>(u.fieldname==="account_head"&&(u.linkFilters={company:a.expenseClaim.company,account_type:["in",["Tax","Chargeable","Income Account","Expenses Included In Valuation"]]}),u)).filter(u=>!n.includes(u.fieldname))}});T.reload();const U=I(()=>a.isReadOnly?"Expense Tax":r.value===null?"New Expense Tax":"Edit Expense Tax"),M=I(()=>{var o;return(o=T.data)==null?void 0:o.some(n=>{if(n.reqd&&!l.value[n.fieldname])return!0})});j(()=>l.value.account_head,o=>{l.value.description=o==null?void 0:o.split(" - ").slice(0,-1).join(" - ")}),j(()=>l.value.rate,(o,n)=>{r.value&&o&&!n||(l.value.tax_amount=parseFloat(a.expenseClaim.total_sanctioned_amount)*(parseFloat(o)/100),B())}),j(()=>l.value.tax_amount,o=>{B()});function B(){l.value.total=parseFloat(a.expenseClaim.total_sanctioned_amount)+parseFloat(l.value.tax_amount)}return(o,n)=>{var V;const u=G("Button");return t.expenseClaim.expenses?(d(),p(E,{key:0},[s("div",W,[X,s("div",Y,[s("span",Z,m(x(k)(t.expenseClaim.total_taxes_and_charges,t.currency)),1),t.isReadOnly?g("",!0):(d(),w(u,{key:0,id:"add-taxes-modal",class:"text-sm",icon:"plus",variant:"subtle",onClick:n[0]||(n[0]=e=>f())}))])]),(V=t.expenseClaim.taxes)!=null&&V.length?(d(),p("div",ee,[(d(!0),p(E,null,S(t.expenseClaim.taxes,(e,F)=>(d(),p("div",{class:"flex flex-row p-3.5 items-center justify-between border-b cursor-pointer",key:e.name,onClick:ve=>f(e,F)},[s("div",ae,[s("div",se,[s("div",le,[s("div",ne,[s("div",oe,m(e.account_head),1),s("div",ie,[s("span",null," Rate: "+m(x(k)(e.rate,t.currency)),1),re,s("span",de," Amount: "+m(x(k)(e.tax_amount,t.currency)),1)])])]),s("div",ce,[s("span",ue,m(x(k)(e.total,t.currency)),1),h(x($),{name:"chevron-right",class:"h-5 w-5 text-gray-500"})])])])],8,te))),128))])):(d(),w(P,{key:1,message:"No taxes added",isTableField:!0})),h(Q,{isOpen:_.value,onDidDismiss:n[3]||(n[3]=e=>C())},{actionSheet:b(()=>[s("div",xe,[s("div",me,[s("span",fe,m(U.value),1)]),s("div",pe,[s("div",ye,[(d(!0),p(E,null,S(x(T).data,e=>(d(),w(J,{key:e.fieldname,class:"w-full",label:e.label,fieldtype:e.fieldtype,fieldname:e.fieldname,options:e.options,linkFilters:e.linkFilters,hidden:e.hidden,reqd:e.reqd,readOnly:e.read_only||t.isReadOnly,default:e.default,modelValue:l.value[e.fieldname],"onUpdate:modelValue":F=>l.value[e.fieldname]=F},null,8,["label","fieldtype","fieldname","options","linkFilters","hidden","reqd","readOnly","default","modelValue","onUpdate:modelValue"]))),128))]),t.isReadOnly?g("",!0):(d(),p("div",_e,[r.value!==null?(d(),w(u,{key:0,class:"border-red-600 text-red-600 py-5 text-sm",variant:"outline",theme:"red",onClick:n[1]||(n[1]=e=>c())},{prefix:b(()=>[h(x($),{name:"trash",class:"w-4"})]),default:b(()=>[A(" Delete ")]),_:1})):g("",!0),h(u,{variant:"solid",class:"w-full py-5 text-sm disabled:bg-gray-700 disabled:text-white",onClick:n[2]||(n[2]=e=>v()),disabled:M.value},{prefix:b(()=>[h(x($),{name:r.value===null?"plus":"check",class:"w-4"},null,8,["name"])]),default:b(()=>[A(" "+m(r.value===null?"Add Tax":"Update Tax"),1)]),_:1},8,["disabled"])]))])])]),_:1},8,["isOpen"])],64)):g("",!0)}}};export{Fe as default};
//# sourceMappingURL=ExpenseTaxesTable-CJzn-rjO.js.map
