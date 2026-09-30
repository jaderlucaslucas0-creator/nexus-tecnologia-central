import { useMemo, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { motion } from "framer-motion";
import { useEffect, useRef } from "react";
import { JarvisSpeech } from "./speech";

type Role="user"|"jarvis";
type Message={role:Role;text:string;time:string};
const now=()=>new Date().toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"});

export default function App(){
 const [messages,setMessages]=useState<Message[]>([{role:"jarvis",text:"Todos os sistemas principais estão online. Aguardando seu comando.",time:now()}]);
 const [input,setInput]=useState(""); const [listening,setListening]=useState(false); const [active,setActive]=useState("CONVERSA"); const [system,setSystem]=useState("ONLINE");
 const [apiEndpoint,setApiEndpoint]=useState(localStorage.getItem("jarvis_endpoint")||"");
 const [apiKey,setApiKey]=useState(localStorage.getItem("jarvis_key")||"");
 const [model,setModel]=useState(localStorage.getItem("jarvis_model")||"");
 const [memory,setMemory]=useState<string[]>(JSON.parse(localStorage.getItem("jarvis_memory")||"[]"));
 const speech=useRef<JarvisSpeech|null>(null);
 useEffect(()=>{ speech.current=new JarvisSpeech({onText:(text)=>{setInput(text); setTimeout(()=>sendText(text),0)},onListening:setListening,onError:(message)=>{setSystem("WARNING"); setMessages(m=>[...m,{role:"jarvis",text:message,time:now()}])}}); return ()=>speech.current?.stop(); },[]);
 async function sendText(text:string){ const reply=await respond(text); setMessages(m=>[...m,{role:"jarvis",text:reply,time:now()}]); speech.current?.speak(reply); }
 const stats=useMemo(()=>[["NÚCLEO","ONLINE"],["IA","READY"],["MEMÓRIA","ONLINE"],["SEGURANÇA","ACTIVE"]],[]);
 async function respond(command:string){
  const c=command.toLowerCase().trim();
  if(c==="status"||c.includes("status")) return "Status: "+await invoke<string>("jarvis_status");
  if(c.includes("sistema")) { const info=await invoke<{os:string;arch:string;hostname:string}>("system_info"); return `Sistema: ${info.os} • ${info.arch} • ${info.hostname}`; }
  if(c.startsWith("abrir ")) { const url=c.slice(6).trim(); if(url.startsWith("http")) { await invoke("open_url",{url}); return "Abrindo o endereço solicitado."; } }
  if(c.includes("hora")) return "Agora são "+now()+".";
  if(c.includes("olá")||c.includes("ola")) return "Olá. JARVIS pronto para executar seus comandos.";
  if(c.includes("ajuda")) return "Experimente: status, sistema, hora, abrir https://..., abrir calculadora ou pesquisar.";
  if(c.includes("limpar")) { setMessages([]); return ""; }
  if(c.startsWith("memorize ")||c.startsWith("guarde ")){ const value=command.split(" ").slice(1).join(" ").trim(); const next=[...memory,value]; setMemory(next); localStorage.setItem("jarvis_memory",JSON.stringify(next)); return "Memória salva."; }
  if(c.includes("abrir calculadora")){await invoke("launch_app",{app:"calc"});return "Calculadora aberta."}
  if(c.includes("abrir bloco de notas")){await invoke("launch_app",{app:"notepad"});return "Bloco de notas aberto."}
  if(c.startsWith("pesquisar ")||c.startsWith("pesquise ")){const q=command.replace(/^pesquis(ar|e)\s+/i,""); const results=await invoke<any[]>("web_search",{query:q}); return results.length?"Encontrei "+results.length+" resultados para "+q+".":"Não encontrei resultados."}
  if(apiEndpoint){ const context=messages.slice(-12).map(m=>({role:m.role==="jarvis"?"assistant":"user",content:m.text})); return await invoke<string>("ai_chat",{endpoint:apiEndpoint,apiKey,model,system:"Você é JARVIS, assistente pessoal em português do Brasil. Seja útil, objetivo e seguro. Não execute ações perigosas sem confirmação.",messages:[...context,{role:"user",content:command}]}); }
  return "Comando recebido. O núcleo nativo está ativo. A próxima camada conectará IA, voz e automações.";
 }
 async function send(){
  const text=input.trim(); if(!text)return; setInput("");
  setMessages(m=>[...m,{role:"user",text,time:now()}]);
  try { const reply=await respond(text); if(reply){setMessages(m=>[...m,{role:"jarvis",text:reply,time:now()}]); speech.current?.speak(reply);} }
  catch(e){ setSystem("WARNING"); setMessages(m=>[...m,{role:"jarvis",text:"Não consegui executar o comando com segurança.",time:now()}]); }
 }
 return <div className="shell">
  <aside className="sidebar"><div className="brand"><div className="brandMark">J</div><div><strong>JARVIS</strong><small>AI CORE</small></div></div>
   <nav>{["CONVERSA","MEMÓRIA","AUTOMAÇÕES","SISTEMA","CONFIGURAÇÕES"].map(item=><button key={item} className={active===item?"selected":""} onClick={()=>setActive(item)}>{item}</button>)}</nav>
   <div className="sideBottom"><span className="online"/><div><b>SISTEMA {system}</b><small>NEXUS TECNOLOGIA</small></div></div>
  </aside>
  <main className="main"><header className="top"><div><span>JARVIS AI</span><small>DESKTOP INTELLIGENCE PLATFORM</small></div><div className="connection"><i/> CONNECTED</div></header>
   <section className="workspace"><div className="hero"><div className={"orb "+(listening?"listen":"")}><div className="orbCore">J</div><div className="orbRing a"/><div className="orbRing b"/><div className="orbRing c"/></div>
    <motion.h1 animate={{opacity:[.75,1,.75]}} transition={{duration:3,repeat:Infinity}}>JARVIS</motion.h1><p>{listening?"OUVINDO SEU COMANDO":"PRONTO PARA RECEBER COMANDOS"}</p>
    <button className={"listenBtn "+(listening?"on":"")} onClick={()=>{if(listening)speech.current?.stop();else speech.current?.start();}}>🎙 {listening?"PARAR ESCUTA":"ATIVAR MICROFONE"}</button>
   </div>
   <div className="panel"><div className="panelTitle"><span>{active}</span><small>v1.0.1</small></div>
    {active==="MEMÓRIA"?<div className="placeholder"><h3>MEMÓRIA</h3><p>{memory.length?memory.map((m,i)=><span key={i} style={{display:"block",margin:"8px"}}>• {m}</span>):"Nenhuma memória salva."}</p></div>:active==="CONFIGURAÇÕES"?<div className="settings"><input value={apiEndpoint} onChange={e=>{setApiEndpoint(e.target.value);localStorage.setItem("jarvis_endpoint",e.target.value)}} placeholder="Endpoint compatível com OpenAI"/><input value={apiKey} onChange={e=>{setApiKey(e.target.value);localStorage.setItem("jarvis_key",e.target.value)}} placeholder="Chave da API"/><input value={model} onChange={e=>{setModel(e.target.value);localStorage.setItem("jarvis_model",e.target.value)}} placeholder="Modelo"/><p>As configurações ficam salvas localmente neste computador.</p></div>:active==="CONVERSA"?<div className="conversation">{messages.map((m,i)=><div className={"message "+m.role} key={i}><div className="avatar">{m.role==="jarvis"?"J":"V"}</div><div><b>{m.role==="jarvis"?"JARVIS":"VOCÊ"}</b><small>{m.time}</small><p>{m.text}</p></div></div>)}</div>:<div className="placeholder">Módulo <b>{active}</b> preparado para integração.</div>}
    <div className="composer"><input value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>e.key==="Enter"&&send()} placeholder="Digite um comando..."/><button onClick={send}>ENVIAR</button></div>
   </div></section>
   <footer className="statusGrid">{stats.map(([a,b])=><div key={a}><small>{a}</small><b>{b}</b></div>)}</footer>
  </main>
 </div>;
}
