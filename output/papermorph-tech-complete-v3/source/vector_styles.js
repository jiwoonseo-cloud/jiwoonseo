/* Papermorph vector studies. Deterministic SVG; no external assets or timers. */
(function () {
  'use strict';
  window.PM_STYLES = window.PM_STYLES || {};
  const W=900,H=1600,TAU=Math.PI*2;
  let serial=0;
  const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
  const smooth=v=>{v=clamp(v);return v*v*(3-2*v);};
  const lerp=(a,b,t)=>a+(b-a)*t;
  const phase=(q,a,b)=>clamp((q-a)/(b-a));
  const wave=(q,a,b)=>Math.sin(Math.PI*phase(q,a,b));
  const seed=n=>{const x=Math.sin(n*12.9898+78.233)*43758.5453;return x-Math.floor(x);};
  const PAPER_SHADOW='__paper_cutout_shadow__';
  const E=(tag,a,p)=>{
    if(a && a.filter===PAPER_SHADOW){
      // Crisp offset silhouettes preserve cut-paper depth without costly blur passes.
      a={...a};delete a.filter;
      mk(tag,{...a,fill:'#6f563c',stroke:'none',opacity:.14*(a.opacity===undefined?1:Number(a.opacity)),transform:`translate(0 7) ${a.transform||''}`},p);
    }
    return mk(tag,a||{},p);
  };
  const group=(p,a)=>E('g',a,p);
  const R=(p,x,y,w,h,fill,rx=0,more={})=>E('rect',{x,y,width:w,height:h,rx,fill,...more},p);
  const C=(p,x,y,r,fill,more={})=>E('circle',{cx:x,cy:y,r,fill,...more},p);
  const O=(p,x,y,rx,ry,fill,more={})=>E('ellipse',{cx:x,cy:y,rx,ry,fill,...more},p);
  const L=(p,x1,y1,x2,y2,stroke,width=2,more={})=>E('line',{x1,y1,x2,y2,stroke,'stroke-width':width,...more},p);
  const P=(p,d,fill='none',stroke='none',sw=1,more={})=>E('path',{d,fill,stroke,'stroke-width':sw,'stroke-linecap':'round','stroke-linejoin':'round',...more},p);
  const POLY=(p,points,fill,more={})=>E('polygon',{points,fill,...more},p);
  const TX=(p,txt,x,y,size,color,more={})=>{const e=E('text',{x,y,fill:color,'font-size':size,'font-family':'Noto Sans CJK KR, sans-serif','font-weight':500,...more},p);e.textContent=txt;return e;};
  const set=(e,a)=>{Object.entries(a).forEach(([k,v])=>e.setAttribute(k,v));};
  const tr=(e,x=0,y=0,s=1,r=0)=>set(e,{transform:`translate(${x} ${y}) scale(${s}) rotate(${r})`});
  const fade=(e,v)=>set(e,{opacity:clamp(v)});
  const tick=(fn,D)=>{fn(0);prog(fn,0,D,q=>q);};
  const uid=k=>'pmv_'+k+'_'+(++serial);
  const dash=(p,x1,y1,x2,y2,c,w=2)=>L(p,x1,y1,x2,y2,c,w,{'stroke-dasharray':'7 10'});
  const arrow=(p,x,y,a,c,s=1)=>P(p,'M -10 -8 L 0 0 L -10 8','none',c,3,{transform:`translate(${x} ${y}) rotate(${a}) scale(${s})`});
  function defs(p,kind){
    const d=E('defs',{},p),id=uid(kind),grain=id+'_grain',shadow=id+'_shadow',glow=id+'_glow';
    const pat=E('pattern',{id:grain,width:80,height:80,patternUnits:'userSpaceOnUse'},d);
    if(kind==='line'){
      for(let i=-80;i<160;i+=10)L(pat,i,0,i+80,80,'#33464b',.65,{opacity:.23});
    }else{
      for(let i=0;i<26;i++)C(pat,seed(i+4)*80,seed(i+88)*80,.4+seed(i+15)*.65,kind==='paper'?'#6e4931':'#a8b5ae',{opacity:.22});
    }
    if(kind==='paper')return {grain:`url(#${grain})`,shadow:PAPER_SHADOW,glow:'none',d};
    const f=E('filter',{id:shadow,x:'-30%',y:'-30%',width:'170%',height:'180%'},d);
    E('feDropShadow',{dx:0,dy:kind==='paper'?8:5,stdDeviation:kind==='paper'?5:7,'flood-color':'#172c34','flood-opacity':kind==='paper'?.15:.3},f);
    const gl=E('filter',{id:glow,x:'-100%',y:'-100%',width:'300%',height:'300%'},d);
    E('feGaussianBlur',{stdDeviation:8},gl);
    return {grain:`url(#${grain})`,shadow:`url(#${shadow})`,glow:`url(#${glow})`,d};
  }
  function label(p,txt,x,y,c='#c5e7e8',size=22){return TX(p,txt,x,y,size,c,{'font-family':'Noto Sans Mono CJK KR, monospace','letter-spacing':2});}
  function stage(p,bg){R(p,0,0,W,H,bg);return group(p);}
  function techHeader(p,index){
    label(p,'입자와 빛 · 설명용 도해',62,132,'#83b8c1',18);
    L(p,62,157,838,157,'#35545f',1);
    label(p,['01   실내에서 흡입구로','02   센서 안쪽의 빛','03   산란광이 신호로'][index],62,213,'#e4f2ee',29);
    label(p,'—',805,212,'#f6cb65',30);
  }
  function techRoom(p){
    const pal={edge:'#6e9ba5',fill:'#17323d',dark:'#0a202b'};
    for(let i=0;i<17;i++)L(p,64+i*49,330,64+i*49,1190,'#27434d',.8,{opacity:.55});
    for(let y=350;y<1230;y+=48)L(p,60,y,840,y,'#27434d',.8,{opacity:.55});
    P(p,'M 66 1030 L 335 837 L 835 837 M 335 837 L 335 332','none','#42606b',2);
    POLY(p,'66,1030 335,837 835,837 835,1190 66,1190','#142d38',{opacity:.65});
    R(p,106,400,207,239,'#14323d',5,{stroke:'#688c94','stroke-width':2});
    L(p,209,400,209,639,'#688c94');L(p,106,518,313,518,'#688c94');
    POLY(p,'121,612 160,563 208,599 249,536 299,612','#34545d');
    C(p,270,445,24,'#92b2b0',{opacity:.24});
    R(p,365,648,323,172,'#23404b',26,{stroke:'#5f7f88','stroke-width':2});
    R(p,384,679,133,100,'#30505b',15,{stroke:'#557883'});R(p,529,679,133,100,'#30505b',15,{stroke:'#557883'});
    R(p,348,746,350,120,'#1c3844',20,{stroke:'#5f7f88','stroke-width':2});R(p,332,717,53,154,'#33525c',16);R(p,666,717,53,154,'#33525c',16);
    L(p,373,867,366,915,'#9ab6b8',8);L(p,676,867,684,915,'#9ab6b8',8);
    for(let i=0;i<8;i++)L(p,402+i*35,891,403+i*35,903,'#33525c',1);
    P(p,'M 727 653 L 727 432 M 681 432 L 777 432 L 755 364 L 703 364 Z','none','#668e98',3);
    O(p,730,912,80,17,'#071a24',{opacity:.45});
    const purifier=group(p);
    P(p,'M 660 711 Q 660 682 690 677 L 784 677 Q 815 682 815 711 L 815 1048 Q 810 1080 782 1085 L 691 1085 Q 660 1079 660 1050 Z','#20404c','#a0c1c6',2);
    O(p,738,698,72,19,'#466974',{stroke:'#a0c1c6','stroke-width':2});
    O(p,738,699,49,10,'#112a36');
    R(p,676,758,123,219,'#071b27',14,{stroke:'#6c939c','stroke-width':1.5});
    for(let i=0;i<10;i++)R(p,686+i*10,771,4,191,'#446772',2);
    C(p,738,1015,6,'#8be7d4');
    label(p,'흡입구',672,1140,'#b9e0e4',23);
    P(p,'M 722 1110 L 722 1067','none','#b9e0e4',1);arrow(p,722,1067,-90,'#b9e0e4',.6);
    O(p,225,1061,129,22,'#071a24',{opacity:.5});
    R(p,118,944,219,25,'#4d625f',8);L(p,141,969,131,1142,'#7f9b98',9);L(p,312,969,323,1142,'#7f9b98',9);
    const humid=group(p);P(humid,'M 160 834 Q 161 786 220 776 Q 279 786 280 834 L 280 936 L 160 936 Z','#325b69','#b1d6db',2);
    O(humid,220,835,60,18,'#436d78',{stroke:'#b1d6db','stroke-width':2});R(humid,160,873,120,62,'#b9e1df',0,{opacity:.17});
    O(humid,220,936,60,16,'#294956',{stroke:'#b1d6db','stroke-width':2});O(humid,220,792,17,6,'#091e28');
    R(humid,205,899,30,6,'#a7ece6',3);
    label(p,'미스트',145,1190,'#b9e0e4',23);
    return {inlet:[738,865],outlet:[220,792]};
  }
  function techSensor(p,D,scene){
    const d=defs(p,'tech'),body=group(p);
    P(body,'M 85 461 L 230 381 L 685 381 L 818 460 L 818 1093 L 680 1169 L 223 1169 L 85 1093 Z','#173541','#577986',2);
    P(body,'M 116 492 L 249 418 L 666 418 L 785 492 L 785 1067 L 665 1130 L 250 1130 L 116 1067 Z','#0b202c','#38535f',2);
    P(body,'M 116 492 L 785 492 M 116 1067 L 785 1067','none','#294956',2);
    for(let i=0;i<7;i++){L(body,131+i*20,484,210+i*20,440,'#577986',1);L(body,663+i*16,1098,706+i*16,1074,'#577986',1);}
    C(body,129,459,8,'#0c202a',{stroke:'#8cabaf','stroke-width':2});C(body,776,459,8,'#0c202a',{stroke:'#8cabaf','stroke-width':2});
    C(body,130,1081,8,'#0c202a',{stroke:'#8cabaf','stroke-width':2});C(body,776,1081,8,'#0c202a',{stroke:'#8cabaf','stroke-width':2});
    const flow=group(body,{opacity:.35});
    for(let i=0;i<3;i++){dash(flow,385+i*42,452,385+i*42,1090,'#7bbfcb',2);arrow(flow,385+i*42,1055,90,'#7bbfcb',1);}
    R(body,119,662,139,139,'#27434e',12,{stroke:'#9cbbb8','stroke-width':2});R(body,138,684,80,93,'#142d37',5);
    for(let i=0;i<5;i++)L(body,147+i*15,695,147+i*15,765,'#5d8d92',3);
    P(body,'M 218 687 L 251 701 L 251 760 L 218 775 Z','#c9aa5e','#f8d47a',2);R(body,251,707,11,47,'#ffe4a1',3);
    label(body,'광원',120,620,'#e4eacb',23);L(body,194,634,194,660,'#aec7c7',1);
    R(body,724,671,36,120,'#233b44',5,{stroke:'#71929a'});L(body,733,682,752,701,'#749098');L(body,733,708,752,727,'#749098');L(body,733,734,752,753,'#749098');L(body,733,760,752,779,'#749098');
    const beam=group(body);
    R(beam,264,721,462,18,'#f8d274',0,{opacity:.07,filter:d.glow});
    L(beam,264,730,725,730,'#f8d274',5);L(beam,264,730,725,730,'#fff3bd',1.5);
    arrow(beam,697,730,0,'#f8d274',1.2);
    label(body,'직진하는 빛',387,689,'#edcb83',20);
    R(body,592,945,120,83,'#315763',7,{stroke:'#a0c6c8','stroke-width':2});R(body,584,928,136,20,'#9ccdd0',4);R(body,603,931,97,9,'#c5efeb',3);
    for(let i=0;i<5;i++)L(body,607+i*22,1030,607+i*22,1055,'#8ba7aa',3);
    label(body,'측면',620,839,'#b9dddf',22);label(body,'수광부',620,870,'#b9dddf',22);L(body,680,882,680,926,'#b9dddf');
    const resp=group(body,{opacity:0});R(resp,582,921,140,113,'#89ece1',15,{opacity:.14,filter:d.glow});R(resp,603,931,97,9,'#ddffbd',3);
    const scatter=group(body,{opacity:0});
    for(let i=-2;i<=2;i++)L(scatter,430,730,650+i*12,930,'#f9d36c',i===0?3:1.2,{opacity:i===0?1:.35});
    const photon=C(scatter,430,730,7,'#fff3b4',{filter:d.glow});const photonCore=C(scatter,430,730,4,'#fff9da');
    const droplet=group(body,{opacity:0});P(droplet,'M 0 -29 C -11 -13 -24 -2 -24 13 A 24 24 0 0 0 24 13 C 24 -2 11 -13 0 -29 Z','#78d7e1','#b7ffff',2);P(droplet,'M -10 2 Q -16 18 -5 24','none','#e0ffff',3);
    const ring=C(body,430,730,46,'none',{stroke:'#facd67','stroke-width':2,opacity:0});
    const signal=group(p);label(signal,'센서 신호',95,1230,'#a2c4cd',19);L(signal,318,1224,803,1224,'#45616d',1);
    const trace=P(signal,'M 318 1224 L 803 1224','none','#8ae4d7',4);
    const dots=[];for(let i=0;i<5;i++)dots.push(C(body,400+(i%3)*32,500+i*95,3,'#6db3c4',{opacity:.5}));
    tick(q=>{
      dots.forEach((e,i)=>set(e,{cy:500+((q*500+i*95)%530)}));
      fade(beam,scene===1?smooth(phase(q,.12,.3)):1);
      if(scene===1){
        let s=1;set(body,{transform:`translate(${450-450*s} ${780-780*s}) scale(${s})`});
        fade(body,smooth(phase(q,0,.13)));fade(signal,smooth(phase(q,.65,.85))*.7);
      } else {
        let y=q<.38?lerp(490,730,smooth(phase(q,.08,.38))):q<.59?730:lerp(730,1150,smooth(phase(q,.59,.91)));
        tr(droplet,430,y);fade(droplet,smooth(phase(q,.04,.1))*(1-smooth(phase(q,.88,.98))));
        const a=smooth(phase(q,.39,.43))*(1-smooth(phase(q,.57,.65)));fade(scatter,a);
        const t=phase(q,.42,.51);set(photon,{cx:lerp(430,650,t),cy:lerp(730,930,t)});set(photonCore,{cx:lerp(430,650,t),cy:lerp(730,930,t)});
        fade(resp,smooth(phase(q,.49,.55))*(.75+.25*Math.sin(q*28)));set(ring,{r:28+phase(q,.39,.56)*55,opacity:wave(q,.39,.57)*.7});
        const pts=[];for(let j=0;j<=100;j++){let x=318+j*4.85;let a=clamp((q-.55)*2.7);let val=j<100*a?((j>13&&j<25)?-55*Math.sin((j-13)/12*Math.PI):(j>34&&j<52)?-24*Math.sin((j-34)/18*Math.PI):Math.sin(j*2.5)*1.8):0;pts.push(`${x},${1224+val}`);}set(trace,{d:'M '+pts.join(' L ')});
      }
    },D);
    if(scene===2)comparison(p,D,'tech');
    return body;
  }
  window.PM_STYLES.tech=function(parent,i,D){
    const root=stage(parent,'#0b202b');techHeader(root,i);
    if(i===0){const cam=group(root);techRoom(cam);const flow=group(cam);
      for(let j=0;j<4;j++)P(flow,`M ${215+j*4} 784 C ${185+j*21} ${650-j*22} ${446+j*22} ${619+j*28} 681 ${811+j*25}`,'none','#71d1d3',1.6,{opacity:.25});
      const ds=[];for(let j=0;j<38;j++)ds.push(C(flow,220,780,2.5+seed(j)*4,'#abedf0'));
      const ring=C(cam,738,865,89,'none',{stroke:'#f4d47a','stroke-width':2,'stroke-dasharray':'12 10',opacity:0});
      const tag=group(root);label(tag,'물방울',86,290,'#93d4dc',20);P(tag,'M 280 302 L 280 344 L 345 344','none','#6f9ba6',1.5);
      tick(q=>{ds.forEach((e,j)=>{let t=(q*.95+j/38)%1;let xx=lerp(220,687,t);let yy=792-198*Math.sin(t*Math.PI)+t*67+(seed(j+57)-.5)*58*Math.sin(t*Math.PI);set(e,{cx:xx,cy:yy,opacity:.25+.65*Math.sin(t*Math.PI)});});let z=0;set(cam,{transform:'translate(0 0) scale(1)'});fade(tag,1);set(ring,{opacity:wave(q,.57,.92),r:89+6*Math.sin(q*25)});},D);
    } else {techSensor(root,D,i);if(i===1)inletBridge(root,D,'tech');}
  };

  /* Pixel: hand-built sprites, isometric floor and a square-grid optical chamber. */
  const px=(p,x,y,w,h,c,more={})=>R(p,Math.round(x/4)*4,Math.round(y/4)*4,w,h,c,0,more);
  function pixelFont(p,txt,x,y,size,c){return TX(p,txt,x,y,size,c,{'font-family':'Noto Sans Mono CJK KR, monospace','font-weight':700,'letter-spacing':2});}
  function pixelHeader(p,i){
    px(p,56,94,36,36,'#2b4b58');px(p,64,102,20,20,'#f6bd61');
    pixelFont(p,['거실','흡입구 안으로','빛이 신호가 되기까지'][i],112,124,28,'#244855');
    for(let j=0;j<3;j++){px(p,744+j*32,98,20,20,j===i?'#e57b59':'#b1c7bb');}
    px(p,56,150,788,4,'#a5bdb1');
  }
  function pixelRoom(p){
    const c={wall:'#dde7c8',wall2:'#b4c8ad',wood:'#c48661',dark:'#355665',deep:'#244550',blue:'#719a9c',cream:'#fff1cd',orange:'#df875f',brown:'#805c4b'};
    POLY(p,'60,460 449,300 839,460 839,1070 450,1230 60,1070',c.wall);
    POLY(p,'449,300 839,460 839,1010 449,854',c.wall2);
    POLY(p,'60,460 449,614 839,460 839,1010 450,1170 60,1010','#d9b997');
    for(let k=0;k<8;k++){L(p,60,640+k*48,450,795+k*48,'#ba9879',3);L(p,450,795+k*48,839,640+k*48,'#ba9879',3);}
    px(p,100,446,224,204,c.dark);px(p,112,458,200,180,'#e8f3dd');px(p,124,470,176,156,'#9ecac0');
    px(p,124,554,32,72,'#609b97');px(p,156,526,32,100,'#70a79e');px(p,188,570,48,56,'#669992');px(p,260,546,40,80,'#7dab9d');
    px(p,204,458,12,180,c.cream);px(p,112,540,200,12,c.cream);px(p,100,642,236,12,c.brown);
    px(p,540,456,148,108,'#577b77');px(p,552,468,124,84,'#f0d697');px(p,576,504,52,36,'#e2a45e');px(p,608,492,44,48,'#81a590');
    // Sofa sprite: stepped arms, individual cushions, legs, piping.
    px(p,386,682,280,108,c.orange);px(p,374,698,304,88,c.orange);px(p,390,698,120,72,'#efab78');px(p,522,698,128,72,'#edac7d');
    px(p,370,764,312,60,'#ba6c50');px(p,358,736,40,112,'#d9845e');px(p,652,736,40,112,'#d9845e');px(p,390,784,256,40,'#df8b61');
    px(p,378,848,20,40,c.brown);px(p,652,848,20,40,c.brown);px(p,414,708,56,48,'#ffe0a2');px(p,578,716,48,48,'#638b8c');px(p,590,728,24,24,'#83b0a7');
    // Pixel lamp, shelf, stack of books.
    px(p,752,540,12,280,c.brown);px(p,708,512,100,40,'#f2cb86');px(p,724,488,68,24,'#f8d895');px(p,712,820,92,16,c.brown);
    px(p,466,596,120,12,c.brown);px(p,478,560,20,36,'#7f9e8e');px(p,502,548,16,48,'#c4855f');px(p,522,556,20,40,'#f2cd84');
    // Woven stepped rug.
    POLY(p,'195,976 478,864 758,976 478,1088','#729792');
    POLY(p,'231,976 478,880 722,976 478,1072','#e7d9a9');
    POLY(p,'279,976 478,900 674,976 478,1052','#80a49c');
    for(let j=0;j<8;j++)px(p,335+j*28,940+(j%2)*24,16,16,'#e1d69f');
    // Humidifier table / actual sprite silhouette.
    px(p,122,920,188,24,c.brown);px(p,136,944,16,112,c.brown);px(p,278,944,16,112,c.brown);px(p,154,812,120,108,c.cream);px(p,166,788,96,24,c.cream);px(p,182,776,64,12,c.cream);
    px(p,166,848,96,48,'#a9cfce');px(p,166,848,12,48,'#d7ece0');px(p,194,764,40,12,c.dark);px(p,174,900,80,12,'#d7d7ba');px(p,212,904,8,8,'#73aeb2');
    // Purifier on orange feet, subtly isometric right-hand face.
    px(p,676,828,128,260,'#f9eac3');px(p,688,812,104,16,'#fff3d3');px(p,804,840,20,236,'#c5cdb0');px(p,688,1088,28,24,c.orange);px(p,768,1088,28,24,c.orange);
    px(p,688,860,104,164,c.deep);for(let j=0;j<6;j++)px(p,696+j*16,868,8,148,c.blue);px(p,704,836,72,8,c.dark);px(p,736,1052,12,12,'#71ac95');
    // Leaf-by-leaf plant rather than a generic symbol.
    px(p,92,738,12,116,c.brown);px(p,68,838,64,16,'#bd7959');px(p,76,854,48,48,'#d28d61');
    [[68,720],[100,690],[112,750],[56,770],[100,796]].forEach(([x,y],j)=>{px(p,x,y,36,24,j%2?'#4b7c74':'#678c71');px(p,x+8,y-8,24,40,j%2?'#4b7c74':'#678c71');});
    return {outlet:[214,764],inlet:[740,944]};
  }
  function pixelSensor(p,D,scene){
    const bg=group(p);px(bg,56,318,788,872,'#234c58');px(bg,72,334,756,840,'#3e6d73');px(bg,96,358,708,792,'#1e414d');
    // Tiled machinery housing and roof vents.
    for(let x=112;x<796;x+=48){px(bg,x,374,32,16,'#5c8b89');px(bg,x,1118,32,16,'#5c8b89');}
    for(let y=414;y<1090;y+=48){px(bg,112,y,16,28,'#527d7d');px(bg,772,y,16,28,'#527d7d');}
    for(let x=164;x<758;x+=40)for(let y=414;y<1104;y+=40)px(bg,x,y,4,4,'#315c66');
    px(bg,348,358,176,28,'#183642');for(let x=360;x<518;x+=24)px(bg,x,358,12,28,'#a6c3b4');
    pixelFont(p,'광학식 센서 내부',92,279,30,'#244855');
    pixelFont(bg,'광원',144,600,23,'#f2d8a0');
    px(bg,136,642,104,148,'#c98b63');px(bg,148,654,80,124,'#edb97d');px(bg,160,670,52,92,'#c7865c');px(bg,228,678,24,76,'#efcc73');px(bg,252,694,20,44,'#ffe9a1');
    for(let y=660;y<786;y+=24)px(bg,128,y,12,12,'#976f54');
    const beam=group(bg);px(beam,272,710,476,12,'#d8ad55');px(beam,272,714,476,4,'#fff2a6');for(let x=300;x<740;x+=96){px(beam,x,702,8,8,'#edc66b');px(beam,x+8,710,8,12,'#edc66b');px(beam,x,722,8,8,'#edc66b');}
    px(bg,748,658,20,112,'#658f8a');px(bg,740,670,8,88,'#9cb7a4');
    px(bg,576,960,136,100,'#ca7759');px(bg,564,948,160,24,'#e6a579');px(bg,584,932,120,16,'#b3d3bd');px(bg,600,928,88,8,'#def0d0');
    for(let x=584;x<712;x+=28)px(bg,x,1060,12,32,'#dbba7e');
    pixelFont(bg,'측면',612,836,23,'#cee3ca');pixelFont(bg,'수광부',612,868,23,'#cee3ca');
    const drop=group(bg);px(drop,-8,-24,16,8,'#a0e3db');px(drop,-16,-16,32,8,'#a0e3db');px(drop,-24,-8,48,32,'#74c6d0');px(drop,-16,24,32,8,'#74c6d0');px(drop,-16,-8,8,16,'#def9d9');
    const scatter=group(bg,{opacity:0});
    const blocks=[];for(let j=0;j<14;j++){let t=j/13;blocks.push(px(scatter,432+208*t,716+212*t,8,8,'#ffe994'));}
    const spark=group(bg,{opacity:0});for(let j=0;j<8;j++){let a=j*TAU/8;px(spark,432+Math.cos(a)*44,716+Math.sin(a)*44,8,8,'#fff2b0');}
    const resp=group(bg,{opacity:0});px(resp,588,932,112,8,'#fff4a5');px(resp,576,972,136,76,'#fadf86',{opacity:.2});
    const signal=group(p);pixelFont(signal,'신호',92,1240,24,'#355866');px(signal,250,1208,550,40,'#bad0ba');
    const bars=[];for(let j=0;j<22;j++)bars.push(px(signal,264+j*24,1232,16,8,'#4b897f'));
    const falling=[];for(let j=0;j<7;j++)falling.push(px(bg,368+(j%3)*44,412+j*52,8,8,'#75aaa8',{opacity:.45}));
    tick(q=>{
      falling.forEach((e,j)=>set(e,{y:Math.round((404+(q*420+j*71)%660)/8)*8}));
      if(scene===1){const z=1-smooth(phase(q,0,.2));tr(bg,0,z*100);fade(bg,1-z);fade(beam,smooth(phase(q,.2,.38)));fade(drop,0);fade(signal,smooth(phase(q,.7,.9))*.65);}
      else {
        let y=q<.37?lerp(480,716,phase(q,.06,.37)):q<.6?716:lerp(716,1140,phase(q,.6,.94));tr(drop,432,Math.round(y/8)*8);fade(drop,1-smooth(phase(q,.9,.99)));
        let sp=smooth(phase(q,.39,.43))*(1-smooth(phase(q,.58,.65)));fade(scatter,sp);blocks.forEach((e,j)=>fade(e,q>(.41+j*.006)?1:0));fade(spark,wave(q,.38,.6));fade(resp,smooth(phase(q,.49,.55))*(.7+.3*(Math.floor(q*22)%2)));
        bars.forEach((e,j)=>{let h=q>.57+j*.014?[12,24,48,72,96,64,40,24,16,16,24,32,48,40,24,16,12,8,8,8,8,8][j]:8;set(e,{height:h,y:1240-h});});
      }
    },D);if(scene===2)comparison(p,D,'pixel');return bg;
  }
  window.PM_STYLES.pixel=function(parent,i,D){
    const root=stage(parent,'#f0edcf');set(root,{'shape-rendering':'crispEdges'});pixelHeader(root,i);
    if(i===0){const cam=group(root);pixelRoom(cam);const steam=[];for(let j=0;j<28;j++)steam.push(px(cam,214,740,j%3?8:12,j%3?8:12,j%3?'#a5d5d2':'#e9fff2'));
      pixelFont(root,'미스트',104,1192,23,'#355765');pixelFont(root,'흡입구',676,1192,23,'#355765');
      tick(q=>{steam.forEach((e,j)=>{let t=(q*.84+j/28)%1;set(e,{x:Math.round(lerp(214,740,t)/8)*8,y:Math.round((764-232*Math.sin(t*Math.PI)+t*180+(seed(j)-.5)*52)/8)*8,opacity:.35+.65*Math.sin(Math.PI*t)});});let z=Math.floor(smooth(phase(q,.77,1))*10)/10;let s=1+z*2.5;set(cam,{transform:`translate(${(450-740*s)*z} ${(780-944*s)*z}) scale(${s})`});},D);
    }else {pixelSensor(root,D,i);if(i===1)inletBridge(root,D,'pixel');}
  };

  /* Cut-paper theatre: shaped silhouettes, offset layers, grain and folding leaves. */
  const paper={bg:'#f1e7d6',ink:'#3c594f',cream:'#fff8e6',leaf:'#6f9273',mint:'#a8c4a6',red:'#c96f50',peach:'#e7ac80',gold:'#e3bc67',navy:'#3c6470'};
  function paperShape(p,d,c,shadow,stroke='none'){return P(p,d,c,stroke,1,shadow?{filter:shadow}:{});}
  function paperHeader(p,i){
    TX(p,['공기가 움직이는 방','흡입구 안의 작은 세계','빛이 흩어지면, 신호가'][i],65,145,40,paper.ink,{'font-family':'Noto Serif CJK KR, serif','font-style':'italic'});
    L(p,65,178,835,178,'#bfbea3',1.5);TX(p,['I','II','III'][i],806,139,26,paper.red,{'font-family':'Noto Serif CJK KR, serif'});
  }
  function paperRoom(p,d){
    paperShape(p,'M 49 556 Q 56 474 119 444 L 715 320 Q 821 300 851 395 L 851 1090 Q 820 1144 729 1135 L 93 1164 Q 47 1153 49 1080 Z','#e3d4b7',d.shadow);
    paperShape(p,'M 59 891 Q 285 824 481 862 Q 670 904 849 831 L 849 1106 Q 577 1184 68 1140 Z','#c1c6a2',null);
    // Arched window, separate curved frame and three landscape layers.
    P(p,'M 111 732 L 111 477 A 127 127 0 0 1 254 352 A 127 127 0 0 1 365 477 L 365 732 Z','#fff5da','none',1,{filter:d.shadow});
    P(p,'M 129 713 L 129 481 A 109 109 0 0 1 238 372 A 109 109 0 0 1 347 481 L 347 713 Z','#b7cfb2');
    C(p,267,439,42,'#efcc78');P(p,'M 129 627 Q 218 499 347 594 L 347 713 L 129 713 Z','#96b79b');P(p,'M 129 660 Q 269 570 347 650 L 347 713 L 129 713 Z','#719b85');
    R(p,232,373,11,342,'#fff5da');R(p,129,538,218,10,'#fff5da');
    P(p,'M 94 737 L 380 737 L 370 753 L 102 753 Z','#d5b891');
    // Paper framed abstract print.
    P(p,'M 540 433 L 703 416 L 720 589 L 554 608 Z','#fff5de','none',1,{filter:d.shadow});P(p,'M 557 448 L 689 434 L 702 574 L 570 589 Z','#e2c28c');C(p,627,490,34,'#b76d4c');P(p,'M 571 567 Q 622 493 696 552 L 702 575 L 573 587 Z','#8eaa86');
    // Full cut-out couch with soft asymmetry and separate folded cushions.
    paperShape(p,'M 358 705 Q 356 675 395 669 L 661 646 Q 693 643 699 679 L 710 845 L 357 861 Z','#b56d4c',d.shadow);
    paperShape(p,'M 379 702 Q 431 689 505 689 L 509 794 L 379 803 Z','#dc9268',d.shadow);
    paperShape(p,'M 517 687 Q 584 670 674 674 L 683 783 L 519 795 Z','#d58b62',d.shadow);
    paperShape(p,'M 348 786 Q 348 766 367 762 L 390 761 L 397 861 L 690 850 L 684 752 Q 723 736 733 769 L 745 865 Q 742 886 717 893 L 368 912 Q 343 906 343 884 Z','#d3845a',d.shadow);
    P(p,'M 397 815 Q 532 799 690 802 L 691 850 L 397 862 Z','#e2a173');
    L(p,374,907,367,946,'#795b45',13);L(p,716,894,723,931,'#795b45',13);
    paperShape(p,'M 415 727 L 480 716 L 489 782 L 422 794 Z','#e8c47d',d.shadow);P(p,'M 429 742 L 470 735 L 476 773 L 435 779 Z','none','#c99f5f',2);
    paperShape(p,'M 589 701 L 649 705 L 648 768 L 582 765 Z','#789e8b',d.shadow);
    // Irregular woven rug, decorative cutouts.
    paperShape(p,'M 195 1027 Q 439 935 756 994 L 780 1089 Q 506 1174 173 1114 Z','#f4dfab',d.shadow);
    P(p,'M 222 1042 Q 456 970 736 1014 L 750 1070 Q 502 1136 209 1099 Z','none','#ce9263',7);
    for(let j=0;j<12;j++)P(p,`M ${203+j*47} ${1121-Math.sin(j/12*Math.PI)*13} l -4 18`,'none','#f1d8a0',4);
    // Tall leafy paper plant, each leaf individually cut.
    P(p,'M 797 862 Q 786 760 792 641','none','#567c65',7);
    [[792,694,-28],[790,749,32],[790,800,-38],[792,653,25]].forEach(([x,y,a],j)=>P(p,'M 0 0 Q -55 -60 -6 -91 Q 36 -46 0 0 Z',j%2?'#789c7b':'#5f856b','none',1,{transform:`translate(${x} ${y}) rotate(${a})`,filter:d.shadow}));
    P(p,'M 747 847 Q 790 832 829 847 L 817 925 Q 787 948 758 923 Z','#d6a371','none',1,{filter:d.shadow});O(p,788,846,40,10,'#aa7954');
    // Round timber table and domed humidifier.
    O(p,220,1010,121,21,'#a67c57',{filter:d.shadow});L(p,145,1016,132,1138,'#88694c',14);L(p,294,1016,311,1133,'#88694c',14);
    P(p,'M 161 963 L 155 878 Q 153 814 218 801 Q 279 804 282 868 L 283 967 Q 218 996 161 963 Z','#fff2d6','none',1,{filter:d.shadow});
    P(p,'M 159 900 Q 220 920 281 901 L 283 967 Q 218 990 162 965 Z','#adcfc3');P(p,'M 175 870 Q 170 837 199 824','none','#ffffff',6);
    O(p,218,809,20,7,'#476e6e');O(p,222,969,22,7,'#e9dec1');C(p,222,966,5,'#789f8a');
    // Sculpted air purifier, slanted body and slatted inlet.
    P(p,'M 650 858 Q 650 829 679 819 L 751 807 Q 789 806 799 836 L 817 1080 Q 810 1117 776 1125 L 691 1136 Q 663 1133 662 1109 Z','#f8e9c8','none',1,{filter:d.shadow});
    O(p,724,825,65,18,'#e3c99b',{transform:'rotate(-7 724 825)'});O(p,726,823,43,10,'#45666c',{transform:'rotate(-7 726 823)'});
    P(p,'M 678 889 L 781 875 L 793 1052 L 690 1069 Z','#577d7f');
    for(let j=0;j<9;j++)P(p,`M ${688+j*10} ${889-j*1.35} L ${699+j*10} ${1057-j*1.35}`,'none','#90aaa0',4);
    C(p,742,1093,7,'#c88656');
    R(p,49,310,803,882,d.grain,0,{opacity:.3,'pointer-events':'none'});
  }
  function paperSensor(p,D,scene){
    const d=defs(p,'paper'),world=group(p);
    paperShape(world,'M 70 421 Q 105 357 180 368 L 725 355 Q 815 359 839 434 L 835 1094 Q 825 1153 755 1165 L 153 1176 Q 72 1160 65 1097 Z','#7c9b8b',d.shadow);
    paperShape(world,'M 112 441 Q 111 406 155 409 L 742 397 Q 788 400 789 444 L 789 1081 Q 793 1124 743 1128 L 155 1141 Q 111 1134 108 1096 Z','#345d63',d.shadow);
    P(world,'M 127 1040 Q 296 998 431 1043 Q 606 1095 775 1047 L 776 1104 L 127 1120 Z','#477377');
    // A notched inlet channel at the top, with folded edges.
    P(world,'M 347 367 L 355 491 L 522 488 L 530 360 Z','#204951');P(world,'M 347 368 L 365 381 L 371 488 L 355 491 Z','#c0d0af');P(world,'M 510 374 L 530 360 L 522 488 L 506 487 Z','#9bb59a');
    TX(p,'흡입구를 지나 센서로',87,289,31,paper.ink,{'font-family':'Noto Serif CJK KR, serif'});
    // Folded lamp / emitter.
    P(world,'M 115 688 L 226 664 L 248 794 L 133 817 Z','#d39e60','none',1,{filter:d.shadow});
    P(world,'M 133 698 L 216 681 L 231 779 L 146 796 Z','#eac580');P(world,'M 215 682 L 247 705 L 259 763 L 231 779 Z','#bb864a');
    P(world,'M 247 705 Q 282 726 259 763 Z','#fff2af');
    TX(world,'광원',132,630,29,'#f5e9bc',{'font-family':'Noto Serif CJK KR, serif','font-style':'italic'});
    const beam=group(world);P(beam,'M 262 724 L 752 724 L 752 741 L 262 741 Z','#f8df8d','none',1,{opacity:.6});
    L(beam,266,732,754,732,'#fff2b2',3);P(beam,'M 734 719 L 752 732 L 734 745','none','#fff2b2',3);
    P(world,'M 752 695 L 778 691 L 780 773 L 755 773 Z','#96b3a0');
    // A collector cup is below the direct beam, its surface facing upward.
    paperShape(world,'M 583 968 L 713 953 L 705 1035 Q 653 1071 606 1049 Z','#d9906c',d.shadow);
    O(world,648,962,66,16,'#efc29b',{transform:'rotate(-6 648 962)'});O(world,648,959,46,10,'#b9d2b4',{transform:'rotate(-6 648 959)'});
    P(world,'M 610 1049 L 615 1080 M 638 1057 L 643 1088 M 666 1055 L 672 1084 M 692 1041 L 699 1072','none','#dbbb88',5);
    TX(world,'측면 수광부',602,851,25,'#e1e6c9',{'font-family':'Noto Serif CJK KR, serif','font-style':'italic'});P(world,'M 683 865 Q 684 902 664 940','none','#d5dec0',1.5);
    const drop=group(world);P(drop,'M 0 -34 Q -37 5 -25 24 Q 0 49 26 24 Q 38 7 0 -34 Z','#a9d5ce','none',1,{filter:d.shadow});P(drop,'M -7 -9 Q -22 12 -13 22','none','#e6f3da',5);
    const scatter=group(world,{opacity:0});P(scatter,'M 433 732 L 621 949 L 679 954 Z','#f7d87d','none',1,{opacity:.17});L(scatter,433,732,649,953,'#ffecaa',3);
    const light=group(scatter);P(light,'M 0 -10 L 4 -3 L 12 0 L 4 4 L 0 12 L -4 4 L -12 0 L -4 -3 Z','#fff2a9');
    const response=O(world,648,960,58,14,'#fff0a5',{opacity:0,transform:'rotate(-6 648 960)'});
    const sign=group(p);TX(sign,'센서 신호',84,1241,24,paper.ink,{'font-family':'Noto Serif CJK KR, serif','font-style':'italic'});P(sign,'M 286 1236 Q 498 1227 814 1237','none','#abc1a8',2);
    const trace=P(sign,'M 286 1236 L 814 1236','none','#c47d4f',4);
    R(world,65,350,774,830,d.grain,0,{opacity:.5});
    const left=group(p),right=group(p);
    P(left,'M 64 347 L 449 364 L 449 1173 L 67 1183 Z','#e6d4b3','none',1,{filter:d.shadow});P(right,'M 449 364 L 837 347 L 835 1183 L 449 1173 Z','#d7c49e','none',1,{filter:d.shadow});
    for(let j=0;j<11;j++){P(left,`M ${100+j*29} 399 L ${102+j*29} 1122`,'none','#829b8b',12);P(right,`M ${478+j*29} 399 L ${480+j*29} 1122`,'none','#6f8a7d',12);}
    tick(q=>{
      fade(beam,scene===1?smooth(phase(q,.2,.4)):1);
      if(scene===1){let t=smooth(phase(q,0,.27));set(left,{transform:`translate(${-390*t} 0) skewY(${-t*3})`});set(right,{transform:`translate(${390*t} 0) skewY(${t*3})`});fade(left,1-smooth(phase(q,.2,.3)));fade(right,1-smooth(phase(q,.2,.3)));fade(drop,0);fade(sign,smooth(phase(q,.68,.88))*.6);}
      else {fade(left,0);fade(right,0);let y=q<.37?lerp(495,732,smooth(phase(q,.06,.37))):q<.61?732:lerp(732,1170,smooth(phase(q,.61,.94)));tr(drop,433,y,1,Math.sin(q*8)*3);fade(drop,1-smooth(phase(q,.9,.99)));fade(scatter,smooth(phase(q,.39,.44))*(1-smooth(phase(q,.59,.68))));let t=phase(q,.43,.52);tr(light,lerp(433,648,t),lerp(732,955,t),1,45*t);fade(response,smooth(phase(q,.51,.57))*.9);
        const k=smooth(phase(q,.58,.86));set(trace,{d:`M 286 1236 L 369 1236 L 403 ${1236-66*k} L 430 ${1236+8*k} L 459 ${1236-31*k} L 489 1236 L 541 1236 L 575 ${1236-17*k} L 610 1236 L 814 1236`});}
    },D);
  }
  window.PM_STYLES.paper=function(parent,i,D){
    const root=stage(parent,paper.bg),d=defs(root,'paper');R(root,0,0,W,H,d.grain);paperHeader(root,i);
    if(i===0){const cam=group(root);paperRoom(cam,d);const mist=group(cam);const ds=[];for(let j=0;j<22;j++){let e=group(mist);P(e,'M 0 -9 Q -10 1 -6 8 Q 0 14 7 7 Q 10 1 0 -9 Z',j%2?'#c1dfd6':'#f6fae9','none',1,{filter:d.shadow});ds.push(e);}
      TX(root,'미스트',107,1238,29,paper.ink,{'font-family':'Noto Serif CJK KR, serif','font-style':'italic'});TX(root,'흡입구',705,1238,29,paper.ink,{'font-family':'Noto Serif CJK KR, serif','font-style':'italic'});
      tick(q=>{ds.forEach((e,j)=>{let t=(q*.8+j/22)%1;tr(e,lerp(218,733,t),810-222*Math.sin(t*Math.PI)+t*165+(seed(j)-.5)*35,1+seed(j)*.35,Math.sin(t*8+j)*15);fade(e,.2+.8*Math.sin(Math.PI*t));});let z=smooth(phase(q,.77,1));let s=lerp(1,2.1,z);set(cam,{transform:`translate(${(450-733*s)*z} ${(800-960*s)*z}) scale(${s})`});},D);
    }else {paperSensor(root,D,i);if(i===1)inletBridge(root,D,'paper');if(i===2)comparison(root,D,'paper');}
  };

  /* Engraved plate: contour hatching, stipple, long ink lines and an optical iris. */
  const ink='#314b50',faint='#90a09b',cream='#eee8d8',ochre='#b49347';
  function hatch(p,d,fill,defsObj,sw=2){P(p,d,fill,ink,sw);return P(p,d,defsObj.grain,'none',0);}
  function lineHeader(p,i){
    TX(p,'빛과 공기 관찰 · 설명용 도해',450,118,23,ink,{'text-anchor':'middle','font-family':'Noto Serif CJK KR, serif','letter-spacing':4});
    L(p,65,147,835,147,ink,1);L(p,65,153,835,153,ink,.6);
    TX(p,['I.  실내에서 움직이는 입자','II.  광학식 센서 안쪽','III.  흩어진 빛의 경로'][i],450,213,35,ink,{'text-anchor':'middle','font-family':'Noto Serif CJK KR, serif','font-style':'italic'});
  }
  function engravedRoom(p,d){
    P(p,'M 61 1019 L 359 837 L 835 837 M 359 837 L 359 321 M 61 1019 L 61 349 M 835 837 L 835 349','none',ink,2);
    for(let j=0;j<8;j++)L(p,77,1023+j*24,824,853+j*32,faint,.8);
    for(let j=0;j<10;j++)L(p,142+j*69,1147,398+j*43,839,faint,.7);
    // Architectural arched sash.
    hatch(p,'M 97 689 L 97 447 A 110 110 0 0 1 317 447 L 317 689 Z','#e0e3d3',d,2.5);
    P(p,'M 109 678 L 109 449 A 98 98 0 0 1 305 449 L 305 678 Z',cream,ink,1.5);
    L(p,207,351,207,678,ink,2);L(p,110,494,305,494,ink,2);L(p,110,590,305,590,ink,2);
    for(let j=0;j<6;j++)P(p,`M 120 ${651-j*6} Q 191 ${602-j*4} 296 ${630-j*5}`,'none',faint,.9);
    L(p,87,699,328,699,ink,4);
    // Engraved couch: rolled arms, turned feet, contour lines.
    hatch(p,'M 380 682 Q 373 638 415 629 L 649 624 Q 685 627 681 677 L 678 797 L 380 809 Z','#e1ddcc',d);
    P(p,'M 393 683 Q 489 666 664 675 M 393 693 Q 495 676 664 685','none',ink,1.2);
    P(p,'M 400 704 L 507 700 L 508 786 L 400 791 Z',cream,ink,1.5);P(p,'M 520 700 L 660 697 L 661 782 L 521 787 Z',cream,ink,1.5);
    for(let j=0;j<5;j++){P(p,`M ${411+j*4} 709 L ${411+j*4} 780`,'none',faint,.8);P(p,`M ${646+j*2} 706 L ${646+j*2} 776`,'none',faint,.8);}
    hatch(p,'M 357 741 Q 333 710 315 738 Q 296 768 329 783 L 335 855 Q 352 876 384 869 L 686 851 Q 716 848 715 818 L 719 765 Q 747 750 734 724 Q 719 701 698 731 L 685 800 L 363 816 Z','#e6e0ce',d);
    P(p,'M 332 747 Q 322 763 345 764 M 713 735 Q 726 723 724 747 M 363 831 L 685 815 M 363 843 L 685 827','none',ink,1.5);
    P(p,'M 352 873 Q 360 903 348 925 L 367 926 Q 362 900 371 872 M 686 853 Q 689 882 681 906 L 699 907 Q 693 883 703 851',cream,ink,2);
    // Framed stippled print.
    R(p,461,385,174,171,'none',0,{stroke:ink,'stroke-width':3});R(p,470,394,156,153,'none',0,{stroke:ink});
    C(p,548,458,40,'none',{stroke:ink,'stroke-width':1.5});for(let j=0;j<45;j++)C(p,485+seed(j)*123,410+seed(j+23)*117,.7,ink,{opacity:.45});P(p,'M 483 527 L 524 485 L 557 504 L 591 466 L 615 528','none',ink,1.3);
    // Brass floor lamp.
    L(p,774,455,774,867,ink,3);hatch(p,'M 714 473 L 831 473 L 803 392 L 741 392 Z','#e4dec9',d);O(p,774,873,50,10,cream,{stroke:ink,'stroke-width':2});
    // Fringed rug with concentric elliptical engraving.
    for(let j=0;j<5;j++)O(p,465,1039,266-j*13,71-j*5,'none',{stroke:j===0?ink:faint,'stroke-width':j===0?2:1});
    for(let j=0;j<33;j++){let a=(j/33)*TAU;L(p,465+Math.cos(a)*269,1039+Math.sin(a)*72,465+Math.cos(a)*282,1039+Math.sin(a)*81,faint,1);}
    // Slender side table, glass humidifier.
    O(p,210,962,117,21,cream,{stroke:ink,'stroke-width':2});O(p,210,969,117,21,'none',{stroke:ink,'stroke-width':1});P(p,'M 125 976 L 116 1122 M 292 978 L 303 1123 M 136 1070 L 289 1070','none',ink,4);
    hatch(p,'M 153 827 Q 151 795 210 788 Q 268 795 267 827 L 267 941 Q 208 968 153 941 Z','#dce4db',d);
    O(p,210,825,57,16,cream,{stroke:ink,'stroke-width':1.5});P(p,'M 157 880 Q 211 898 264 880 M 157 887 Q 211 904 264 887','none','#749c9b',1.5);O(p,210,794,18,6,ink);
    P(p,'M 164 841 L 164 930 M 170 844 L 170 936 M 175 848 L 175 937','none',cream,2);O(p,210,943,57,16,'none',{stroke:ink,'stroke-width':1.5});
    // Purifier with rounded perforated front, not a plain box.
    hatch(p,'M 667 756 Q 671 719 731 716 Q 793 720 799 755 L 808 1080 Q 804 1114 745 1120 Q 685 1117 677 1091 Z','#e1e2d5',d);
    O(p,732,743,64,23,cream,{stroke:ink,'stroke-width':2});for(let j=0;j<5;j++)O(p,732,743,55-j*8,17-j*2.4,'none',{stroke:ink,'stroke-width':.8});
    P(p,'M 689 807 Q 743 794 784 807 L 791 1035 Q 744 1056 689 1044 Z',cream,ink,1.6);
    for(let j=0;j<12;j++)for(let k=0;k<17;k++)C(p,698+j*7,820+k*12+(j%2)*4,1.4,ink,{opacity:.66});
    O(p,743,1081,8,5,'none',{stroke:ink});P(p,'M 681 1093 Q 746 1120 805 1084','none',ink,1);
    // Fern at left foreground with actual fronds.
    for(let j=0;j<6;j++){let x=80+j*13,y=909-j%3*17;P(p,`M 107 1000 Q ${x} 951 ${x} ${y}`,'none',ink,1.5);for(let k=0;k<6;k++){let yy=928+k*10;P(p,`M ${x} ${yy} q -16 -15 -21 -8 M ${x} ${yy} q 16 -15 21 -8`,'none',ink,1);}}
    hatch(p,'M 74 996 Q 108 1007 139 996 L 131 1060 Q 107 1071 83 1060 Z','#ddd8c7',d);
    TX(p,'가',210,1180,27,ink,{'font-family':'Noto Serif CJK KR, serif','font-style':'italic','text-anchor':'middle'});TX(p,'나',743,1180,27,ink,{'font-family':'Noto Serif CJK KR, serif','font-style':'italic','text-anchor':'middle'});
  }
  function lineSensor(p,D,scene){
    const d=defs(p,'line'),world=group(p);
    // Circular optical plate within a sectional metal chamber.
    O(world,450,762,378,407,'#e5e3d3',{stroke:ink,'stroke-width':2.4});O(world,450,762,362,390,'none',{stroke:ink,'stroke-width':1});O(world,450,762,342,369,cream,{stroke:ink,'stroke-width':1.4});
    for(let j=0;j<48;j++){let a=j*TAU/48;L(world,450+Math.cos(a)*365,762+Math.sin(a)*393,450+Math.cos(a)*375,762+Math.sin(a)*404,ink,j%4===0?1.7:.7);}
    P(world,'M 370 400 L 370 555 M 511 398 L 511 555','none',ink,2);for(let j=0;j<8;j++)L(world,374+j*18,416,374+j*18,453,faint,1);
    P(world,'M 439 465 L 439 628','none',faint,1.5,{'stroke-dasharray':'6 7'});arrow(world,439,618,90,faint,.8);
    // Engraved emitter, lens and radiating horizontal line.
    hatch(world,'M 125 674 L 210 674 L 242 698 L 242 765 L 210 788 L 125 788 Z','#ddd8c4',d,2);
    for(let j=0;j<7;j++)L(world,134+j*11,682,134+j*11,780,ink,.8);O(world,241,732,12,34,'#e9d6a0',{stroke:ink,'stroke-width':1.5});O(world,244,732,5,24,cream,{stroke:ink,'stroke-width':1});
    TX(world,'광원',129,638,27,ink,{'font-family':'Noto Serif CJK KR, serif','font-style':'italic'});P(world,'M 177 648 L 177 674','none',ink,1);
    const beam=group(world);L(beam,254,732,747,732,ochre,3);L(beam,254,727,747,727,ochre,.7,{opacity:.6});L(beam,254,737,747,737,ochre,.7,{opacity:.6});arrow(beam,720,732,0,ochre,1);
    hatch(world,'M 746 679 L 770 683 L 771 782 L 749 783 Z','#d7dbcd',d,1.5);
    // Separate photodetector sits below and to the right of drop path.
    hatch(world,'M 586 957 L 707 957 L 707 1035 Q 646 1057 586 1035 Z','#d6d9cd',d,2);O(world,646,957,61,15,cream,{stroke:ink,'stroke-width':2});O(world,646,957,45,9,'#acbcb0',{stroke:ink,'stroke-width':1});
    for(let j=0;j<6;j++)L(world,598+j*19,1042,598+j*19,1070,ink,1.7);
    TX(world,'측면 수광부',602,860,25,ink,{'font-family':'Noto Serif CJK KR, serif','font-style':'italic'});P(world,'M 679 876 L 679 939','none',ink,1);
    // Fine engraved droplet highlight and hatching.
    const drop=group(world);P(drop,'M 0 -33 C -14 -13 -28 1 -25 19 C -21 49 24 48 28 19 C 30 1 13 -13 0 -33 Z','#cfdfd9',ink,1.8);P(drop,'M 0 -33 C -14 -13 -28 1 -25 19 C -21 49 24 48 28 19 C 30 1 13 -13 0 -33 Z',d.grain);P(drop,'M -10 -3 Q -19 12 -12 24','none',cream,4);
    const scatter=group(world,{opacity:0});L(scatter,439,732,646,956,ochre,2.5);L(scatter,439,732,622,949,ochre,.8);L(scatter,439,732,674,949,ochre,.8);
    for(let j=0;j<7;j++){let a=(j/6)*Math.PI*.8+.1;L(scatter,439+Math.cos(a)*35,732+Math.sin(a)*35,439+Math.cos(a)*54,732+Math.sin(a)*54,ochre,1.2);}
    const dot=C(scatter,439,732,5,'#c69b40',{stroke:cream,'stroke-width':1});const response=O(world,646,957,47,9,'#d7b661',{opacity:0});
    const signal=group(p);TX(signal,'센서 반응',90,1234,24,ink,{'font-family':'Noto Serif CJK KR, serif','font-style':'italic'});L(signal,306,1226,806,1226,faint,.9);const trace=P(signal,'M 306 1226 L 806 1226','none',ink,2.5);
    const iris=group(p);O(iris,450,762,382,413,cream,{stroke:ink,'stroke-width':2});for(let j=0;j<40;j++){let a=j*TAU/40;L(iris,450+Math.cos(a)*365,762+Math.sin(a)*395,450+Math.cos(a)*378,762+Math.sin(a)*408,ink,1);}
    tick(q=>{fade(beam,scene===1?smooth(phase(q,.2,.42)):1);
      if(scene===1){let a=smooth(phase(q,0,.24));set(iris,{transform:`translate(${450-450*(1+a*1.7)} ${762-762*(1+a*1.7)}) scale(${1+a*1.7})`});fade(iris,1-smooth(phase(q,.07,.22)));fade(drop,0);fade(signal,smooth(phase(q,.67,.88))*.7);}
      else {fade(iris,0);let y=q<.38?lerp(484,732,smooth(phase(q,.06,.38))):q<.6?732:lerp(732,1150,smooth(phase(q,.6,.94)));tr(drop,439,y);fade(drop,1-smooth(phase(q,.88,.98)));fade(scatter,smooth(phase(q,.39,.44))*(1-smooth(phase(q,.59,.67))));let t=phase(q,.43,.53);set(dot,{cx:lerp(439,646,t),cy:lerp(732,956,t)});fade(response,smooth(phase(q,.52,.57))*.85);
        const pts=[];for(let j=0;j<=120;j++){let a=clamp((q-.57)*3);let y=0;if(j<120*a){y=j>16&&j<31?-59*Math.sin((j-16)/15*Math.PI):j>36&&j<58?-22*Math.sin((j-36)/22*Math.PI):Math.sin(j*3)*1.5;}pts.push(`${306+j*4.1667},${1226+y}`);}set(trace,{d:'M '+pts.join(' L ')});
      }
    },D);
  }
  window.PM_STYLES.line=function(parent,i,D){
    const root=stage(parent,cream),d=defs(root,'line');for(let j=0;j<280;j++)C(root,seed(j)*900,seed(j+553)*1600,.4+seed(j+66)*.5,ink,{opacity:.1});lineHeader(root,i);
    if(i===0){const cam=group(root);engravedRoom(cam,d);const paths=[];for(let j=0;j<9;j++)paths.push(P(cam,`M ${210+j*1.3} 787 C ${160+j*11} ${662-j*8} ${392+j*17} ${587+j*14} ${702+j*5} ${815+j*17}`,'none','#6c9699',.9,{opacity:.2}));
      const ds=[];for(let j=0;j<27;j++)ds.push(C(cam,210,780,1.6+seed(j)*2.6,'#759c9d',{stroke:cream,'stroke-width':.4}));
      const lens=group(cam,{opacity:0});C(lens,742,923,115,'none',{stroke:ink,'stroke-width':2});C(lens,742,923,121,'none',{stroke:ink,'stroke-width':.7});L(lens,662,1013,608,1070,ink,9);
      tick(q=>{ds.forEach((e,j)=>{let t=(q*.85+j/27)%1;set(e,{cx:lerp(210,739,t),cy:787-225*Math.sin(t*Math.PI)+t*144+(seed(j+90)-.5)*48,opacity:.25+.75*Math.sin(Math.PI*t)});});paths.forEach((e,j)=>set(e,{opacity:.15+.15*Math.sin(q*5+j)}));fade(lens,smooth(phase(q,.55,.72)));let z=smooth(phase(q,.76,1)),s=1+z*2;set(cam,{transform:`translate(${(450-742*s)*z} ${(762-923*s)*z}) scale(${s})`});},D);
    }else {lineSensor(root,D,i);if(i===1)inletBridge(root,D,'line');if(i===2)comparison(root,D,'line');}
  };


  function inletBridge(p,D,kind){
    const layer=group(p),cover=group(layer);let cx,cy,targetY,scale;
    if(kind==='tech'){techRoom(cover);cx=450;cy=780;targetY=780;scale=1;}
    else if(kind==='pixel'){pixelRoom(cover);cx=740;cy=944;targetY=780;scale=3.5;}
    else if(kind==='paper'){paperRoom(cover,defs(cover,'paper'));cx=733;cy=960;targetY=800;scale=2.1;}
    else {engravedRoom(cover,defs(cover,'line'));C(cover,742,923,115,'none',{stroke:ink,'stroke-width':2});C(cover,742,923,121,'none',{stroke:ink,'stroke-width':.7});L(cover,662,1013,608,1070,ink,9);cx=742;cy=923;targetY=762;scale=3;}
    tick(q=>{let z=smooth(phase(q,0,.22));let s=scale*(1+z*(kind==='pixel'?.55:kind==='tech'?0:.16));if(kind==='pixel')s=Math.round(s*8)/8;set(cover,{transform:`translate(${450-cx*s} ${targetY-cy*s-(kind==='pixel'?z*120:0)}) scale(${s})`});fade(layer,1-smooth(phase(q,.025,kind==='paper'?.135:.2)));},D);
  }

  // A short final comparison: particle composition is not inferred from scattered light.
  function comparison(p,D,kind){
    const cfg={tech:{bg:'#0b202b',panel:'#15333f',edge:'#648b93',ink:'#d9e9e8',beam:'#f7ce72',drop:'#80dce4',dust:'#e0bb8b',trace:'#8ae4d7'},pixel:{bg:'#f0edcf',panel:'#244c58',edge:'#638d89',ink:'#e6eace',beam:'#f9d77d',drop:'#82d5ce',dust:'#d89e70',trace:'#aed1ac'},paper:{bg:paper.bg,panel:'#355e64',edge:'#799a89',ink:'#e9e5c4',beam:'#ffe49a',drop:'#b8dcd2',dust:'#d49b71',trace:'#f1c78b'},line:{bg:cream,panel:'#e7e4d4',edge:ink,ink:ink,beam:ochre,drop:'#cadcd5',dust:'#b2a688',trace:ink}}[kind];
    const g=group(p,{opacity:0}),type=kind==='paper'||kind==='line'?'Noto Serif CJK KR, serif':'Noto Sans CJK KR, sans-serif';
    R(g,45,257,810,1015,cfg.bg);
    TX(g,'서로 다른 입자',450,318,kind==='pixel'?29:28,kind==='tech'?'#d9e9e8':kind==='paper'?paper.ink:kind==='line'?ink:'#244855',{'text-anchor':'middle','font-family':type,'letter-spacing':2});
    const panels=[];
    [72,470].forEach((x,i)=>{
      const a=group(g);panels.push(a);
      if(kind==='paper')P(a,`M ${x} 390 L ${x+349} 378 L ${x+356} 1098 L ${x+9} 1112 Z`,cfg.panel,cfg.edge,7);
      else R(a,x,384,358,728,cfg.panel,kind==='pixel'?0:kind==='tech'?16:100,{stroke:cfg.edge,'stroke-width':kind==='pixel'?12:2});
      if(kind==='line'){R(a,x+14,399,330,698,'none',88,{stroke:ink,'stroke-width':.7});for(let j=0;j<25;j++)L(a,x+20+j*12,408,x+29+j*12,423,faint,.8);}
      TX(a,i===0?'물방울':'먼지',x+179,456,28,cfg.ink,{'text-anchor':'middle','font-family':type,'font-style':kind==='paper'||kind==='line'?'italic':'normal','letter-spacing':2});
      R(a,x+28,612,50,74,kind==='line'?'#d0cbb7':kind==='paper'?'#ddb37a':'#d9a571',kind==='paper'?9:0,{stroke:cfg.edge,'stroke-width':1});
      for(let j=0;j<4;j++)L(a,x+35+j*10,620,x+35+j*10,678,cfg.edge,kind==='pixel'?4:1);
      R(a,x+78,632,12,34,cfg.beam,kind==='paper'?6:0);
      L(a,x+90,649,x+322,649,cfg.beam,kind==='pixel'?8:3);arrow(a,x+314,649,0,cfg.beam,.7);
      L(a,x+322,610,x+322,690,cfg.edge,kind==='pixel'?12:5);
      const particle=group(a),ray=group(a,{opacity:0}),det=group(a),resp=group(a,{opacity:0});
      if(i===0){
        if(kind==='pixel'){R(particle,-8,-24,16,8,cfg.drop);R(particle,-16,-16,32,8,cfg.drop);R(particle,-24,-8,48,32,cfg.drop);R(particle,-16,24,32,8,cfg.drop);R(particle,-12,-8,8,12,'#e5f7d6');}
        else {P(particle,'M 0 -31 Q -31 3 -23 22 Q 0 44 23 22 Q 32 4 0 -31 Z',cfg.drop,kind==='line'?ink:'none',1.5);P(particle,'M -9 -4 Q -18 12 -9 22','none',kind==='line'?cream:'#e7f8e0',3);}
      } else {
        if(kind==='pixel'){R(particle,-28,-12,16,32,cfg.dust);R(particle,-16,-24,32,56,cfg.dust);R(particle,16,-8,20,24,cfg.dust);R(particle,0,-12,12,12,'#f0c991');}
        else {P(particle,'M -29 -12 L -11 -28 L 1 -17 L 20 -25 L 29 -6 L 17 5 L 25 24 L 3 30 L -7 19 L -28 23 L -22 4 Z',cfg.dust,kind==='line'?ink:'none',1.5);P(particle,'M -13 -12 L 8 -9 L 16 7 M -11 10 L 1 18','none',kind==='line'?ink:'#f5c99a',2);}
      }
      L(ray,x+179,649,x+273,849,cfg.beam,kind==='pixel'?5:2.5);if(kind!=='pixel'){L(ray,x+179,649,x+249,849,cfg.beam,.7);L(ray,x+179,649,x+297,849,cfg.beam,.7);}
      R(det,x+231,852,84,63,kind==='line'?'#cdd3c7':'#b98363',kind==='pixel'?0:8,{stroke:cfg.edge,'stroke-width':1});R(det,x+225,842,96,12,kind==='line'?'#9aa99e':'#acc7ad',kind==='pixel'?0:5);R(resp,x+231,841,84,13,cfg.beam,kind==='pixel'?0:5);
      for(let j=0;j<4;j++)L(det,x+240+j*20,916,x+240+j*20,934,cfg.edge,kind==='pixel'?4:2);
      const trace=P(a,`M ${x+39} 1033 L ${x+317} 1033`,'none',cfg.trace,kind==='pixel'?6:3);
      L(a,x+37,1033,x+322,1033,cfg.edge,.8);
      TX(a,'신호',x+179,985,18,cfg.ink,{'text-anchor':'middle','font-family':type,'letter-spacing':2});
      tick(q=>{let z=phase(q,.8,.88),y=lerp(565,649,smooth(z));tr(particle,x+179,kind==='pixel'?Math.round(y/4)*4:y);let a=smooth(phase(q,.875,.91));fade(ray,a);fade(resp,a);let h=smooth(phase(q,.91,.965))*(i===0?1:.62);set(trace,{d:`M ${x+39} 1033 L ${x+103} 1033 L ${x+129} ${1033-50*h} L ${x+153} ${1033+5*h} L ${x+175} ${1033-19*h} L ${x+193} 1033 L ${x+317} 1033`});},D);
    });
    TX(g,'성분 대신 산란광을 읽습니다',450,1191,kind==='pixel'?24:25,kind==='tech'?'#a9d3d8':kind==='paper'?paper.ink:kind==='line'?ink:'#355866',{'text-anchor':'middle','font-family':type,'letter-spacing':1});
    tick(q=>fade(g,smooth(phase(q,.765,.81))),D);
  }
  window.PM_STYLES.complete=function(parent,i,D){
    const root=stage(parent,'#0b202b');
    label(root,'입자와 빛 · 원리 시각화',62,132,'#83b8c1',18);L(root,62,157,838,157,'#35545f',1);
    const foot=TX(root,'설명용 도해 · 실제 크기와 속도가 아닙니다',450,1500,19,'#71949f',{'text-anchor':'middle'});
    const title=(s)=>label(root,s,62,213,'#e4f2ee',29);
    const water=(p,x,y,r,alpha=1)=>C(p,x,y,r,'#79d4df',{stroke:'#c2f9fa','stroke-width':2,opacity:alpha});
    const crystal=(p,x,y,r)=>POLY(p,`${x-r},${y-3} ${x-4},${y-r} ${x+r},${y-5} ${x+r*.6},${y+r} ${x-r*.7},${y+r*.6}`,'#ecd2a2',{stroke:'#fff0cc','stroke-width':1.5});
    if([0,1,5,11,19,23].includes(i)){
      title(i<2?'작은 방울, 빨간 표시등':i===5?'실내에서 흡입구로':'처음의 빨간불로');
      const room=group(root);techRoom(room);
      const ds=Array.from({length:32},(_,j)=>water(room,220,780,2.5+seed(j)*3));
      const led=C(room,738,1000,9,'#ee775e');
      tick(q=>{ds.forEach((e,j)=>{let t=(q*.8+j/32)%1;set(e,{cx:220+467*t,cy:792-198*Math.sin(t*Math.PI)+t*67+(seed(j+57)-.5)*48*Math.sin(t*Math.PI),opacity:.25+.65*Math.sin(t*Math.PI)});});set(led,{fill:i===0&&q<.38?'#82d3c8':'#ee775e'});},D);
      if(i===11)TX(root,'표시값 ↑',450,305,34,'#ef997d',{'text-anchor':'middle'});
      if(i===1)TX(root,'맑은 물인데, 왜?',450,305,34,'#ecdcac',{'text-anchor':'middle'});
    }else if([6,7,8,9,10,11,20,25].includes(i)){
      title('광학식 센서 · 빛이 신호로');
      const old=TW.length;techSensor(root,D,1);evalTo(D);TW.splice(old);
      // Keep the repaired camera fixed. The particle always follows x=430.
      const dust=[7,8].includes(i), show=i!==6;
      const part=group(root,{opacity:show?1:0});
      if(dust)crystal(part,0,0,21);else water(part,0,0,24);
      const rays=group(root,{opacity:0});
      for(let a=0;a<8;a++){const ang=a*Math.PI/4;L(rays,430,730,430+Math.cos(ang)*85,730+Math.sin(ang)*85,'#f6d382',1.5,{opacity:.65});}
      L(rays,430,730,650,932,'#f6d382',3);arrow(rays,558,847,43,'#f6d382',1.2);
      const photon=C(rays,430,730,5,'#fff6ca');
      const detect=R(root,603,931,97,9,'#f8e7a2',3,{opacity:0});
      label(root,'입자 이동',330,327,'#9ddde3',22);label(root,'빛만 수광부에 도달',502,1144,'#f0cf83',20);
      const trace=P(root,'M 318 1224 L 803 1224','none','#8ae4d7',4);
      tick(q=>{if(i===7||i===9)q=q*.65;else if(i===8||i===10)q=.65+q*.35;let y=q<.35?lerp(505,730,smooth(phase(q,0,.35))):q<.6?730:lerp(730,1100,smooth(phase(q,.6,1)));tr(part,430,y);let a=show?smooth(phase(q,.35,.4))*(1-smooth(phase(q,.58,.65))):0;fade(rays,a);let t=phase(q,.4,.55);set(photon,{cx:lerp(430,650,t),cy:lerp(730,932,t)});fade(detect,show?smooth(phase(q,.54,.59))*(1-smooth(phase(q,.8,1))):0);let h=show?smooth(phase(q,.57,.72)):0;set(trace,{d:`M 318 1224 L 420 1224 L 445 ${1224-h*46} L 466 1224 L 494 ${1224-h*16} L 520 1224 L 803 1224`});},D);
      if(i===11){const num=TX(root,'표시값 ↑',670,302,29,'#ef997d',{'text-anchor':'middle'});}
    }else if([2,3,4,15,24].includes(i)){
      title('분무를 확대하면');
      R(root,140,760,620,300,'#173541',30,{stroke:'#668f9d','stroke-width':2});
      const surface=P(root,'','none','#9cdee4',3);R(root,143,855,614,202,'#254e60',20,{opacity:.7});
      O(root,450,1048,92,17,'#c5a56a',{stroke:'#f4d28b','stroke-width':2});label(root,'진동판',390,1125,'#d1c4a3',24);
      const ds=Array.from({length:14},(_,j)=>water(root,450,800,8+seed(j)*15));
      tick(q=>{let path='M 143 850';for(let x=143;x<=757;x+=8)path+=` L ${x} ${850+7*Math.sin(x/27+q*D*19)}`;set(surface,{d:path});ds.forEach((e,j)=>{let t=(q*D*.23+j/14)%1;set(e,{cx:450+Math.sin(j*7)*t*250,cy:825-t*420,opacity:Math.sin(t*Math.PI)*.9});});},D);
      if(i===4){label(root,'작은 액체 방울',270,344,'#a8e6ea',32);label(root,'수증기(기체)와 다릅니다',240,390,'#92aeb9',23);}
    }else if(i===18){
      title('물자국이 마르는 것처럼');
      O(root,450,877,320,115,'#173843',{stroke:'#78959d','stroke-width':2});
      const wet=O(root,450,860,210,70,'#73bccc',{opacity:.6});
      const residue=O(root,450,860,207,68,'none',{stroke:'#eee7cc','stroke-width':12,opacity:0,'stroke-dasharray':'7 5 13 3'});
      tick(q=>{set(wet,{rx:210*(1-q*.95),ry:70*(1-q*.95),opacity:.6*(1-q)});fade(residue,smooth(phase(q,.25,.9)));},D);
      label(root,'물은 증발하고, 자국은 남습니다',183,1110,'#d8ddcb',27);
    }else if([21,22].includes(i)){
      title(i===21?'서로 다른 두 과정':'숫자만으로는 알 수 없는 것');
      [90,480].forEach((x,j)=>{R(root,x,435,330,590,'#15333f',16,{stroke:'#426573','stroke-width':2});label(root,j?'증발 뒤 남은 입자':'물방울의 빛 산란',x+25,492,'#cfdfdb',23);});
      const drop=water(root,255,710,45);L(root,132,710,380,710,'#f2d081',3);L(root,255,710,355,870,'#f2d081',3);R(root,330,875,48,18,'#b2d9d6',2);crystal(root,645,730,32);
      if(i===22){R(root,225,1090,450,90,'#0b202b',12,{stroke:'#df997b','stroke-width':2});TX(root,'성분 · 위험성은 별도 판단',450,1148,29,'#e7ceaf',{'text-anchor':'middle'});}
    }else{
      title('물과 함께 이동한 미네랄');
      const g=group(root), droplet=water(g,450,720,170,.6);
      const dots=[];for(let j=0;j<13;j++){let a=j*2.399,r=35+Math.sqrt(j)*31;dots.push(C(g,450+Math.cos(a)*r,720+Math.sin(a)*r,4,'#ecd2a2'));}
      const evaporate=[12,17].includes(i);
      const vapor=Array.from({length:10},(_,j)=>water(root,450,500,3,.4));
      tick(q=>{let z=evaporate?1-smooth(phase(q,.15,.85))*.88:1;set(droplet,{r:170*z,opacity:evaporate?.6*(1-q):.6});dots.forEach((e,j)=>{let a=j*2.399,r=(35+Math.sqrt(j)*31)*(evaporate?z:1);set(e,{transform:`translate(${(Math.cos(a)*(35+Math.sqrt(j)*31))*(z-1)} ${(Math.sin(a)*(35+Math.sqrt(j)*31))*(z-1)})`});});vapor.forEach((e,j)=>{let t=(q+j/10)%1;set(e,{cx:450+Math.sin(j*7)*180,cy:550-t*160,opacity:evaporate?Math.sin(t*Math.PI)*q*.4:0});});if(i===16)tr(g,0,-q*130);},D);
      label(root,evaporate?'물 증발 → 남을 수 있는 고체 입자':'물속에 녹아 있는 미네랄',150,1060,'#d9d6b7',28);
      label(root,'용존 성분은 기호로 표시 · 실제 크기 아님',145,1130,'#7799a6',21);
    }
  };

})();
