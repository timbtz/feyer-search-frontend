"""Refresh the committed, sanitized dashboard snapshot from the read-only API."""
import argparse
import datetime
import hashlib
import json
import math
from pathlib import Path
import re
from urllib.parse import urlsplit
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 32 * 1024 * 1024
PRIVATE = re.compile(r'-----BEGIN [^-]*PRIVATE KEY-----.*?(?:-----END [^-]*PRIVATE KEY-----|$)', re.S)
SECRET = re.compile(r'\b(?:rc-[\da-fA-F]{24,}|gh[pousr]_[\w]{20,}|github_pat_[\w]{20,}|sk-[\w-]{20,})\b|(?i:Bearer\s+\S+)')
KEY = re.compile(r'^(?:api[_-]?key|authorization|password|access_token|refresh_token|claim_token|actor_token|role_token|token|token_hash|capability|secret|credentials?)$', re.I)


def sanitize(value):
    if isinstance(value, dict):
        return {k:sanitize(v) for k,v in value.items() if not KEY.match(k) and k not in ('raw_messages','transcript','transcripts')}
    if isinstance(value, list):return [sanitize(v) for v in value]
    if isinstance(value, str):
        value=PRIVATE.sub('[private key redacted]',value)
        value=SECRET.sub('[credential redacted]',value)
        return re.sub(r'(?im)^.*\b(?:api[_-]?key|authorization|password|access_token|refresh_token|claim_token|actor_token|role_token|token|capability|secret)\s*[:=].*$', '[credential line redacted]',value)
    if isinstance(value,float) and not math.isfinite(value):return None
    return value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    source=parser.add_mutually_exclusive_group()
    source.add_argument('--api-url',default=None,help='Read-only dashboard origin; defaults to http://127.0.0.1:8765')
    source.add_argument('--input',type=Path,help='Already exported local snapshot')
    parser.add_argument('--output',type=Path,default=ROOT/'data/latest.json')
    args=parser.parse_args()
    if args.input:
        with args.input.open('rb') as stream:raw=stream.read(LIMIT+1)
    else:
        origin=args.api_url or 'http://127.0.0.1:8765';url=urlsplit(origin)
        if url.scheme not in ('http','https') or not url.hostname or url.username or url.password or url.path not in ('','/') or url.query or url.fragment:
            parser.error('--api-url must be an HTTP(S) origin without credentials or path')
        with urlopen(origin.rstrip('/')+'/api/state',timeout=30) as response:raw=response.read(LIMIT+1)
    if len(raw)>LIMIT:raise ValueError('Snapshot exceeds 32 MB')
    data=json.loads(raw)
    if not isinstance(data,dict) or not isinstance(data.get('campaigns'),list):raise ValueError('Missing campaign array')
    if data.get('demo'):raise ValueError('Refusing to replace real evidence with synthetic demo data')
    if not data.get('submission',{}).get('candidates'):raise ValueError('Submission dossier missing; update the observatory first')
    data=sanitize(data);data['snapshot']=True
    data['snapshot_export']={'captured_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope':'Saved read-only observation. Includes bounded sanitized evaluator logs; excludes raw conversations and credentials.',
        'refresh_command':'npm run refresh:data'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    encoded=(json.dumps(data,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n').encode()
    temporary=args.output.with_suffix('.tmp');temporary.write_bytes(encoded);temporary.replace(args.output)
    manifest={'captured_at_utc':data['snapshot_export']['captured_at_utc'],'generated_at':data.get('generated_at'),
        'sha256':hashlib.sha256(encoded).hexdigest(),'bytes':len(encoded),'jobs':len(data.get('jobs',[])),
        'profiles':len(data.get('profiler_reports',[])),'candidates':[c['sha'] for c in data['submission']['candidates']],
        'selection_status':data['submission'].get('selection_status')}
    args.output.with_name('manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest))


if __name__=='__main__':main()
