const test=require('node:test'),assert=require('node:assert/strict');
const {Verification,Progression,Metrics}=require('../app.js');
test('verification joins exact candidates, preserves pending and failures, and never promotes a run',()=>{
 const sha='a'.repeat(40),r={sha,profile:'full',research_records:[{record_id:'r',candidate_sha:sha,source_ref:'https://example.com/source',verification:{candidate_sha:sha,checks:[{id:'official',setup:'dev-101',method:'official benchmark',status:'passed'},{id:'generalization',setup:'random-3',method:'baseline comparison',status:'failed'},{id:'judge',setup:'withheld',method:'organizer benchmark',status:'pending'}]}}]};
 assert.deepEqual(Verification.checks(r).map(c=>c.status),['passed','failed','pending']);
 assert.equal(Verification.checks(r)[0].source_ref,'https://example.com/source');
 assert.equal(Progression.verdict(r).label,'Unconfirmed');assert.equal(Metrics.reference(r,[],{}).available,false);
 assert.deepEqual(Verification.checks({...r,sha:'b'.repeat(40)}),[]);
 const other=structuredClone(r);other.research_records[0].verification.candidate_sha='c'.repeat(40);assert.deepEqual(Verification.checks(other),[]);
});
