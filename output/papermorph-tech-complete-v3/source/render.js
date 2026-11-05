/* Offline adapter: executes unmodified drawing/timeline functions from pinned Papermorph.
 * Official browser exporter cannot run here: Chromium's local socket is blocked.
 * This adapter does NOT emulate the complete player. It serializes deterministic SVG frames.
 */
'use strict';
const fs=require('fs'), path=require('path'), vm=require('vm'), sharp=require('sharp'), {spawn}=require('child_process');
sharp.concurrency(2); sharp.cache({memory:64,files:8,items:50});
const ROOT=__dirname, STYLE=process.argv[2]||'gouache', FPS=+(process.env.FPS||24), HEIGHT=+(process.env.HEIGHT||1920), WIDTH=Math.round(HEIGHT*9/16);
const START=+(process.env.START||0), END=+(process.env.END||18), TAG=process.env.TAG||'v2';
const OUT=path.join(ROOT,'output'), REVIEW=path.join(ROOT,'review');fs.mkdirSync(OUT,{recursive:true});fs.mkdirSync(REVIEW,{recursive:true});
const xml=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
class El{
 constructor(tag){this.tagName=tag;this.attrs={};this.children=[];this.style={};this._text='';}
 setAttribute(k,v){this.attrs[k]=String(v);}setAttributeNS(ns,k,v){this.setAttribute(k,v);}getAttribute(k){return this.attrs[k]??null;}removeAttribute(k){delete this.attrs[k];}
 appendChild(c){this.children.push(c);c.parentNode=this;return c;} remove(){if(this.parentNode)this.parentNode.children=this.parentNode.children.filter(c=>c!==this);}
 set textContent(v){this._text=String(v);this.children=[];}get textContent(){return this._text;}
 serialize(){const a={...this.attrs}, sty=Object.entries(this.style).map(([k,v])=>k.replace(/[A-Z]/g,m=>'-'+m.toLowerCase())+':'+v).join(';');if(sty)a.style=sty;return '<'+this.tagName+Object.entries(a).map(([k,v])=>' '+k+'="'+xml(v)+'"').join('')+'>'+xml(this._text)+this.children.map(x=>x.serialize()).join('')+'</'+this.tagName+'>';}
}
const raw=fs.readFileSync(path.join(ROOT,'vendor/engine/engine.js'),'utf8');
const drawing=raw.slice(raw.indexOf('function mk('),raw.indexOf('// A citation drawn'));
const timeline=raw.slice(raw.indexOf('let TW = [];'),raw.indexOf('// A camera looks at a world group'));
fs.writeFileSync(path.join(OUT,'papermorph-core-executed.js'),drawing+'\n'+timeline);
const ctx=vm.createContext({console,Math,JSON,Number,String,Array,Object,Date,Map,Set,Uint8Array,Infinity,document:{createElementNS:(ns,t)=>new El(t)},NS:'http://www.w3.org/2000/svg',UI:'Noto Sans CJK KR',COL:{chalk:'#ffffff',board:'#08141c'},P:{back:0},window:{}, PM_STYLES:{}});
ctx.window=ctx;
vm.runInContext(drawing+'\n'+timeline,ctx,{filename:'Papermorph-original-core.js'});
for(const f of ['vector_styles.js','image_styles.js']) if(fs.existsSync(path.join(ROOT,f)))vm.runInContext(fs.readFileSync(path.join(ROOT,f),'utf8'),ctx,{filename:f});
if(!ctx.PM_STYLES[STYLE])throw new Error('Unknown style '+STYLE);

const segments=JSON.parse(fs.readFileSync(path.join(ROOT,'timing.json'),'utf8'));
const mode=process.env.PREVIEW==='1';
const selected=mode?segments.filter(x=>x.id===9):segments;
function caption(svg){const t=new El('text');t.attrs={x:450,y:1320,'text-anchor':'middle','font-size':44,'font-family':'Noto Sans CJK KR','font-weight':800,fill:'#fff',stroke:'#14202b','stroke-width':5,'stroke-linejoin':'round','paint-order':'stroke fill'};svg.appendChild(t);return t;}
async function main(){
 const output=path.join(OUT,mode?'sensor_test.mp4':'papermorph_tech_complete_v3.mp4');
 const duration=selected.reduce((a,s)=>a+s.duration,0),begin=mode?selected[0].start:0;
 const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-','-ss',String(begin),'-i',path.join(ROOT,'audio/narration.wav'),'-map','0:v','-map','1:a','-c:v','libx264','-preset','fast','-threads','2','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-t',String(duration),'-movflags','+faststart',output],{stdio:['pipe','inherit','inherit']});
 const done=new Promise((res,rej)=>ff.on('close',c=>c===0?res():rej(Error('ffmpeg '+c))));
 const cues=[];
 for(const seg of selected){
   vm.runInContext('TW=[]',ctx);
   const svg=new El('svg');svg.attrs={xmlns:'http://www.w3.org/2000/svg',width:WIDTH,height:HEIGHT,viewBox:'0 0 900 1600'};
   ctx.PM_STYLES.complete(svg,seg.id,seg.duration);const cap=caption(svg);
   const words=seg.text.split(' '), chunks=[];for(let j=0;j<words.length;j+=3)chunks.push(words.slice(j,j+3).join(' '));
   const total=chunks.reduce((a,v)=>a+v.length,0);let off=0;
   const caps=chunks.map(c=>{let a=off/total*seg.duration;off+=c.length;return {text:c,start:seg.start+a,end:seg.start+off/total*seg.duration};});cues.push(...caps);
   for(let f=0;f<Math.round(seg.duration*FPS);f++){
     const t=f/FPS;ctx.evalTo(t);cap.textContent=(caps.find(c=>t+seg.start<c.end)||caps.at(-1)).text;
     const str=svg.serialize(),buf=await sharp(Buffer.from(str)).jpeg({quality:92,chromaSubsampling:'4:4:4'}).toBuffer();
     if([0,Math.round(seg.duration*FPS*.48),Math.round(seg.duration*FPS)-1].includes(f))fs.writeFileSync(path.join(REVIEW,`scene_${seg.id}_${f}.jpg`),buf);
     if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
   }
   console.log('rendered',seg.id,seg.text);
 }
 ff.stdin.end();await done;
 fs.writeFileSync(path.join(OUT,mode?'preview_cues.json':'captions.json'),JSON.stringify(cues,null,2));
 console.log(output);
}
main().catch(e=>{console.error(e);process.exit(1)});
