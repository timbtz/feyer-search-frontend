const {test} = require('node:test');
const assert = require('node:assert/strict');
const {build,layout,trace} = require('../app.js');
const fixture = () => ({workers:[{id:'researcher',model:'large-model',status:'complete'}],campaigns:[{id:'one',rounds:[{round_id:'r',spec:{lanes:{small:{owner:'selector',dimensions:['batch']}},dimensions:{batch:[1,2]}}}],candidates:[
 {candidate_id:'a',round_id:'r',lane_id:'small',parents:[],valid:true,kind:'seed'},
 {candidate_id:'b',round_id:'r',lane_id:'small',parents:['a'],valid:true,kind:'mutate'},
 {candidate_id:'c',round_id:'r',lane_id:'small',parents:['a','b'],status:'screened',kind:'combine'},
],guidance:[{guidance_id:'idea',actor:'researcher',payload:{parents:['b'],hypothesis:'Try a new solver'}}],evaluations:[{request_id:'screen',candidate_id:'c',profile:'screen',status:'completed'},{request_id:'full',candidate_id:'c',profile:'full',status:'reserved'}]}]});
test('combination retains all scientific parents and proposal remains unvalidated',()=>{
 const g=build(fixture());const c=g.nodes.find(n=>n.candidate==='c');
 assert.equal(g.edges.filter(e=>e.target===c.id&&!e.grouping).length,2);assert.equal(c.valid,false);
 const guidance=g.nodes.find(n=>n.type==='guidance');assert.match(guidance.status,/Proposal/);assert.ok(!guidance.valid);
 assert.equal(g.edges.filter(e=>e.target===guidance.id&&!e.grouping).length,2);
});
test('tracing follows ancestry and descendants without pulling in unrelated siblings through grouping',()=>{
 const data=fixture();data.campaigns[0].candidates.push({candidate_id:'unrelated',round_id:'r',lane_id:'small',parents:[]});
 const g=build(data),c=g.nodes.find(n=>n.candidate==='c'),ids=trace(g,c.id);
 for(const name of ['a','b','c'])assert.ok(ids.has(g.nodes.find(n=>n.candidate===name).id));
 assert.ok(!ids.has(g.nodes.find(n=>n.candidate==='unrelated').id));assert.ok(!ids.has('root'));
});
test('all evaluations retain identity, screen completion never becomes full validation',()=>{
 const g=build(fixture(),{evaluations:true}),ev=g.nodes.filter(n=>n.type==='evaluation');assert.equal(ev.length,2);
 assert.ok(ev.every(n=>!n.valid));assert.equal(g.edges.filter(e=>ev.some(n=>n.id===e.target)).length,2);
});
test('campaign identifiers isolate duplicate local candidate IDs',()=>{
 const data=fixture();data.campaigns.push({...data.campaigns[0],id:'two'});const g=build(data);
 assert.equal(new Set(g.nodes.map(n=>n.id)).size,g.nodes.length);assert.equal(g.nodes.filter(n=>n.candidate==='a').length,2);
 const scoped=build(data,{campaign:'two'});assert.ok(scoped.nodes.every(n=>!n.campaign||n.campaign==='two'));
});
test('cyclic evidence is reported and unresolved parents remain visible',()=>{
 const data=fixture();data.campaigns[0].candidates[0].parents=['c','missing'];const g=layout(build(data));
 assert.ok(g.warnings.length);assert.ok(g.nodes.some(n=>n.type==='missing'));
 for(const e of g.edges)assert.ok(g.nodes.find(n=>n.id===e.source).x<g.nodes.find(n=>n.id===e.target).x);
});
test('automatic layout keeps nodes apart and every connection moves forward',()=>{
 const g=layout(build(fixture(),{evaluations:true}));
 for(const a of g.nodes)for(const b of g.nodes)if(a.id!==b.id)assert.ok(a.x+a.width<=b.x||b.x+b.width<=a.x||a.y+a.height<=b.y||b.y+b.height<=a.y);
 for(const e of g.edges)assert.ok(g.nodes.find(n=>n.id===e.source).x<g.nodes.find(n=>n.id===e.target).x);
 assert.deepEqual(g,layout(build(fixture(),{evaluations:true})));
});
test('empty evidence has no invented workers, candidates or results',()=>{
 const g=build({});assert.equal(g.nodes.length,1);assert.equal(g.edges.length,0);
});
