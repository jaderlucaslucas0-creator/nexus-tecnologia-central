import { useState } from "react";
import { motion } from "framer-motion";

type Message={role:"user"|"jarvis";text:string};

export default function App(){
  const [messages,setMessages]=useState<Message[]>([
    {role:"jarvis",text:"Sistemas online. JARVIS AI está pronto."}
  ]);
  const [input,setInput]=useState("");
  const [listening,setListening]=useState(false);

  function send(){
    const text=input.trim();
    if(!text)return;
    setMessages(m=>[...m,{role:"user",text},{role:"jarvis",text:"Comando recebido. O núcleo nativo será conectado nesta etapa."}]);
    setInput("");
  }

  return <main className="app">
    <header><div><span className="dot"/> JARVIS AI</div><small>v0.1 • SYSTEM ONLINE</small></header>
    <section className="hud">
      <motion.div className={"core "+(listening?"listening":"")} animate={{scale:listening?[1,1.08,1]:1}} transition={{repeat:listening?Infinity:0,duration:1.4}}>
        <div className="ring ring1"/><div className="ring ring2"/><span>J</span>
      </motion.div>
      <h1>{listening?"OUVINDO...":"JARVIS"}</h1>
      <p>{listening?"Fale seu comando":"Assistente pessoal • sistema pronto"}</p>
    </section>
    <section className="chat">{messages.map((m,i)=><div className={"msg "+m.role} key={i}><b>{m.role==="user"?"VOCÊ":"JARVIS"}</b><span>{m.text}</span></div>)}</section>
    <footer>
      <button className={listening?"active":""} onClick={()=>setListening(v=>!v)}>🎙</button>
      <input value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>e.key==="Enter"&&send()} placeholder="Digite um comando para JARVIS..."/>
      <button onClick={send}>ENVIAR</button>
    </footer>
  </main>;
}
