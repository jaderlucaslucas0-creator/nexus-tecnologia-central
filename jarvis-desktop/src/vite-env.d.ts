interface SpeechRecognitionEvent extends Event {
  readonly results: SpeechRecognitionResultList;
}
interface SpeechRecognitionErrorEvent extends Event {
  readonly error: string;
}
interface SpeechRecognitionResult {
  readonly isFinal: boolean;
  readonly length: number;
  [index:number]: SpeechRecognitionAlternative;
}
interface SpeechRecognitionResultList {
  readonly length: number;
  [index:number]: SpeechRecognitionResult;
}
interface SpeechRecognitionAlternative {
  readonly transcript: string;
  readonly confidence: number;
}
interface SpeechRecognition {
  lang:string;
  continuous:boolean;
  interimResults:boolean;
  onstart:(event:Event)=>void;
  onend:(event:Event)=>void;
  onerror:(event:SpeechRecognitionErrorEvent)=>void;
  onresult:(event:SpeechRecognitionEvent)=>void;
  start():void;
  stop():void;
}
declare var SpeechRecognition: {new():SpeechRecognition};
