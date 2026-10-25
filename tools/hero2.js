function gear(lv){
  return {
    weapon: lv>=10?'legend':lv>=8?'steel':lv>=5?'iron':lv>=3?'copper':lv>=2?'stick':null,
    shield: lv>=10?'dragon':lv>=9?'magic':lv>=7?'steel':lv>=5?'iron':lv>=3?'leather':null,
    armor:  lv>=10?'gold':lv>=9?'magic':lv>=7?'steel':lv>=6?'chain':lv>=4?'leather':'tshirt',
    helm:   lv>=10?'king':lv>=9?'wing':lv>=7?'iron':null,
    cape:   lv>=10?'royal':lv>=8?'red':null
  };
}
var GN={
  weapon:{stick:'ひのきのぼう',copper:'どうのつるぎ',iron:'てつのつるぎ',steel:'はがねのつるぎ',legend:'でんせつのつるぎ'},
  shield:{leather:'かわのたて',iron:'てつのたて',steel:'はがねのたて',magic:'まほうのたて',dragon:'ドラゴンのたて'},
  armor:{tshirt:'Tシャツとたんパン',leather:'かわのよろい',chain:'くさりかたびら',steel:'はがねのよろい',magic:'まほうのよろい',gold:'おうごんのよろい'},
  helm:{iron:'てつのかぶと',wing:'はねかぶと',king:'おうのかぶと'},
  cape:{red:'ゆうしゃのマント',royal:'おうのマント'}
};
/* 80×96 のドット絵。グリッドに塗ってから輪郭線を付け、横方向にまとめて rect にする。 */
function heroSvg(lv){
  var g=gear(lv), W=80, H=96;
  var HP={
    K:'#1a1a2e',
    s:'#ffd6a5', s1:'#e0a877', s2:'#fff0dc',
    N:'#6b4423', N1:'#4a2c12', N2:'#8f5f33',
    w:'#ffffff', w1:'#c9c9d6',
    r:'#e63946', r1:'#9b1d2a', R:'#9b1d2a',
    B:'#1d4ed8', B1:'#142f8f', B2:'#4895ef',
    n:'#b08968', n1:'#6b4423', n2:'#d4ab85',
    e:'#c9c9c9', E:'#6b7280', E1:'#3f4652', E2:'#9aa3b0',
    b:'#4895ef', b2:'#7fdfff',
    y:'#ffd60a', y1:'#c99a00', y2:'#fff4b0',
    t:'#e9c46a', t1:'#a8841f', t2:'#f7e4a8',
    o:'#f4a261', o1:'#b86f2e', o2:'#ffd0a0',
    c:'#7fdfff', c1:'#2fa7d6', c2:'#ddf8ff',
    P:'#6d28d9', P1:'#44178c', P2:'#9d5cf0',
    m:'#ff9fb5', k:'#1a1a2e',
    st:'#dfe9f5', st1:'#8fa3bf'
  };
  function col(c){ return HP[c] || (typeof PAL!=='undefined' && PAL[c]) || c; }
  function Layer(){ var gr=[]; for(var y=0;y<H;y++){ var row=[]; for(var x=0;x<W;x++) row.push(null); gr.push(row); } this.g=gr; this.minY=0; this.extra=[]; }
  Layer.prototype.px=function(x,y,c){ if(x<0||x>=W||y<0||y>=H){ if(c) this.extra.push([x,y,c]); return; } this.g[y][x]=c; };
  Layer.prototype.fill=function(x,y,w,h,c){ for(var j=y;j<y+h;j++) for(var i=x;i<x+w;i++) this.px(i,j,c); };
  Layer.prototype.clear=function(x,y,w,h){ this.fill(x,y,w,h,null); };
  Layer.prototype.box=function(x,y,w,h,c,edge){ this.fill(x,y,w,h,c); this.fill(x,y,w,1,edge); this.fill(x,y+h-1,w,1,edge); this.fill(x,y,1,h,edge); this.fill(x+w-1,y,1,h,edge); };
  Layer.prototype.outline=function(){
    var gr=this.g, add=[];
    for(var y=0;y<H;y++) for(var x=0;x<W;x++){
      if(gr[y][x]) continue;
      if((y>0&&gr[y-1][x])||(y<H-1&&gr[y+1][x])||(x>0&&gr[y][x-1])||(x<W-1&&gr[y][x+1])) add.push([x,y]);
    }
    for(var i=0;i<add.length;i++) gr[add[i][1]][add[i][0]]='K';
  };
  Layer.prototype.svg=function(){
    /* 横の連続をまとめ、同じ形の行が続けば縦にも伸ばして rect の数を減らす */
    var s='', gr=this.g, open={};
    for(var y=0;y<=H;y++){
      var runs={}, x=0;
      if(y<H) while(x<W){
        var c=gr[y][x]; if(!c){ x++; continue; }
        var x2=x; while(x2<W && gr[y][x2]===c) x2++;
        runs[x+','+(x2-x)+','+c]=true; x=x2;
      }
      for(var k in open){ if(!runs[k]){ var o=open[k], p=k.split(','); s+='<rect x="'+p[0]+'" y="'+o.y+'" width="'+p[1]+'" height="'+(y-o.y)+'" fill="'+col(p[2])+'"/>'; delete open[k]; } }
      for(var k2 in runs){ if(!open[k2]) open[k2]={y:y}; }
    }
    for(var i=0;i<this.extra.length;i++){ var e=this.extra[i]; s+='<rect x="'+e[0]+'" y="'+e[1]+'" width="1" height="1" fill="'+col(e[2])+'"/>'; }
    return s;
  };

  var L=new Layer(), A=g.armor, S=g.shield, Hm=g.helm, Wp=g.weapon, C=g.cape;

  /* ---- マント（体の後ろ） ---- */
  if(C==='red'){
    L.fill(14,34,52,46,'r');
    L.fill(14,34,52,2,'r1'); L.fill(14,34,2,46,'r1'); L.fill(64,34,2,46,'r1'); L.fill(14,78,52,2,'r1');
    L.fill(22,40,1,38,'r1'); L.fill(30,44,1,34,'r1'); L.fill(49,44,1,34,'r1'); L.fill(57,40,1,38,'r1');
    for(var cx=16;cx<64;cx+=6) L.clear(cx,79,2,1);
  }
  if(C==='royal'){
    L.fill(12,34,56,48,'P');
    L.fill(12,34,56,2,'t'); L.fill(12,34,2,48,'t'); L.fill(66,34,2,48,'t'); L.fill(12,78,56,4,'t');
    L.fill(20,40,1,38,'P1'); L.fill(28,44,1,34,'P1'); L.fill(51,44,1,34,'P1'); L.fill(59,40,1,38,'P1');
    L.fill(16,36,4,2,'t2'); L.fill(60,36,4,2,'t2');
    for(var dx=16;dx<64;dx+=8){ L.fill(dx,79,2,2,'w'); }
    for(var dx2=20;dx2<64;dx2+=8){ L.fill(dx2,80,1,1,'K'); }
  }

  /* ---- 首・顔 ---- */
  L.fill(36,32,8,5,'s1');
  L.fill(28,14,24,19,'s');
  L.fill(28,14,2,19,'s1'); L.fill(50,14,2,19,'s1');
  L.fill(30,31,20,2,'s1');
  L.fill(30,14,20,3,'s1');
  /* 髪 */
  L.fill(26,6,28,10,'N');
  L.fill(26,12,3,12,'N'); L.fill(51,12,3,12,'N');
  L.fill(27,12,1,12,'N1'); L.fill(53,12,1,12,'N1');
  L.fill(29,8,6,2,'N2'); L.fill(29,10,2,4,'N2'); L.fill(40,7,8,1,'N2');
  L.fill(26,14,28,2,'N1');
  var bang=[30,35,40,45];
  for(var bi=0;bi<bang.length;bi++){ L.fill(bang[bi],16,4,2,'N'); L.fill(bang[bi]+1,18,2,1,'N'); L.fill(bang[bi],16,4,1,'N1'); }
  L.fill(49,16,3,2,'N'); L.fill(28,16,2,2,'N');
  /* 眉・目・ほほ・口 */
  L.fill(33,20,4,1,'N1'); L.fill(43,20,4,1,'N1');
  L.fill(33,22,4,5,'k'); L.fill(43,22,4,5,'k');
  L.px(34,23,'w'); L.px(44,23,'w'); L.fill(34,25,2,1,'B2'); L.fill(44,25,2,1,'B2');
  L.fill(30,27,2,1,'m'); L.fill(48,27,2,1,'m');
  L.fill(38,29,4,1,'r1'); L.px(37,29,'s1'); L.px(42,29,'s1');

  /* ---- 腕 ---- */
  L.box(18,36,8,18,'s','s1'); L.box(54,36,8,18,'s','s1');
  L.fill(20,38,2,10,'s2'); L.fill(56,38,2,10,'s2');
  /* ---- 手 ---- */
  L.box(18,54,8,6,'s','s1'); L.box(54,54,8,6,'s','s1');
  L.fill(20,55,2,2,'s2'); L.fill(56,55,2,2,'s2');

  /* ---- 胴・袖・ズボン・足 ---- */
  function torso(fc,ec,hi,sh){
    L.box(26,36,28,20,fc,ec);
    L.box(18,36,8,7,fc,ec); L.box(54,36,8,7,fc,ec);
    L.fill(28,38,2,15,hi); L.fill(50,38,2,15,sh); L.fill(28,53,24,2,sh);
    L.fill(20,37,2,4,hi); L.fill(59,38,2,3,sh);
  }
  function pants(fc,ec,hi,sh){ L.box(26,56,28,12,fc,ec); L.fill(28,57,2,9,hi); L.fill(50,57,2,9,sh); L.fill(39,57,2,10,ec); }
  function legs(fc,ec,hi){ L.box(28,68,10,17,fc,ec); L.box(42,68,10,17,fc,ec); L.fill(29,69,2,13,hi); L.fill(43,69,2,13,hi); }
  function shoes(fc,ec,hi){ L.box(26,84,12,7,fc,ec); L.box(42,84,12,7,fc,ec); L.fill(27,85,10,1,hi); L.fill(43,85,10,1,hi); L.fill(26,89,12,2,ec); L.fill(42,89,12,2,ec); }
  function shoulders(fc,ec,hi){ L.box(14,33,14,9,fc,ec); L.box(52,33,14,9,fc,ec); L.fill(15,34,12,1,hi); L.fill(53,34,12,1,hi); L.fill(16,36,10,1,hi); L.fill(54,36,10,1,hi); }
  function belt(fc,ec,buck,buckE){ L.box(26,52,28,4,fc,ec); if(buck){ L.box(37,51,6,5,buck,buckE); L.fill(39,53,2,1,'w'); } }

  if(A==='tshirt'){
    torso('w','w1','w','w1');
    /* 胸のハートマーク */
    L.fill(37,41,2,1,'r'); L.fill(41,41,2,1,'r'); L.fill(36,42,8,2,'r'); L.fill(37,44,6,1,'r'); L.fill(38,45,4,1,'r'); L.fill(39,46,2,1,'r');
    L.px(37,42,'m'); L.px(42,43,'r1'); L.fill(40,45,2,1,'r1');
    pants('B','B1','B2','B1');
    legs('s','s1','s2');
    shoes('N','N1','N2');
  }else if(A==='leather'){
    torso('n','n1','n2','n1');
    for(var sy=39;sy<52;sy+=3){ L.px(31,sy,'n1'); L.px(48,sy,'n1'); }
    L.fill(38,38,4,14,'n1'); L.fill(39,38,2,14,'n2');
    belt('N','N1','t','t1');
    pants('N','N1','n','N1');
    legs('s','s1','s2');
    shoes('N','N1','N2');
  }else if(A==='chain'){
    torso('e','E','e','E');
    for(var cy=38;cy<53;cy++) for(var cxx=27;cxx<53;cxx++) if((((cxx>>1)+(cy>>1))&1)===0) L.px(cxx,cy,'E');
    for(var cy2=37;cy2<42;cy2++){ for(var a1=19;a1<25;a1++) if((((a1>>1)+(cy2>>1))&1)===0) L.px(a1,cy2,'E'); for(var a2=55;a2<61;a2++) if((((a2>>1)+(cy2>>1))&1)===0) L.px(a2,cy2,'E'); }
    belt('N','N1','t','t1');
    pants('E','E1','E2','E1');
    legs('E','E1','E2');
    shoes('E1','K','E');
  }else if(A==='steel'){
    torso('e','E1','w','E');
    L.fill(39,38,2,14,'E'); L.fill(30,45,20,1,'E');
    L.fill(32,39,4,4,'w'); L.fill(44,39,4,4,'E2');
    shoulders('E','E1','e');
    belt('E1','K','e','E1');
    pants('E','E1','E2','E1');
    legs('E','E1','E2');
    shoes('E1','K','E');
  }else if(A==='magic'){
    torso('b','B1','b2','B');
    L.fill(36,41,8,8,'c'); L.fill(38,43,4,4,'w'); L.px(37,42,'c2'); L.px(42,47,'c1');
    L.fill(30,45,6,1,'B'); L.fill(44,45,6,1,'B');
    shoulders('B','B1','c');
    belt('B1','K','c','c1');
    pants('B','B1','b','B1');
    legs('B','B1','b');
    shoes('B1','K','B');
  }else if(A==='gold'){
    torso('y','t1','y2','t');
    L.fill(36,41,8,8,'R'); L.fill(37,42,6,6,'r'); L.fill(38,43,2,2,'w'); L.px(41,46,'R');
    L.fill(30,45,6,1,'t1'); L.fill(44,45,6,1,'t1'); L.fill(30,39,4,2,'w');
    shoulders('t','t1','y2');
    belt('t1','K','r','R');
    pants('t','t1','y2','t1');
    legs('t','t1','y2');
    shoes('t1','K','y');
  }

  /* ---- かぶと ---- */
  function dome(fc,ec,hi,rim){
    L.fill(26,6,28,12,fc); L.fill(28,3,24,3,fc); L.fill(30,2,20,1,fc); L.fill(34,1,12,1,fc);
    L.fill(24,10,2,8,fc); L.fill(54,10,2,8,fc);
    L.fill(28,4,4,8,hi); L.fill(32,3,6,2,hi);
    L.fill(50,6,3,12,ec);
    L.box(24,16,32,3,rim,ec);
    L.box(24,19,5,6,fc,ec); L.box(51,19,5,6,fc,ec);
  }
  if(Hm==='iron'){ dome('e','E1','w','E'); L.fill(39,2,2,14,'E'); }
  if(Hm==='wing'){
    dome('c','c1','c2','b');
    L.fill(39,2,2,14,'c1');
    var wing=[[16,11,8,3],[14,8,8,3],[12,5,6,3],[11,2,4,3],[10,0,3,2]];
    for(var wi=0;wi<wing.length;wi++){ var w0=wing[wi]; L.fill(w0[0],w0[1],w0[2],w0[3],'w'); L.fill(80-w0[0]-w0[2],w0[1],w0[2],w0[3],'w'); L.fill(w0[0],w0[1]+w0[3]-1,w0[2],1,'w1'); L.fill(80-w0[0]-w0[2],w0[1]+w0[3]-1,w0[2],1,'w1'); }
  }
  if(Hm==='king'){
    dome('t','t1','y2','y1');
    L.fill(39,2,2,14,'t1');
    L.fill(26,0,4,6,'y'); L.fill(50,0,4,6,'y'); L.fill(32,-1,4,5,'y'); L.fill(44,-1,4,5,'y');
    L.fill(27,0,1,5,'y2'); L.fill(51,0,1,5,'y2'); L.fill(33,-1,1,4,'y2'); L.fill(45,-1,1,4,'y2');
    L.fill(38,8,4,4,'c'); L.px(38,8,'c2'); L.fill(30,9,3,3,'r'); L.fill(47,9,3,3,'r'); L.px(30,9,'m'); L.px(47,9,'m');
    L.fill(38,-9,4,11,'r'); L.fill(36,-7,2,7,'r'); L.fill(42,-7,2,7,'r'); L.fill(39,-11,2,2,'r'); L.fill(41,-8,1,10,'r1'); L.fill(43,-6,1,5,'r1');
  }

  /* ---- 盾（左腕の前） ---- */
  function shieldBase(outer,inner,hi,sh){
    L.fill(7,36,20,26,outer); L.fill(9,38,16,22,inner);
    L.clear(7,36,2,2); L.clear(25,36,2,2); L.clear(7,60,2,2); L.clear(25,60,2,2);
    L.px(9,38,outer); L.px(24,38,outer); L.px(9,59,outer); L.px(24,59,outer);
    L.fill(10,39,2,8,hi); L.fill(22,41,2,17,sh); L.fill(11,57,12,1,sh);
  }
  if(S==='leather'){ shieldBase('N','n','n2','n1'); L.fill(15,47,4,4,'N'); L.px(15,47,'n2'); L.px(10,40,'N1'); L.px(23,40,'N1'); L.px(10,57,'N1'); L.px(23,57,'N1'); }
  if(S==='iron'){ shieldBase('E1','e','w','E'); L.px(10,39,'E1'); L.px(23,39,'E1'); L.px(10,58,'E1'); L.px(23,58,'E1'); L.fill(16,40,2,18,'E2'); }
  if(S==='steel'){ shieldBase('E1','e','w','E'); L.fill(15,40,4,18,'r'); L.fill(10,46,14,4,'r'); L.fill(18,40,1,18,'r1'); L.fill(10,49,14,1,'r1'); L.px(10,39,'E1'); L.px(23,39,'E1'); L.px(10,58,'E1'); L.px(23,58,'E1'); }
  if(S==='magic'){
    shieldBase('c1','b','b2','B');
    var star=[[17,44,1],[16,45,3],[16,46,3],[12,47,11],[13,48,9],[14,49,7],[15,50,5],[14,51,7],[13,52,4],[18,52,4],[12,53,3],[20,53,3]];
    for(var si=0;si<star.length;si++) L.fill(star[si][0],star[si][1],star[si][2],1,'y');
    L.px(17,45,'y2'); L.px(13,47,'y2'); L.px(17,50,'y1'); L.px(21,53,'y1');
    L.px(9,40,'c2'); L.px(24,40,'c2'); L.px(9,57,'c2'); L.px(24,57,'c2');
  }
  if(S==='dragon'){
    shieldBase('t1','r1','r','R');
    L.fill(11,40,12,18,'r'); L.fill(11,40,2,6,'m'); L.fill(21,42,2,16,'R');
    L.fill(8,38,18,1,'y'); L.fill(8,59,18,1,'y'); L.fill(8,38,1,22,'y'); L.fill(25,38,1,22,'y');
    L.fill(14,43,6,2,'y'); L.fill(13,45,8,2,'y'); L.fill(16,47,2,8,'y'); L.fill(14,50,6,2,'y'); L.fill(13,47,1,2,'y'); L.fill(20,47,1,2,'y');
    L.fill(19,45,2,1,'y1'); L.fill(17,52,1,3,'y1'); L.px(15,43,'y2');
    L.fill(9,39,2,2,'y'); L.fill(23,39,2,2,'y'); L.fill(9,57,2,2,'y'); L.fill(23,57,2,2,'y');
  }

  L.outline();

  /* ---- 武器（右手。別レイヤーで最後に。柄がグループの一番下） ---- */
  var WL=new Layer(), wsvg='';
  function tip(x,yTop,w,c,hi){ /* 刃先を2段で細くする */
    if(w>=8){ WL.fill(x+1,yTop+2,w-2,2,c); WL.fill(x+2,yTop,w-4,2,c); WL.fill(x+1,yTop+2,1,2,hi); WL.fill(x+2,yTop,1,2,hi); }
    else { WL.fill(x+1,yTop+2,w-2,2,c); WL.fill(x+2,yTop,w-4,2,c); WL.fill(x+1,yTop+2,1,2,hi); WL.fill(x+2,yTop,1,2,hi); }
  }
  function grip(c,stripe,pom,pomE){ WL.fill(56,54,6,9,c); for(var gy=55;gy<62;gy+=2) WL.fill(56,gy,6,1,stripe); WL.fill(54,63,10,3,pom); WL.fill(54,63,10,1,pomE); }
  if(Wp==='stick'){
    WL.fill(56,20,6,46,'n'); WL.fill(56,20,1,46,'n2'); WL.fill(61,20,1,46,'N'); WL.fill(56,18,6,2,'N2'); WL.fill(57,17,4,1,'N2');
    WL.fill(56,28,6,1,'N1'); WL.fill(56,42,6,1,'N1'); WL.fill(56,52,6,2,'N1'); WL.fill(56,60,6,1,'N1'); WL.fill(58,34,2,1,'N');
  }
  if(Wp==='copper'){
    WL.fill(56,18,6,32,'o'); WL.fill(56,18,2,32,'o2'); WL.fill(60,18,2,32,'o1'); tip(56,14,6,'o','o2');
    WL.fill(49,50,20,4,'t'); WL.fill(49,50,20,1,'t2'); WL.fill(49,53,20,1,'t1'); WL.fill(49,50,2,4,'t1'); WL.fill(67,50,2,4,'t1');
    grip('N','n','t','t2');
  }
  if(Wp==='iron'){
    WL.fill(56,8,6,42,'e'); WL.fill(56,8,2,42,'w'); WL.fill(60,8,2,42,'E'); WL.fill(58,12,1,36,'E2'); tip(56,4,6,'e','w');
    WL.fill(48,50,22,4,'E'); WL.fill(48,50,22,1,'E2'); WL.fill(48,53,22,1,'E1'); WL.fill(48,50,2,4,'E1'); WL.fill(68,50,2,4,'E1');
    grip('N','n','E','E2');
  }
  if(Wp==='steel'){
    WL.fill(55,2,8,48,'st'); WL.fill(55,2,2,48,'w'); WL.fill(61,2,2,48,'st1'); WL.fill(58,6,1,42,'st1'); tip(55,-2,8,'st','w');
    WL.fill(47,50,24,4,'t'); WL.fill(47,50,24,1,'t2'); WL.fill(47,53,24,1,'t1'); WL.fill(47,49,3,1,'t'); WL.fill(68,49,3,1,'t'); WL.fill(57,50,4,4,'b'); WL.px(57,50,'b2');
    grip('N','t','t','t2');
  }
  if(Wp==='legend'){
    WL.fill(55,-6,8,56,'y'); WL.fill(55,-6,2,56,'w'); WL.fill(61,-6,2,56,'t'); WL.fill(58,-2,1,50,'y2'); WL.fill(59,-2,1,50,'t'); tip(55,-10,8,'y','w');
    WL.fill(46,50,26,4,'t'); WL.fill(46,50,26,1,'t2'); WL.fill(46,53,26,1,'t1'); WL.fill(46,48,3,2,'y'); WL.fill(69,48,3,2,'y'); WL.fill(46,54,3,2,'y'); WL.fill(69,54,3,2,'y');
    WL.fill(57,49,4,5,'R'); WL.fill(58,50,2,3,'r'); WL.px(58,50,'m');
    grip('P','t','y','y2'); WL.fill(58,64,2,1,'r');
  }
  if(Wp){ WL.outline(); wsvg='<g class="wpn'+(Wp==='legend'?' glow':'')+'">'+WL.svg()+'</g>'; }

  return '<svg viewBox="0 0 80 96" xmlns="http://www.w3.org/2000/svg" shape-rendering="crispEdges" overflow="visible">'+L.svg()+wsvg+'</svg>';
}
