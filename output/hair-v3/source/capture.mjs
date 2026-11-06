import fs from 'node:fs';import http from 'node:http';import path from 'node:path';
import {chromium} from 'playwright';
const root=path.dirname(new URL(import.meta.url).pathname);const port=8769;
const server=http.createServer((req,res)=>{let p=path.join(root,decodeURIComponent(req.url.split('?')[0]));if(req.url==='/')p=path.join(root,'index.html');try{const b=fs.readFileSync(p);res.setHeader('Content-Type',p.endsWith('.js')?'text/javascript':p.endsWith('.json')?'application/json':p.endsWith('.html')?'text/html':'application/octet-stream');res.end(b);}catch{res.statusCode=404;res.end('404');}}).listen(port,'127.0.0.1');
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const page=await browser.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});page.on('pageerror',e=>console.log('PAGE ERROR',String(e)));await page.goto(`http://127.0.0.1:${port}`);await page.waitForFunction(()=>window.ready,{timeout:60000});
const args=process.argv.slice(2);
if(args[0]==='proof'){
 fs.mkdirSync(root+'/proof-frames',{recursive:true});const modes=['wrap','slide','short','duo'];for(let f=0;f<192;f++){const k=Math.floor(f/48),t=(f%48)/24;const b=await page.evaluate(({t,mode})=>{window.renderAt(t,{mode,start:0,end:2});return window.captureJPEG();},{t,mode:modes[k]});fs.writeFileSync(`${root}/proof-frames/${String(f).padStart(5,'0')}.jpg`,Buffer.from(b,'base64'));if(f%48===0)console.log('proof',modes[k],Date.now());}
}else if(args[0]==='still'){
 for(const mode of ['flip','reveal','wrap','short','center','cap','duo','snip']){await page.evaluate(({mode})=>window.renderAt(.7,{mode,start:0,end:1}),{mode});await page.screenshot({path:`${root}/test_${mode}.png`});console.log(mode,Date.now());}
}else{
 const timeline=JSON.parse(fs.readFileSync(root+'/timeline.json','utf8'));const fps=24,end=timeline.at(-1).end;fs.mkdirSync(root+'/frames',{recursive:true});const patch=args[0]==='patch';const start=patch?0:Number(args[0]||0),stop=Math.min(Number(args[1]||end),end);let t0=Date.now();
 for(let f=Math.round(start*fps);f<Math.round(stop*fps);f++){if(patch){const shot=timeline.find(s=>s.start<=f/fps&&f/fps<s.end);if(!shot||!['cap','slide','motor','overview'].includes(shot.mode))continue;}const b=await page.evaluate(t=>{window.renderAt(t);return window.captureJPEG();},f/fps);fs.writeFileSync(`${root}/frames/${String(f).padStart(5,'0')}.jpg`,Buffer.from(b,'base64'));if(f%24===0)console.log(f,'/',Math.round(end*fps),'elapsed',(Date.now()-t0)/1000);}
}
await browser.close();server.close();
