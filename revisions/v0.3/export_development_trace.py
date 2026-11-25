#!/usr/bin/env python3
"""Export genuine public development events; exclude private context, never invent steps."""
import argparse
import collections
import hashlib
import json
import re
from pathlib import Path


def export(source, target, report, start_marker='开始吧，记住我们的目标是拿高分'):
    raw=Path(source).read_bytes();lines=raw.decode('utf-8').splitlines()
    parsed=[];start=None
    for n,line in enumerate(lines,1):
        try:row=json.loads(line)
        except json.JSONDecodeError:continue
        payload=row.get('payload',{})
        if not isinstance(payload,dict):continue
        if row.get('type')=='response_item' and payload.get('type')=='message' and payload.get('role')=='user':
            content=payload.get('content',[])
            texts=[c.get('text','') for c in content if isinstance(c,dict)] if isinstance(content,list) else [str(content)]
            if any(start_marker in t for t in texts):start=n
        parsed.append((n,line,row,payload))
    if start is None:raise ValueError('Explicit development-start user message not found; do not guess the scope')
    relevant=[r for r in parsed if r[0]>=start]
    echo_ids={p.get('call_id') for _,line,r,p in relevant if p.get('type') in {'function_call_output','custom_tool_call_output'} and 'trace_steps' in line and 'dry_run' in line and 'manifest' in line}
    completed={p.get('call_id') for _,_,r,p in relevant if r.get('type')=='response_item' and p.get('type') in {'function_call_output','custom_tool_call_output'}}
    excluded=collections.Counter();kept=[];records=[];redactions=0
    for n,line,row,payload in relevant:
        typ=payload.get('type')
        reason=None
        if row.get('type')!='response_item':reason='non-conversation metadata or duplicate events'
        elif typ=='message' and payload.get('role') not in {'user','assistant','tool'}:reason='private system/developer context'
        elif typ=='reasoning' or (typ=='message' and payload.get('role')=='assistant' and payload.get('channel')=='analysis'):reason='private reasoning event'
        elif typ not in {'message','function_call','function_call_output','custom_tool_call','custom_tool_call_output'}:reason='non-public conversation event'
        elif payload.get('call_id') in echo_ids:reason='recursive dry-run trace echo and paired call; source report stays local'
        elif typ in {'function_call','custom_tool_call'} and payload.get('call_id') not in completed:reason='call not yet completed at export snapshot'
        if reason:
            excluded[reason]+=1
            continue
        cleaned,count=re.subn(r'asp_[A-Za-z0-9]{40,}','<API_TOKEN_REDACTED>',line)
        redactions+=count
        cleaned,count=re.subn(r'(Bearer\s+)[A-Za-z0-9._-]{20,}',r'\1<API_TOKEN_REDACTED>',cleaned,flags=re.I)
        redactions+=count
        for pattern in (r'sk-[A-Za-z0-9_-]{20,}',r'(?:gh[pousr]_|github_pat_)[A-Za-z0-9_]{20,}'):
            cleaned,count=re.subn(pattern,'<API_TOKEN_REDACTED>',cleaned);redactions+=count
        kept.append(cleaned)
        records.append({'original_line':n,'original_sha256':hashlib.sha256(line.encode()).hexdigest(),
                        'export_sha256':hashlib.sha256(cleaned.encode()).hexdigest(),'type':typ,'call_id':payload.get('call_id')})
    if not kept:raise ValueError('No public development events exported')
    data=('\n'.join(kept)+'\n').encode()
    Path(target).parent.mkdir(parents=True,exist_ok=True);Path(target).write_bytes(data)
    audit={'source_name':Path(source).name,'source_snapshot_sha256':hashlib.sha256(raw).hexdigest(),
           'scope':'Actual development events starting at the user approval. Original events retained in original order; no invented messages or tool results.',
           'start_line':start,'start_marker':start_marker,'exported_events':len(kept),'excluded_counts':dict(excluded),
           'token_redactions':redactions,'export_sha256':hashlib.sha256(data).hexdigest(),
           'notice':'Filtered native Codex JSONL export, not an unmodified native file. Exclusion/line mapping is explicit. The original remains private locally.',
           'source_line_map':records}
    Path(report).write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    return {k:v for k,v in audit.items() if k not in {'source_line_map'}}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True);p.add_argument('--out',required=True);p.add_argument('--audit',required=True)
    p.add_argument('--start-marker',default='开始吧，记住我们的目标是拿高分');a=p.parse_args();print(json.dumps(export(a.source,a.out,a.audit,start_marker=a.start_marker),ensure_ascii=True,indent=2))
