function generateTables(){
  let p = parseInt(document.getElementById('processes').value||2);
  let r = parseInt(document.getElementById('resources').value||2);

  // AVAILABLE
  let avail = '<table><tr>';
  for(let j=0;j<r;j++) avail += `<th>R${j+1}</th>`;
  avail += '</tr><tr>';
  for(let j=0;j<r;j++) avail += `<td><input id="avail_${j}" type="number" value="0"></td>`;
  avail += '</tr></table>';
  document.getElementById('availableTable').innerHTML = avail;

  // MAX
  let max = '<table><tr><th></th>';
  for(let j=0;j<r;j++) max += `<th>R${j+1}</th>`;
  max += '</tr>';
  for(let i=0;i<p;i++){
    max += `<tr><th>P${i+1}</th>`;
    for(let j=0;j<r;j++) max += `<td><input id="max_${i}_${j}" type="number" value="1"></td>`;
    max += '</tr>';
  }
  max += '</table>';
  document.getElementById('maxTable').innerHTML = max;

  // ALLOCATION
  let alloc = '<table><tr><th></th>';
  for(let j=0;j<r;j++) alloc += `<th>R${j+1}</th>`;
  alloc += '</tr>';
  for(let i=0;i<p;i++){
    alloc += `<tr><th>P${i+1}</th>`;
    for(let j=0;j<r;j++) alloc += `<td><input id="alloc_${i}_${j}" type="number" value="0"></td>`;
    alloc += '</tr>';
  }
  alloc += '</table>';
  document.getElementById('allocationTable').innerHTML = alloc;

  // reset
  document.getElementById('safeSeq').innerText = 'Safe Sequence: n/a';
  document.getElementById('deadlockInfo').innerText = 'Deadlocked: —';
  document.getElementById('resolveBtn').disabled=true;
  document.getElementById('resolveOutput').innerText='No action taken yet.';
  document.getElementById('graph').innerHTML='';
}

function collectData(){
  const p = parseInt(document.getElementById('processes').value||0);
  const r = parseInt(document.getElementById('resources').value||0);
  const allocation = [], request = [], available = [];
  for(let i=0;i<p;i++){
    const a=[]; const m=[];
    for(let j=0;j<r;j++){
      a.push(parseInt(document.getElementById(`alloc_${i}_${j}`).value||0));
      m.push(parseInt(document.getElementById(`max_${i}_${j}`).value||0));
    }
    allocation.push(a); request.push(m);
  }
  for(let j=0;j<r;j++) available.push(parseInt(document.getElementById(`avail_${j}`).value||0));
  return {processes:p, resources:r, allocation, request, available};
}

function predictDeadlock(){
  const data = collectData();
  fetch('/predict',{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)})
  .then(r=>r.json()).then(res=>{
    document.getElementById('safeSeq').innerText = 'Safe Sequence: ' + (res.safe? res.sequence.map(i=>`P${i+1}`).join(', ') : 'n/a');
    document.getElementById('deadlockInfo').innerText = 'Deadlocked: ' + (res.deadlocked.length? res.deadlocked.map(i=>`P${i+1}`).join(', ') : 'None');
    document.getElementById('resolveBtn').disabled = !(res.deadlocked && res.deadlocked.length>0);
    drawGraph(res.graph, res.deadlocked);
  }).catch(e=>console.error(e));
}

function resolveDeadlock(){
  const data = collectData();
  fetch('/resolve',{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)})
  .then(r=>r.json()).then(res=>{
    document.getElementById('resolveOutput').innerText = res.explanation || 'No explanation provided.';
    document.getElementById('safeSeq').innerText = 'Safe Sequence: ' + (res.final_sequence && res.final_sequence.length? res.final_sequence.map(i=>`P${i+1}`).join(' -> ') : 'None');
    document.getElementById('deadlockInfo').innerText = 'Deadlocked: ' + (res.deadlocked.length? res.deadlocked.map(i=>`P${i+1}`).join(', ') : 'None');
    drawGraph(res.graph, res.deadlocked, res.highlight_killed || []);
  }).catch(e=>console.error(e));
}

function drawGraph(graphData, deadlocked=[], killed=[]){
  const container = document.getElementById('graph');
  container.innerHTML='';
  const nodes = new vis.DataSet(graphData.nodes.map(n=>{
    const o = Object.assign({}, n);
    // style per group
    if(n.group==='process'){
      o.shape='box'; o.color={background:'#73a7ff', border:'#1b5fde'}; o.font={color:'#000'};
    } else {
      o.shape='dot'; o.size=35; o.color={background:'#b2ffb8', border:'#37b34a'}; o.font={color:'#000'};
    }
    return o;
  }));
  const edges = new vis.DataSet(graphData.edges.map(e=>Object.assign({}, e)));
  const options = {
    physics:{enabled:false},
    nodes:{fixed:{x:true,y:true}},
    edges:{smooth:{type:'continuous'}, arrows:{to:{enabled:true, scaleFactor:0.5}}},
    interaction:{hover:true},
    layout:{improvedLayout:false}
  };
  new vis.Network(container, {nodes, edges}, options);
}

function refreshGraph(){ location.reload(); }
function downloadGraph(){ alert('Use OS screenshot or right-click to save the graph image'); }

// init
generateTables();
