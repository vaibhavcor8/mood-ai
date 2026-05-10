import { useState, useEffect, useRef, useCallback } from "react";
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid } from "recharts";

/* ═══════════════════════════════════════════════════════
   CONSTANTS
═══════════════════════════════════════════════════════ */
const APP_NAME = "RupAI Alarm";

const UPI_APPS = [
  { name: "PhonePe", color: "#6739B7", icon: "📱" },
  { name: "Paytm",   color: "#00BAF2", icon: "💙" },
  { name: "GPay",    color: "#34A853", icon: "🟢" },
  { name: "BHIM",    color: "#FF6B00", icon: "🏛️" },
  { name: "Amazon",  color: "#FF9900", icon: "📦" },
  { name: "Cash",    color: "#22c55e", icon: "💵" },
  { name: "Other",   color: "#888",    icon: "💸" },
];

const CATS = [
  { name: "Food",         icon: "🍔", color: "#f97316" },
  { name: "Shopping",     icon: "🛍️", color: "#a855f7" },
  { name: "Petrol/Travel",icon: "⛽", color: "#3b82f6" },
  { name: "Bills",        icon: "🧾", color: "#ef4444" },
  { name: "EMI/Loan",     icon: "🏦", color: "#f43f5e" },
  { name: "Ghar/Rent",    icon: "🏠", color: "#8b5cf6" },
  { name: "Health",       icon: "💊", color: "#06b6d4" },
  { name: "Entertainment",icon: "🎬", color: "#ec4899" },
  { name: "Friends",      icon: "👥", color: "#22c55e" },
  { name: "Other",        icon: "💸", color: "#888"    },
];

const DEFAULT_FIXED = [
  { id:"rent",       label:"Rent / Kiraya",         icon:"🏠", amount:"", active:true },
  { id:"emi_home",   label:"Home Loan EMI",          icon:"🏦", amount:"", active:true },
  { id:"emi_car",    label:"Car Loan EMI",           icon:"🚘", amount:"", active:true },
  { id:"emi_personal",label:"Personal Loan EMI",    icon:"💳", amount:"", active:true },
  { id:"lic",        label:"LIC / Insurance",        icon:"🛡️", amount:"", active:true },
  { id:"rd",         label:"RD (Recurring Deposit)", icon:"🏧", amount:"", active:true },
  { id:"electricity",label:"Bijli Bill",             icon:"⚡", amount:"", active:true },
  { id:"mobile",     label:"Mobile Recharge",        icon:"📶", amount:"", active:true },
  { id:"internet",   label:"Internet / WiFi",        icon:"🌐", amount:"", active:true },
  { id:"milk",       label:"Doodh (Milk)",           icon:"🥛", amount:"", active:true },
  { id:"sabji",      label:"Sabji / Rashan",         icon:"🥦", amount:"", active:true },
  { id:"school",     label:"School Fees",            icon:"🎒", amount:"", active:true },
  { id:"petrol",     label:"Petrol / CNG",           icon:"⛽", amount:"", active:true },
  { id:"ghar",       label:"Ghar Bhejna",            icon:"🏡", amount:"", active:true },
  { id:"gym",        label:"Gym / Fitness",          icon:"💪", amount:"", active:true },
  { id:"ott",        label:"OTT (Netflix/Prime)",    icon:"📺", amount:"", active:true },
  { id:"medicine",   label:"Dawai / Medicine",       icon:"💊", amount:"", active:true },
  { id:"paper",      label:"Newspaper",              icon:"📰", amount:"", active:true },
];

/* ═══════════════════════════════════════════════════════
   HELPERS
═══════════════════════════════════════════════════════ */
const fmt   = n => "₹" + Number(n||0).toLocaleString("en-IN");
const today = ()  => new Date().toISOString().split("T")[0];
const nowT  = ()  => new Date().toLocaleTimeString("en-IN",{hour:"2-digit",minute:"2-digit"});
const monthOf = d => d.slice(0,7);
const curMonth = () => new Date().toISOString().slice(0,7);
const upiApp = n => UPI_APPS.find(a=>a.name===n)||UPI_APPS[6];
const cat    = n => CATS.find(c=>c.name===n)||CATS[9];
const pct    = (a,b) => b>0 ? Math.min(100,Math.round((a/b)*100)) : 0;

const STYLES = {
  card: { background:"#161625", border:"1px solid #252545", borderRadius:18, padding:"16px" },
  input: { width:"100%", background:"#0d0d1a", border:"1px solid #2a2a4a", borderRadius:10,
           padding:"11px 14px", color:"#fff", fontSize:14, boxSizing:"border-box", outline:"none" },
  btn: (col="#6C3FD4") => ({ background:col, border:"none", borderRadius:12, padding:"13px 20px",
        color:"#fff", fontSize:14, fontWeight:700, cursor:"pointer", width:"100%" }),
  pill: (active,col) => ({ background: active ? col+"33" : "#1a1a2e", border:`1.5px solid ${active?col:"#2a2a4a"}`,
        borderRadius:20, padding:"6px 13px", color: active ? col : "#666", fontSize:12,
        cursor:"pointer", fontWeight: active?700:400, whiteSpace:"nowrap" }),
};

/* ═══════════════════════════════════════════════════════
   SETUP WIZARD
═══════════════════════════════════════════════════════ */
function SetupWizard({ onDone }) {
  const [step, setStep] = useState(0);
  const [name, setName]     = useState("");
  const [salary, setSalary] = useState("");
  const [limit, setLimit]   = useState("");
  const [fixed, setFixed]   = useState(DEFAULT_FIXED.map(f=>({...f})));

  const steps = ["Naam", "Income", "Limit", "Fixed Kharche"];
  const activeFixed = fixed.filter(f=>f.active && f.amount);

  function finish() {
    onDone({ name: name.trim(), salary, spendLimit: limit, fixedExpenses: fixed });
  }

  return (
    <div style={{ minHeight:"100vh", background:"radial-gradient(ellipse at 20% 20%, #1a0d3a 0%, #0d0d18 60%)",
                  display:"flex", alignItems:"center", justifyContent:"center", padding:20 }}>
      <div style={{ width:"100%", maxWidth:420 }}>
        {/* Logo */}
        <div style={{ textAlign:"center", marginBottom:28 }}>
          <div style={{ fontSize:52, marginBottom:8 }}>💰</div>
          <h1 style={{ margin:0, fontSize:26, fontWeight:900,
                       background:"linear-gradient(90deg,#a78bfa,#38bdf8)", WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent" }}>
            {APP_NAME}
          </h1>
          <p style={{ margin:"4px 0 0", color:"#555", fontSize:13 }}>AI-powered paisa manager</p>
        </div>

        {/* Step indicator */}
        <div style={{ display:"flex", gap:6, marginBottom:24, justifyContent:"center" }}>
          {steps.map((s,i)=>(
            <div key={i} style={{ height:4, flex:1, borderRadius:4,
                                   background: i<=step ? "#a78bfa" : "#252535" }} />
          ))}
        </div>

        <div style={{ background:"#12121f", border:"1px solid #252540", borderRadius:22, padding:24 }}>

          {step===0 && (
            <>
              <p style={{ color:"#a78bfa", fontWeight:700, marginBottom:4 }}>👋 Apna naam batao</p>
              <p style={{ color:"#555", fontSize:13, marginBottom:16 }}>Main tumhara financial dost banunga!</p>
              <input autoFocus placeholder="Jaise: Rahul, Priya..." value={name}
                onChange={e=>setName(e.target.value)}
                onKeyDown={e=>e.key==="Enter"&&name.trim()&&setStep(1)}
                style={{ ...STYLES.input, fontSize:18, fontWeight:700, marginBottom:16 }} />
              <button onClick={()=>name.trim()&&setStep(1)} style={STYLES.btn()}>Aage chalo →</button>
            </>
          )}

          {step===1 && (
            <>
              <p style={{ color:"#a78bfa", fontWeight:700, marginBottom:4 }}>💼 Monthly Income</p>
              <p style={{ color:"#555", fontSize:13, marginBottom:16 }}>Salary / business income kitni hai?</p>
              <div style={{ position:"relative", marginBottom:16 }}>
                <span style={{ position:"absolute", left:14, top:"50%", transform:"translateY(-50%)", color:"#a78bfa", fontWeight:700, fontSize:18 }}>₹</span>
                <input type="number" placeholder="Jaise: 35000" value={salary}
                  onChange={e=>setSalary(e.target.value)} style={{ ...STYLES.input, paddingLeft:32, fontSize:18, fontWeight:700 }} />
              </div>
              <div style={{ display:"flex", gap:10 }}>
                <button onClick={()=>setStep(0)} style={{ ...STYLES.btn("#252535"), flex:0.4 }}>← Back</button>
                <button onClick={()=>setStep(2)} style={{ ...STYLES.btn(), flex:0.6 }}>Aage →</button>
              </div>
            </>
          )}

          {step===2 && (
            <>
              <p style={{ color:"#a78bfa", fontWeight:700, marginBottom:4 }}>🎯 Spending Limit</p>
              <p style={{ color:"#555", fontSize:13, marginBottom:8 }}>Monthly kitna kharcha karna chahte ho? (fixed kharche alag hain)</p>
              {salary && <p style={{ color:"#22c55e", fontSize:12, marginBottom:12 }}>💡 Suggestion: {fmt(Number(salary)*0.3)} (salary ka 30%)</p>}
              <div style={{ position:"relative", marginBottom:16 }}>
                <span style={{ position:"absolute", left:14, top:"50%", transform:"translateY(-50%)", color:"#f97316", fontWeight:700, fontSize:18 }}>₹</span>
                <input type="number" placeholder="Jaise: 10000" value={limit}
                  onChange={e=>setLimit(e.target.value)} style={{ ...STYLES.input, paddingLeft:32, fontSize:18, fontWeight:700 }} />
              </div>
              <div style={{ display:"flex", gap:10 }}>
                <button onClick={()=>setStep(1)} style={{ ...STYLES.btn("#252535"), flex:0.4 }}>← Back</button>
                <button onClick={()=>setStep(3)} style={{ ...STYLES.btn(), flex:0.6 }}>Aage →</button>
              </div>
            </>
          )}

          {step===3 && (
            <>
              <p style={{ color:"#a78bfa", fontWeight:700, marginBottom:4 }}>📋 Fixed Monthly Kharche</p>
              <p style={{ color:"#555", fontSize:13, marginBottom:12 }}>Jo jo monthly fix hai wo daalo (optional — jo na ho khali chhod do)</p>
              <div style={{ maxHeight:300, overflowY:"auto", paddingRight:4 }}>
                {fixed.map((f,i)=>(
                  <div key={f.id} style={{ display:"flex", alignItems:"center", gap:8, marginBottom:8 }}>
                    <button onClick={()=>setFixed(prev=>prev.map((x,j)=>j===i?{...x,active:!x.active}:x))}
                      style={{ background: f.active?"#6C3FD4":"#252535", border:"none", borderRadius:6, width:28, height:28,
                               color:"#fff", cursor:"pointer", fontSize:12, flexShrink:0 }}>
                      {f.active?"✓":"×"}
                    </button>
                    <span style={{ fontSize:16, flexShrink:0 }}>{f.icon}</span>
                    <span style={{ flex:1, fontSize:12, color: f.active?"#ccc":"#444" }}>{f.label}</span>
                    {f.active && (
                      <div style={{ position:"relative", width:90 }}>
                        <span style={{ position:"absolute", left:8, top:"50%", transform:"translateY(-50%)", color:"#a78bfa", fontSize:12 }}>₹</span>
                        <input type="number" placeholder="0" value={f.amount}
                          onChange={e=>setFixed(prev=>prev.map((x,j)=>j===i?{...x,amount:e.target.value}:x))}
                          style={{ ...STYLES.input, padding:"6px 8px 6px 22px", fontSize:13, width:"100%", boxSizing:"border-box" }} />
                      </div>
                    )}
                  </div>
                ))}
              </div>
              {activeFixed.length > 0 && (
                <div style={{ background:"#0d0d1a", borderRadius:10, padding:"10px 14px", margin:"12px 0 0", textAlign:"center" }}>
                  <span style={{ color:"#888", fontSize:12 }}>Total fixed: </span>
                  <span style={{ color:"#f87171", fontWeight:700 }}>{fmt(activeFixed.reduce((s,f)=>s+Number(f.amount),0))}</span>
                </div>
              )}
              <div style={{ display:"flex", gap:10, marginTop:14 }}>
                <button onClick={()=>setStep(2)} style={{ ...STYLES.btn("#252535"), flex:0.4 }}>← Back</button>
                <button onClick={finish} style={{ ...STYLES.btn("#22c55e"), flex:0.6 }}>🚀 Shuru!</button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════
   MAIN APP
═══════════════════════════════════════════════════════ */
export default function RupAIAlarm() {
  const [profile, setProfile]         = useState(null);
  const [screen, setScreen]           = useState("home");
  const [payments, setPayments]       = useState([]);
  const [tasks, setTasks]             = useState([]);
  const [notifs, setNotifs]           = useState([]);
  const [showNotifs, setShowNotifs]   = useState(false);
  const [aiChat, setAiChat]           = useState([]);
  const [aiInput, setAiInput]         = useState("");
  const [aiLoading, setAiLoading]     = useState(false);
  const [form, setForm]               = useState({ app:"PhonePe", amount:"", note:"", category:"Food", date:today() });
  const [taskForm, setTaskForm]       = useState({ title:"", date:today(), time:"09:00", type:"task", note:"" });
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [addedFlash, setAddedFlash]   = useState(null);
  const [showBudgetEdit, setShowBudgetEdit] = useState(false);
  const chatRef = useRef(null);

  /* ── Derived ── */
  const cm = curMonth();
  const monthPay  = payments.filter(p=>monthOf(p.date)===cm);
  const monthSpent= monthPay.reduce((s,p)=>s+p.amount,0);
  const todayPay  = payments.filter(p=>p.date===today());
  const todaySpent= todayPay.reduce((s,p)=>s+p.amount,0);

  const fixedTotal= profile ? profile.fixedExpenses.filter(f=>f.active&&f.amount).reduce((s,f)=>s+Number(f.amount),0) : 0;
  const salaryNum = profile ? Number(profile.salary)||0 : 0;
  const limitNum  = profile ? Number(profile.spendLimit)||0 : 0;
  const available = salaryNum - fixedTotal - monthSpent;
  const spendPct  = pct(monthSpent, limitNum);

  /* ── Notifications ── */
  const pushNotif = useCallback((msg, type="info") => {
    setNotifs(prev=>[{ id:Date.now()+Math.random(), msg, type, time:nowT() }, ...prev].slice(0,40));
  },[]);

  /* Scheduled nudges every 2 mins (simulates 5-6/day) */
  useEffect(()=>{
    if(!profile) return;
    const nudge = ()=>{
      const opts = [
        spendPct>90  ? { m:`🚨 ${profile.name} ji! Limit ka ${spendPct}% kharcha ho gaya! Ruko thoda!`, t:"danger" } : null,
        spendPct>70  ? { m:`⚠️ ${profile.name} ji, ${spendPct}% limit use ho gayi. Sambhalo!`, t:"warn" } : null,
        available<3000&&salaryNum>0 ? { m:`💸 Sirf ${fmt(available)} bacha hai! Bahut sochke kharcho.`, t:"warn" } : null,
        { m:`📊 Aaj ka kharcha: ${fmt(todaySpent)}. Kal ka bhi socho!`, t:"info" },
        { m:`💡 Tip: Chhote chhote kharche milke bade ho jaate hain. Track karte raho!`, t:"tip" },
        available>0 ? { m:`✅ Abhi ${fmt(available)} bachane ki gunjayish hai is mahine.`, t:"info" } : null,
      ].filter(Boolean);
      const pick = opts[Math.floor(Math.random()*opts.length)];
      if(pick) pushNotif(pick.m, pick.t);
    };
    nudge();
    const iv = setInterval(nudge, 120000);
    return ()=>clearInterval(iv);
  },[profile, spendPct, available, todaySpent]);

  /* Task time alerts every 30s */
  useEffect(()=>{
    if(!profile) return;
    const iv = setInterval(()=>{
      const now = new Date();
      const hm  = now.getHours()*60+now.getMinutes();
      tasks.filter(t=>!t.done&&t.date===today()&&t.time).forEach(t=>{
        const [th,tm]=t.time.split(":").map(Number);
        const diff=(th*60+tm)-hm;
        if(diff===30) pushNotif(`⏰ 30 min mein: "${t.title}"`, "remind");
        if(diff===5)  pushNotif(`🔔 Sirf 5 min mein: "${t.title}" — abhi karo!`, "remind");
        if(diff===0)  pushNotif(`🚨 Ab karo: "${t.title}"!`, "danger");
      });
      // birthday/event reminders
      tasks.filter(t=>!t.done&&t.type==="event").forEach(t=>{
        const td=new Date(t.date+"T00:00:00");
        const diff=Math.round((td-now)/86400000);
        if(diff===1) pushNotif(`🎉 Kal hai: "${t.title}" — taiyaari kar lo!`, "remind");
        if(diff===0) pushNotif(`🎊 Aaj hai: "${t.title}"! Happy day!`, "info");
      });
    },30000);
    return ()=>clearInterval(iv);
  },[profile,tasks]);

  /* ── Add payment ── */
  function addPayment(){
    if(!form.amount||isNaN(form.amount)||Number(form.amount)<=0) return;
    const p={ id:Date.now(), ...form, amount:Number(form.amount), time:nowT() };
    setPayments(prev=>[p,...prev]);
    setAddedFlash(p);
    setTimeout(()=>setAddedFlash(null),3000);
    // AI spend warning
    const newTotal = monthSpent + p.amount;
    if(limitNum>0 && newTotal>limitNum*0.8){
      pushNotif(`😤 ${profile.name} ji! ${fmt(p.amount)} aur kharcha? Ab limit ka ${pct(newTotal,limitNum)}% ho gaya!`,"warn");
    } else {
      pushNotif(`✅ ${fmt(p.amount)} add hua — ${p.app} se ${p.note}`,"info");
    }
    setForm(f=>({...f,amount:"",note:""}));
    setScreen("home");
  }

  /* ── Add task ── */
  function addTask(){
    if(!taskForm.title.trim()) return;
    setTasks(prev=>[{ id:Date.now(), ...taskForm, done:false },...prev]);
    pushNotif(`📋 Kaam add hua: "${taskForm.title}" — ${taskForm.date} ${taskForm.time}`,"info");
    setTaskForm({ title:"", date:today(), time:"09:00", type:"task", note:"" });
    setShowTaskForm(false);
  }

  /* ── AI Chat ── */
  async function sendAI(){
    if(!aiInput.trim()||aiLoading) return;
    const userMsg = aiInput.trim();
    setAiInput("");
    setAiChat(prev=>[...prev,{ role:"user", content:userMsg }]);
    setAiLoading(true);

    const catData = CATS.map(c=>({
      name:c.name,
      spent: monthPay.filter(p=>p.category===c.name).reduce((s,p)=>s+p.amount,0)
    })).filter(c=>c.spent>0);

    const context = `
Tu RupAI Alarm hai — ek smart Hindi financial advisor app.
User ka naam: ${profile?.name}
Monthly salary: ${fmt(salaryNum)}
Monthly spending limit: ${fmt(limitNum)}
Fixed monthly kharche: ${fmt(fixedTotal)}
Is mahine kharcha: ${fmt(monthSpent)}
Bacha hai: ${fmt(available)}
Limit use: ${spendPct}%
Category wise: ${catData.map(c=>`${c.name}: ${fmt(c.spent)}`).join(", ")}
Total payments: ${payments.length}
Aaj ka kharcha: ${fmt(todaySpent)}

Tu Hinglish mein baat karta hai (Hindi + English mix).
Friendly par serious advice de. Agar jyada kharcha ho to thoda daata bhi de.
Concise rakh — max 4-5 sentences.
`;

    try {
      const res = await fetch("https://api.anthropic.com/v1/messages",{
        method:"POST",
        headers:{ "Content-Type":"application/json" },
        body: JSON.stringify({
          model:"claude-sonnet-4-20250514",
          max_tokens:500,
          system: context,
          messages:[
            ...aiChat.slice(-6).map(m=>({ role:m.role, content:m.content })),
            { role:"user", content:userMsg }
          ]
        })
      });
      const data = await res.json();
      const reply = data.content?.[0]?.text || "Kuch problem aayi, dobara try karo!";
      setAiChat(prev=>[...prev,{ role:"assistant", content:reply }]);
    } catch(e){
      setAiChat(prev=>[...prev,{ role:"assistant", content:"Network issue hai! Thodi der mein try karo." }]);
    }
    setAiLoading(false);
    setTimeout(()=>chatRef.current?.scrollTo({ top:9999, behavior:"smooth" }),100);
  }

  /* ── Charts ── */
  const catChart = CATS.map(c=>({
    name:c.name, icon:c.icon, value:monthPay.filter(p=>p.category===c.name).reduce((s,p)=>s+p.amount,0), color:c.color
  })).filter(c=>c.value>0).sort((a,b)=>b.value-a.value);

  const appChart = UPI_APPS.map(a=>({
    name:a.name, value:monthPay.filter(p=>p.app===a.name).reduce((s,p)=>s+p.amount,0), color:a.color
  })).filter(a=>a.value>0);

  /* ── Setup ── */
  if(!profile) return <SetupWizard onDone={p=>{ setProfile(p); pushNotif(`🎉 Welcome ${p.name} ji! RupAI Alarm shuru ho gaya!`,"info"); }} />;

  const notifCount = notifs.filter(n=>!n.read).length;
  const todayTasks = tasks.filter(t=>t.date===today()&&!t.done);

  /* ════════════════════════════════════
     RENDER
  ════════════════════════════════════ */
  return (
    <div style={{ minHeight:"100vh", background:"#0a0a14", color:"#e8e8f0",
                  fontFamily:"'Segoe UI',sans-serif", paddingBottom:80, maxWidth:480, margin:"0 auto" }}>

      {/* ── TOP BAR ── */}
      <div style={{ position:"sticky", top:0, zIndex:50, background:"#0a0a14cc", backdropFilter:"blur(12px)",
                    borderBottom:"1px solid #1a1a2e", padding:"10px 16px", display:"flex", alignItems:"center", justifyContent:"space-between" }}>
        <div style={{ display:"flex", alignItems:"center", gap:8 }}>
          <span style={{ fontSize:20 }}>💰</span>
          <span style={{ fontWeight:900, fontSize:16, background:"linear-gradient(90deg,#a78bfa,#38bdf8)",
                         WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent" }}>{APP_NAME}</span>
        </div>
        <div style={{ display:"flex", gap:10, alignItems:"center" }}>
          <button onClick={()=>setShowNotifs(!showNotifs)} style={{ background:"#161625", border:"1px solid #252545",
            borderRadius:10, padding:"6px 10px", color:"#fff", cursor:"pointer", position:"relative", fontSize:16 }}>
            🔔
            {notifCount>0 && <span style={{ position:"absolute", top:-4, right:-4, background:"#ef4444",
              borderRadius:"50%", width:16, height:16, fontSize:9, display:"flex", alignItems:"center",
              justifyContent:"center", fontWeight:700 }}>{notifCount>9?"9+":notifCount}</span>}
          </button>
          <div style={{ width:32, height:32, borderRadius:"50%", background:"linear-gradient(135deg,#6C3FD4,#38bdf8)",
                        display:"flex", alignItems:"center", justifyContent:"center", fontSize:14, fontWeight:700 }}>
            {profile.name[0]}
          </div>
        </div>
      </div>

      {/* ── NOTIFICATION PANEL ── */}
      {showNotifs && (
        <div style={{ position:"fixed", top:56, right:8, left:8, maxWidth:464, margin:"0 auto", zIndex:100,
                      background:"#12121f", border:"1px solid #252545", borderRadius:18, padding:16, maxHeight:360, overflowY:"auto",
                      boxShadow:"0 8px 40px #000a" }}>
          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:12 }}>
            <p style={{ margin:0, fontWeight:700, color:"#a78bfa" }}>🔔 Notifications</p>
            <button onClick={()=>{ setNotifs(prev=>prev.map(n=>({...n,read:true}))); setShowNotifs(false); }}
              style={{ background:"none", border:"none", color:"#555", cursor:"pointer", fontSize:13 }}>Sab dekha ✕</button>
          </div>
          {notifs.length===0 && <p style={{ color:"#444", fontSize:13 }}>Koi notification nahi</p>}
          {notifs.map(n=>(
            <div key={n.id} style={{ background: n.type==="danger"?"#1f0a0a": n.type==="warn"?"#1a1200":"#0f1520",
                                     border:`1px solid ${n.type==="danger"?"#7f1d1d":n.type==="warn"?"#713f12":"#1e293b"}`,
                                     borderRadius:10, padding:"10px 12px", marginBottom:8 }}>
              <p style={{ margin:0, fontSize:13, lineHeight:1.5 }}>{n.msg}</p>
              <p style={{ margin:"4px 0 0", fontSize:10, color:"#444" }}>{n.time}</p>
            </div>
          ))}
        </div>
      )}

      {/* ══════════ HOME ══════════ */}
      {screen==="home" && (
        <div>
          {/* Balance card */}
          <div style={{ background:"linear-gradient(135deg,#1a0d3a 0%,#0d1a35 100%)", padding:"20px 16px 24px" }}>
            <p style={{ margin:"0 0 2px", color:"#666", fontSize:12 }}>Namaste {profile.name} ji 👋</p>
            <p style={{ margin:"0 0 16px", color:"#888", fontSize:12 }}>{new Date().toLocaleDateString("en-IN",{weekday:"long",day:"numeric",month:"long"})}</p>

            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:10, marginBottom:14 }}>
              <div style={{ ...STYLES.card, background:"#0f1520" }}>
                <p style={{ margin:0, fontSize:10, color:"#555", textTransform:"uppercase" }}>Aaj ka kharcha</p>
                <p style={{ margin:"4px 0 0", fontSize:22, fontWeight:900, color:"#f87171" }}>{fmt(todaySpent)}</p>
              </div>
              <div style={{ ...STYLES.card, background:"#0f1520" }}>
                <p style={{ margin:0, fontSize:10, color:"#555", textTransform:"uppercase" }}>Is mahine</p>
                <p style={{ margin:"4px 0 0", fontSize:22, fontWeight:900, color:"#fb923c" }}>{fmt(monthSpent)}</p>
              </div>
            </div>

            {/* Available balance */}
            <div style={{ background:"#0d1a0d", border:"1px solid #14532d", borderRadius:14, padding:"12px 16px", marginBottom:12 }}>
              <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center" }}>
                <div>
                  <p style={{ margin:0, fontSize:11, color:"#4ade80" }}>Bacha hai is mahine</p>
                  <p style={{ margin:"2px 0 0", fontSize:26, fontWeight:900, color: available<0?"#f87171":"#4ade80" }}>{fmt(available)}</p>
                </div>
                <div style={{ textAlign:"right" }}>
                  <p style={{ margin:0, fontSize:10, color:"#555" }}>Salary: {fmt(salaryNum)}</p>
                  <p style={{ margin:0, fontSize:10, color:"#555" }}>Fixed: −{fmt(fixedTotal)}</p>
                  <p style={{ margin:0, fontSize:10, color:"#555" }}>Spent: −{fmt(monthSpent)}</p>
                </div>
              </div>
            </div>

            {/* Spend limit bar */}
            {limitNum>0 && (
              <div>
                <div style={{ display:"flex", justifyContent:"space-between", marginBottom:6 }}>
                  <p style={{ margin:0, fontSize:11, color:"#666" }}>Spending limit: {fmt(monthSpent)} / {fmt(limitNum)}</p>
                  <p style={{ margin:0, fontSize:11, fontWeight:700,
                               color: spendPct>90?"#ef4444":spendPct>70?"#f97316":"#22c55e" }}>{spendPct}%</p>
                </div>
                <div style={{ height:8, background:"#1a1a2e", borderRadius:4, overflow:"hidden" }}>
                  <div style={{ height:"100%", width:`${spendPct}%`, borderRadius:4, transition:"width 0.5s",
                                 background: spendPct>90?"#ef4444":spendPct>70?"#f97316":"#22c55e" }} />
                </div>
                {spendPct>80 && <p style={{ margin:"6px 0 0", fontSize:11, color:"#ef4444" }}>
                  ⚠️ {profile.name} ji! Limit ka {spendPct}% ho gaya — zara sambhalo!
                </p>}
              </div>
            )}
          </div>

          {/* Flash */}
          {addedFlash && (
            <div style={{ margin:"12px 16px 0", background:"#0a2010", border:"1px solid #22c55e",
                          borderRadius:12, padding:"10px 14px", display:"flex", gap:10, alignItems:"center" }}>
              <span>✅</span>
              <div>
                <p style={{ margin:0, fontSize:13, color:"#22c55e", fontWeight:700 }}>Add ho gaya!</p>
                <p style={{ margin:0, fontSize:12, color:"#555" }}>{upiApp(addedFlash.app).icon} {addedFlash.app} — {fmt(addedFlash.amount)} — {addedFlash.note}</p>
              </div>
            </div>
          )}

          {/* Today's tasks strip */}
          {todayTasks.length>0 && (
            <div style={{ margin:"12px 16px 0", background:"#0f1520", border:"1px solid #1e3a5f", borderRadius:14, padding:"12px 14px" }}>
              <p style={{ margin:"0 0 8px", fontSize:12, color:"#38bdf8", fontWeight:700 }}>📋 Aaj ke kaam ({todayTasks.length})</p>
              {todayTasks.slice(0,3).map(t=>(
                <div key={t.id} style={{ display:"flex", alignItems:"center", gap:8, marginBottom:6 }}>
                  <button onClick={()=>setTasks(prev=>prev.map(x=>x.id===t.id?{...x,done:true}:x))}
                    style={{ width:18, height:18, borderRadius:4, background:"#1a2a3a", border:"1px solid #2a4a6a",
                             color:"#38bdf8", fontSize:10, cursor:"pointer", flexShrink:0 }}>○</button>
                  <p style={{ margin:0, fontSize:13, flex:1 }}>{t.title}</p>
                  {t.time && <p style={{ margin:0, fontSize:11, color:"#555" }}>{t.time}</p>}
                </div>
              ))}
            </div>
          )}

          {/* Today payments */}
          <div style={{ padding:"16px 16px 0" }}>
            <p style={{ margin:"0 0 10px", fontSize:11, color:"#444", textTransform:"uppercase", letterSpacing:1 }}>Aaj ki payments</p>
            {todayPay.length===0 && (
              <div style={{ textAlign:"center", padding:"32px 0", color:"#333" }}>
                <p style={{ fontSize:36 }}>💸</p>
                <p style={{ fontSize:13 }}>Aaj koi payment nahi — achha hai!</p>
              </div>
            )}
            {todayPay.map(p=>{
              const a=upiApp(p.app), c=cat(p.category);
              return (
                <div key={p.id} style={{ ...STYLES.card, marginBottom:8, display:"flex", alignItems:"center", gap:12 }}>
                  <div style={{ width:40, height:40, borderRadius:12, background:a.color+"22", border:`1.5px solid ${a.color}44`,
                                display:"flex", alignItems:"center", justifyContent:"center", fontSize:18, flexShrink:0 }}>{a.icon}</div>
                  <div style={{ flex:1 }}>
                    <p style={{ margin:0, fontSize:14, fontWeight:600 }}>{p.note}</p>
                    <p style={{ margin:"2px 0 0", fontSize:11, color:"#444" }}>
                      <span style={{ color:a.color }}>{p.app}</span> · {c.icon}{p.category} · {p.time}
                    </p>
                  </div>
                  <div style={{ textAlign:"right" }}>
                    <p style={{ margin:0, fontSize:15, fontWeight:800, color:"#f87171" }}>−{fmt(p.amount)}</p>
                    <button onClick={()=>setPayments(prev=>prev.filter(x=>x.id!==p.id))}
                      style={{ background:"none", border:"none", color:"#333", fontSize:11, cursor:"pointer" }}>🗑️</button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ══════════ ADD PAYMENT ══════════ */}
      {screen==="add" && (
        <div style={{ padding:20 }}>
          <h2 style={{ margin:"0 0 20px", color:"#a78bfa" }}>💳 Nayi Payment</h2>

          <Lbl>Date</Lbl>
          <input type="date" value={form.date} onChange={e=>setForm(f=>({...f,date:e.target.value}))} style={{ ...STYLES.input, marginBottom:14 }} />

          <Lbl>UPI App</Lbl>
          <div style={{ display:"flex", flexWrap:"wrap", gap:8, marginBottom:16 }}>
            {UPI_APPS.map(a=>(
              <button key={a.name} onClick={()=>setForm(f=>({...f,app:a.name}))}
                style={STYLES.pill(form.app===a.name, a.color)}>
                {a.icon} {a.name}
              </button>
            ))}
          </div>

          <Lbl>Amount (₹)</Lbl>
          <input type="number" placeholder="Kitne rupaye?" value={form.amount}
            onChange={e=>setForm(f=>({...f,amount:e.target.value}))}
            style={{ ...STYLES.input, fontSize:22, fontWeight:700, marginBottom:14 }} />

          <Lbl>Kahan ki payment?</Lbl>
          <input type="text" placeholder="Jaise: Swiggy, Petrol, Amazon..." value={form.note}
            onChange={e=>setForm(f=>({...f,note:e.target.value}))}
            style={{ ...STYLES.input, marginBottom:14 }} />

          <Lbl>Category</Lbl>
          <div style={{ display:"flex", flexWrap:"wrap", gap:8, marginBottom:24 }}>
            {CATS.map(c=>(
              <button key={c.name} onClick={()=>setForm(f=>({...f,category:c.name}))}
                style={STYLES.pill(form.category===c.name, c.color)}>
                {c.icon} {c.name}
              </button>
            ))}
          </div>

          <button onClick={addPayment} style={STYLES.btn()}>✅ Add Karo</button>
        </div>
      )}

      {/* ══════════ BUDGET ══════════ */}
      {screen==="budget" && (
        <div style={{ padding:20 }}>
          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:16 }}>
            <h2 style={{ margin:0, color:"#a78bfa" }}>💼 Budget</h2>
            <button onClick={()=>setShowBudgetEdit(!showBudgetEdit)}
              style={{ background:"#252545", border:"none", borderRadius:8, padding:"6px 12px", color:"#a78bfa", cursor:"pointer", fontSize:12 }}>
              {showBudgetEdit?"Done ✓":"Edit ✏️"}
            </button>
          </div>

          {/* Summary cards */}
          <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:10, marginBottom:16 }}>
            {[
              { l:"Monthly Salary", v:fmt(salaryNum), c:"#a78bfa" },
              { l:"Fixed Kharche", v:fmt(fixedTotal), c:"#f97316" },
              { l:"Spending Limit", v:fmt(limitNum), c:"#38bdf8" },
              { l:"Bacha Hai", v:fmt(available), c:available<0?"#f87171":"#4ade80" },
            ].map(x=>(
              <div key={x.l} style={{ ...STYLES.card }}>
                <p style={{ margin:0, fontSize:10, color:"#555", textTransform:"uppercase" }}>{x.l}</p>
                <p style={{ margin:"4px 0 0", fontSize:18, fontWeight:800, color:x.c }}>{x.v}</p>
              </div>
            ))}
          </div>

          {/* Fixed expenses list */}
          <p style={{ fontSize:11, color:"#555", textTransform:"uppercase", letterSpacing:1, marginBottom:10 }}>Fixed Monthly Kharche</p>
          {profile.fixedExpenses.map((f,i)=>(
            <div key={f.id} style={{ ...STYLES.card, marginBottom:8, display:"flex", alignItems:"center", gap:10 }}>
              {showBudgetEdit ? (
                <button onClick={()=>setProfile(prev=>({ ...prev,
                  fixedExpenses:prev.fixedExpenses.map((x,j)=>j===i?{...x,active:!x.active}:x) }))}
                  style={{ background:f.active?"#6C3FD4":"#252535", border:"none", borderRadius:6,
                           width:24, height:24, color:"#fff", cursor:"pointer", fontSize:11, flexShrink:0 }}>
                  {f.active?"✓":"×"}
                </button>
              ) : (
                <span style={{ fontSize:18 }}>{f.icon}</span>
              )}
              <span style={{ flex:1, fontSize:13, color:f.active?"#ccc":"#444" }}>{f.label}</span>
              {showBudgetEdit ? (
                <input type="number" placeholder="₹0" value={f.amount}
                  onChange={e=>setProfile(prev=>({ ...prev,
                    fixedExpenses:prev.fixedExpenses.map((x,j)=>j===i?{...x,amount:e.target.value}:x) }))}
                  style={{ ...STYLES.input, width:90, padding:"6px 8px", fontSize:13, textAlign:"right" }} />
              ) : (
                <span style={{ color: f.active&&f.amount?"#f87171":"#333", fontWeight:700, fontSize:13 }}>
                  {f.active&&f.amount ? fmt(f.amount) : "—"}
                </span>
              )}
            </div>
          ))}

          {/* Update salary/limit inline */}
          {showBudgetEdit && (
            <div style={{ marginTop:16 }}>
              <Lbl>Salary update karo</Lbl>
              <input type="number" value={profile.salary}
                onChange={e=>setProfile(p=>({...p,salary:e.target.value}))}
                style={{ ...STYLES.input, marginBottom:10 }} />
              <Lbl>Spending limit update karo</Lbl>
              <input type="number" value={profile.spendLimit}
                onChange={e=>setProfile(p=>({...p,spendLimit:e.target.value}))}
                style={{ ...STYLES.input, marginBottom:10 }} />
            </div>
          )}
        </div>
      )}

      {/* ══════════ TASKS ══════════ */}
      {screen==="tasks" && (
        <div style={{ padding:20 }}>
          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:16 }}>
            <h2 style={{ margin:0, color:"#38bdf8" }}>📋 Kaam & Events</h2>
            <button onClick={()=>setShowTaskForm(!showTaskForm)}
              style={{ background:"linear-gradient(135deg,#6C3FD4,#38bdf8)", border:"none", borderRadius:10,
                       padding:"8px 14px", color:"#fff", cursor:"pointer", fontSize:13, fontWeight:700 }}>
              {showTaskForm?"✕ Band":"+ Add"}
            </button>
          </div>

          {showTaskForm && (
            <div style={{ ...STYLES.card, marginBottom:16 }}>
              <Lbl>Kya karna hai?</Lbl>
              <input placeholder="Jaise: Bijli bill bharo, Birthday party..." value={taskForm.title}
                onChange={e=>setTaskForm(f=>({...f,title:e.target.value}))}
                style={{ ...STYLES.input, marginBottom:10 }} />

              <div style={{ display:"flex", gap:10, marginBottom:10 }}>
                <div style={{ flex:1 }}>
                  <Lbl>Type</Lbl>
                  <div style={{ display:"flex", gap:6 }}>
                    {[{v:"task",l:"📋 Kaam"},{v:"event",l:"🎉 Event"},{v:"birthday",l:"🎂 Birthday"}].map(t=>(
                      <button key={t.v} onClick={()=>setTaskForm(f=>({...f,type:t.v}))}
                        style={{ ...STYLES.pill(taskForm.type===t.v,"#38bdf8"), flex:1, textAlign:"center" }}>{t.l}</button>
                    ))}
                  </div>
                </div>
              </div>

              <div style={{ display:"flex", gap:10, marginBottom:10 }}>
                <div style={{ flex:1 }}>
                  <Lbl>Date</Lbl>
                  <input type="date" value={taskForm.date} onChange={e=>setTaskForm(f=>({...f,date:e.target.value}))}
                    style={{ ...STYLES.input }} />
                </div>
                <div style={{ flex:1 }}>
                  <Lbl>Time</Lbl>
                  <input type="time" value={taskForm.time} onChange={e=>setTaskForm(f=>({...f,time:e.target.value}))}
                    style={{ ...STYLES.input }} />
                </div>
              </div>

              <Lbl>Note (optional)</Lbl>
              <input placeholder="Koi extra detail..." value={taskForm.note}
                onChange={e=>setTaskForm(f=>({...f,note:e.target.value}))}
                style={{ ...STYLES.input, marginBottom:12 }} />

              <button onClick={addTask} style={STYLES.btn("#38bdf8")}>✅ Add Karo</button>
            </div>
          )}

          {/* Today */}
          {tasks.filter(t=>t.date===today()).length>0 && (
            <>
              <p style={{ fontSize:11, color:"#555", textTransform:"uppercase", letterSpacing:1, marginBottom:8 }}>Aaj</p>
              {tasks.filter(t=>t.date===today()).map(t=>(
                <TaskCard key={t.id} t={t}
                  onDone={()=>setTasks(prev=>prev.map(x=>x.id===t.id?{...x,done:!x.done}:x))}
                  onDel={()=>setTasks(prev=>prev.filter(x=>x.id!==t.id))} />
              ))}
            </>
          )}

          {/* Upcoming */}
          {tasks.filter(t=>t.date>today()&&!t.done).length>0 && (
            <>
              <p style={{ fontSize:11, color:"#555", textTransform:"uppercase", letterSpacing:1, margin:"16px 0 8px" }}>Aane wala</p>
              {tasks.filter(t=>t.date>today()&&!t.done).sort((a,b)=>a.date.localeCompare(b.date)).map(t=>(
                <TaskCard key={t.id} t={t}
                  onDone={()=>setTasks(prev=>prev.map(x=>x.id===t.id?{...x,done:!x.done}:x))}
                  onDel={()=>setTasks(prev=>prev.filter(x=>x.id!==t.id))} />
              ))}
            </>
          )}

          {tasks.length===0 && (
            <div style={{ textAlign:"center", padding:"40px 0", color:"#333" }}>
              <p style={{ fontSize:36 }}>📋</p>
              <p style={{ fontSize:13 }}>Koi kaam nahi — enjoy karo!</p>
            </div>
          )}
        </div>
      )}

      {/* ══════════ ANALYTICS ══════════ */}
      {screen==="analytics" && (
        <div style={{ padding:20 }}>
          <h2 style={{ margin:"0 0 16px", color:"#f97316" }}>📊 Analytics</h2>

          <div style={{ ...STYLES.card, textAlign:"center", marginBottom:16 }}>
            <p style={{ margin:0, color:"#555", fontSize:11 }}>Is mahine total ({monthPay.length} payments)</p>
            <p style={{ margin:"4px 0 0", fontSize:30, fontWeight:900, color:"#f87171" }}>{fmt(monthSpent)}</p>
          </div>

          {catChart.length===0 && <p style={{ color:"#444", textAlign:"center", padding:32 }}>Is mahine koi payment nahi</p>}

          {catChart.length>0 && (
            <>
              <p style={{ fontSize:11, color:"#555", textTransform:"uppercase", letterSpacing:1, marginBottom:10 }}>Category wise</p>
              <div style={{ ...STYLES.card, marginBottom:16 }}>
                <ResponsiveContainer width="100%" height={190}>
                  <PieChart>
                    <Pie data={catChart} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={75}
                         label={({name,percent})=>`${Math.round(percent*100)}%`} labelLine={false}>
                      {catChart.map((e,i)=><Cell key={i} fill={e.color} />)}
                    </Pie>
                    <Tooltip formatter={v=>fmt(v)} />
                  </PieChart>
                </ResponsiveContainer>
                {catChart.map(c=>(
                  <div key={c.name} style={{ display:"flex", alignItems:"center", gap:8, marginBottom:6 }}>
                    <div style={{ width:10, height:10, borderRadius:2, background:c.color, flexShrink:0 }} />
                    <span style={{ fontSize:13, flex:1 }}>{c.icon} {c.name}</span>
                    <span style={{ fontSize:13, fontWeight:700, color:c.color }}>{fmt(c.value)}</span>
                  </div>
                ))}
              </div>

              {appChart.length>0 && (
                <>
                  <p style={{ fontSize:11, color:"#555", textTransform:"uppercase", letterSpacing:1, marginBottom:10 }}>App wise</p>
                  <div style={{ ...STYLES.card, marginBottom:16 }}>
                    <ResponsiveContainer width="100%" height={160}>
                      <BarChart data={appChart}>
                        <XAxis dataKey="name" tick={{ fill:"#555", fontSize:10 }} />
                        <YAxis hide />
                        <Tooltip formatter={v=>fmt(v)} />
                        <Bar dataKey="value" radius={[6,6,0,0]}>
                          {appChart.map((e,i)=><Cell key={i} fill={e.color} />)}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </>
              )}
            </>
          )}
        </div>
      )}

      {/* ══════════ AI ADVISOR ══════════ */}
      {screen==="ai" && (
        <div style={{ display:"flex", flexDirection:"column", height:"calc(100vh - 120px)" }}>
          <div style={{ padding:"16px 16px 8px" }}>
            <h2 style={{ margin:0, color:"#a78bfa" }}>🤖 RupAI Advisor</h2>
            <p style={{ margin:"4px 0 0", color:"#444", fontSize:12 }}>Apna financial dost — poocho kuch bhi!</p>
          </div>

          {/* Quick prompts */}
          {aiChat.length===0 && (
            <div style={{ padding:"0 16px 12px", display:"flex", flexWrap:"wrap", gap:8 }}>
              {[
                "Mera kharcha kaisa chal raha hai?",
                "Mujhe paisa kaise bachana chahiye?",
                "Is mahine kahan jyada kharcha hua?",
                "Meri EMI ke baad kitna bacha?",
                "Paisa bachane ke tips do",
              ].map(q=>(
                <button key={q} onClick={()=>{ setAiInput(q); }}
                  style={{ background:"#161625", border:"1px solid #252545", borderRadius:20,
                           padding:"7px 13px", color:"#a78bfa", fontSize:12, cursor:"pointer" }}>{q}</button>
              ))}
            </div>
          )}

          {/* Chat messages */}
          <div ref={chatRef} style={{ flex:1, overflowY:"auto", padding:"0 16px 12px" }}>
            {aiChat.map((m,i)=>(
              <div key={i} style={{ display:"flex", justifyContent: m.role==="user"?"flex-end":"flex-start", marginBottom:10 }}>
                {m.role==="assistant" && (
                  <div style={{ width:28, height:28, borderRadius:"50%", background:"linear-gradient(135deg,#6C3FD4,#38bdf8)",
                                display:"flex", alignItems:"center", justifyContent:"center", fontSize:12,
                                marginRight:8, flexShrink:0, alignSelf:"flex-end" }}>🤖</div>
                )}
                <div style={{ maxWidth:"78%", background: m.role==="user"?"linear-gradient(135deg,#6C3FD4,#4f46e5)":"#161625",
                               border: m.role==="assistant"?"1px solid #252545":"none",
                               borderRadius: m.role==="user"?"18px 18px 4px 18px":"18px 18px 18px 4px",
                               padding:"10px 14px" }}>
                  <p style={{ margin:0, fontSize:13, lineHeight:1.6 }}>{m.content}</p>
                </div>
              </div>
            ))}
            {aiLoading && (
              <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:10 }}>
                <div style={{ width:28, height:28, borderRadius:"50%", background:"linear-gradient(135deg,#6C3FD4,#38bdf8)",
                              display:"flex", alignItems:"center", justifyContent:"center", fontSize:12 }}>🤖</div>
                <div style={{ background:"#161625", border:"1px solid #252545", borderRadius:"18px 18px 18px 4px",
                              padding:"10px 14px" }}>
                  <span style={{ color:"#555", fontSize:13 }}>Soch raha hoon... ⏳</span>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div style={{ padding:"8px 16px 12px", borderTop:"1px solid #1a1a2e", display:"flex", gap:8 }}>
            <input placeholder="Poocho kuch bhi..." value={aiInput}
              onChange={e=>setAiInput(e.target.value)}
              onKeyDown={e=>e.key==="Enter"&&sendAI()}
              style={{ ...STYLES.input, flex:1, marginBottom:0 }} />
            <button onClick={sendAI} disabled={aiLoading}
              style={{ background:"linear-gradient(135deg,#6C3FD4,#38bdf8)", border:"none", borderRadius:10,
                       padding:"0 16px", color:"#fff", cursor:"pointer", fontSize:18, flexShrink:0 }}>
              {aiLoading?"⏳":"➤"}
            </button>
          </div>
        </div>
      )}

      {/* ══════════ BOTTOM NAV ══════════ */}
      <div style={{ position:"fixed", bottom:0, left:"50%", transform:"translateX(-50%)", width:"100%", maxWidth:480,
                    background:"#0d0d18", borderTop:"1px solid #1a1a2e",
                    display:"flex", justifyContent:"space-around", padding:"8px 0 14px", zIndex:40 }}>
        {[
          { id:"home",      icon:"🏠", label:"Home"     },
          { id:"add",       icon:"➕", label:"Add"      },
          { id:"budget",    icon:"💼", label:"Budget"   },
          { id:"tasks",     icon:"📋", label:"Kaam"     },
          { id:"analytics", icon:"📊", label:"Chart"    },
          { id:"ai",        icon:"🤖", label:"AI"       },
        ].map(tab=>(
          <button key={tab.id} onClick={()=>setScreen(tab.id)}
            style={{ background:"none", border:"none", cursor:"pointer", display:"flex", flexDirection:"column",
                     alignItems:"center", gap:2, padding:"4px 6px" }}>
            <span style={{ fontSize:20 }}>{tab.icon}</span>
            <span style={{ fontSize:9, color: screen===tab.id?"#a78bfa":"#444", fontWeight: screen===tab.id?700:400 }}>{tab.label}</span>
            {screen===tab.id && <div style={{ width:4, height:4, borderRadius:"50%", background:"#a78bfa" }} />}
          </button>
        ))}
      </div>

      <style>{`
        input[type="date"]::-webkit-calendar-picker-indicator,
        input[type="time"]::-webkit-calendar-picker-indicator { filter:invert(0.6); }
        input::placeholder { color:#333; }
        *{ -webkit-tap-highlight-color:transparent; scrollbar-width:thin; scrollbar-color:#252545 transparent; }
        ::-webkit-scrollbar{ width:4px; }
        ::-webkit-scrollbar-thumb{ background:#252545; border-radius:4px; }
      `}</style>
    </div>
  );

  async function sendAI(){
    if(!aiInput.trim()||aiLoading) return;
    const userMsg=aiInput.trim();
    setAiInput("");
    setAiChat(prev=>[...prev,{role:"user",content:userMsg}]);
    setAiLoading(true);
    const catData=CATS.map(c=>({name:c.name,spent:monthPay.filter(p=>p.category===c.name).reduce((s,p)=>s+p.amount,0)})).filter(c=>c.spent>0);
    const sys=`Tu RupAI Alarm hai — ek smart Hindi financial advisor.
User: ${profile?.name} | Salary: ${fmt(salaryNum)} | Limit: ${fmt(limitNum)} | Fixed: ${fmt(fixedTotal)}
Is mahine kharcha: ${fmt(monthSpent)} | Bacha: ${fmt(available)} | Limit use: ${spendPct}%
Categories: ${catData.map(c=>`${c.name}=${fmt(c.spent)}`).join(", ")}
Hinglish mein baat kar. Friendly + helpful. Jyada kharche pe thoda daato. Max 5 sentences.`;
    try{
      const res=await fetch("https://api.anthropic.com/v1/messages",{method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({model:"claude-sonnet-4-20250514",max_tokens:500,system:sys,
          messages:[...aiChat.slice(-8).map(m=>({role:m.role,content:m.content})),{role:"user",content:userMsg}]})});
      const data=await res.json();
      const reply=data.content?.[0]?.text||"Kuch dikkat aayi, dobara try karo!";
      setAiChat(prev=>[...prev,{role:"assistant",content:reply}]);
    }catch(e){
      setAiChat(prev=>[...prev,{role:"assistant",content:"Network issue! Thodi der mein try karo."}]);
    }
    setAiLoading(false);
    setTimeout(()=>chatRef.current?.scrollTo({top:9999,behavior:"smooth"}),100);
  }
}

/* ── Sub-components ── */
function Lbl({children}){ return <p style={{margin:"0 0 6px",fontSize:11,color:"#555",textTransform:"uppercase",letterSpacing:0.5}}>{children}</p>; }

function TaskCard({t,onDone,onDel}){
  const typeColor = t.type==="birthday"?"#ec4899":t.type==="event"?"#f97316":"#38bdf8";
  const typeIcon  = t.type==="birthday"?"🎂":t.type==="event"?"🎉":"📋";
  return (
    <div style={{ background:"#161625", border:`1px solid ${t.done?"#1a1a2e":"#252545"}`, borderRadius:14,
                  padding:"12px 14px", marginBottom:8, display:"flex", alignItems:"center", gap:10,
                  opacity: t.done?0.45:1 }}>
      <button onClick={onDone} style={{ width:22, height:22, borderRadius:6, flexShrink:0, cursor:"pointer",
        background: t.done?"#22c55e":"#1a2030", border:`1.5px solid ${t.done?"#22c55e":typeColor}`,
        color: t.done?"#fff":typeColor, fontSize:11 }}>{t.done?"✓":"○"}</button>
      <span style={{ fontSize:16 }}>{typeIcon}</span>
      <div style={{ flex:1 }}>
        <p style={{ margin:0, fontSize:13, fontWeight:600, textDecoration: t.done?"line-through":"none" }}>{t.title}</p>
        <p style={{ margin:"2px 0 0", fontSize:11, color:"#444" }}>
          {t.date}{t.time?` · ${t.time}`:""}{t.note?` · ${t.note}`:""}
        </p>
      </div>
      <button onClick={onDel} style={{ background:"none", border:"none", color:"#333", cursor:"pointer", fontSize:14 }}>🗑️</button>
    </div>
  );
}
