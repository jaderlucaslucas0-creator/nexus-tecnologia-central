export type SpeechCallbacks={
  onText:(text:string)=>void;
  onListening:(value:boolean)=>void;
  onError:(message:string)=>void;
};

type Recognition=SpeechRecognition;
type RecognitionConstructor=new()=>Recognition;

declare global {
  interface Window {
    SpeechRecognition?: RecognitionConstructor;
    webkitSpeechRecognition?: RecognitionConstructor;
  }
}

export class JarvisSpeech {
  private recognition: Recognition|null=null;
  private active=false;
  private wakeWord="jarvis";

  constructor(private callbacks:SpeechCallbacks){}

  available(){
    return Boolean(window.SpeechRecognition||window.webkitSpeechRecognition);
  }

  start(){
    const Constructor=window.SpeechRecognition||window.webkitSpeechRecognition;
    if(!Constructor){
      this.callbacks.onError("Reconhecimento de voz não está disponível neste ambiente.");
      return;
    }
    this.active=true;
    const recognition=new Constructor();
    recognition.lang="pt-BR";
    recognition.continuous=true;
    recognition.interimResults=false;
    recognition.onstart=()=>this.callbacks.onListening(true);
    recognition.onend=()=>{
      this.callbacks.onListening(false);
      if(this.active) setTimeout(()=>this.start(),250);
    };
    recognition.onerror=(event)=>this.callbacks.onError(`Microfone: ${event.error}`);
    recognition.onresult=(event)=>{
      const result=event.results[event.results.length-1];
      if(!result?.isFinal)return;
      const text=result[0]?.transcript?.trim()||"";
      if(!text)return;
      const normalized=text.toLowerCase();
      const index=normalized.indexOf(this.wakeWord);
      if(index>=0){
        const command=text.slice(index+this.wakeWord.length).trim();
        this.speak("Sim?");
        if(command) this.callbacks.onText(command);
      }
    };
    this.recognition=recognition;
    recognition.start();
  }

  stop(){
    this.active=false;
    this.recognition?.stop();
    this.recognition=null;
    this.callbacks.onListening(false);
  }

  speak(text:string){
    if(!("speechSynthesis" in window))return;
    window.speechSynthesis.cancel();
    const utterance=new SpeechSynthesisUtterance(text);
    utterance.lang="pt-BR";
    utterance.rate=0.96;
    utterance.pitch=0.82;
    window.speechSynthesis.speak(utterance);
  }
}
