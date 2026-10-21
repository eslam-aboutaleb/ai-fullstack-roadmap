"""Fail on shallow edits to existing chapter interview answers.

Compare a PR/push revision with a *pinned git base commit*. Structure and
citation presence are checked here; external reference accuracy and SME
approval remain independent review tasks.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parent.parent
QUESTION_PATH=re.compile(r"^content/chapters/[a-z0-9-]+/questions(?:-[a-z0-9-]+)?\.json$")
PLACEHOLDERS=("lorem ipsum","todo: write","tbd answer","as an ai language model")


def inspect_revisions(before,after,slug):
    original={row["Q"]:row for row in before}
    failures=[];verified=0
    for row in after:
        prior=original.get(row.get("Q"))
        if not prior:
            continue  # Added IDs are handled by the separate new-question gate.
        # Recheck every changed answer, including legacy IDs at or below 1211.
        if prior.get("A")==row.get("A") and prior.get("follow_ups")==row.get("follow_ups") and prior.get("citations")==row.get("citations"):
            continue
        verified+=1
        prefix=f"{slug}/{row['Q'][:65]}"
        answer=row.get("A")
        if not isinstance(answer,str) or len(answer.strip())<350:
            failures.append(prefix+": revised answer is too short (<350 characters)")
        elif any(term in answer.casefold() for term in PLACEHOLDERS):
            failures.append(prefix+": placeholder text in revised answer")
        citations=row.get("citations") or []
        if not isinstance(citations,list) or not citations or any(
            not isinstance(url,str) or urlsplit(url).scheme!="https" or not urlsplit(url).netloc
            for url in citations
        ):
            failures.append(prefix+": revised answer needs explicit HTTPS primary references")
        followups=row.get("follow_ups")
        if not isinstance(followups,list) or not any(isinstance(f,dict)
            and len(str(f.get("Q","")).strip())>=12
            and len(str(f.get("A","")).strip())>=60 for f in followups):
            failures.append(prefix+": revised answer needs an independently answered follow-up")
        review=row.get("reviewer_status",{})
        if not isinstance(review,dict) or review.get("status") not in ("draft","reviewed","approved"):
            failures.append(prefix+": revised answer must explicitly declare draft/reviewed/approved status")
        elif review["status"] in ("reviewed","approved"):
            # No self-attested approvals: a content-digest-matched attestation
            # is required by editorial.validate_review.
            try:
                from editorial import validate_review
                validate_review(row,"interview/"+slug+"/"+row["Q"])
            except ValueError as exc:
                failures.append(prefix+": invalid independent editorial proof: "+str(exc))
    return verified,failures


def _git(*args,check=True):
    return subprocess.run(["git",*args],cwd=ROOT,text=True,capture_output=True,check=check)


def validate_changed_git_records(base):
    if not base or base.startswith("-") or not re.fullmatch(r"[A-Za-z0-9_./-]+",base):
        raise ValueError("trusted git base revision required")
    # Explicit base SHA/ref is supplied by the GitHub Actions event. No
    # network or PR API is used by the content test itself.
    changed=_git("diff","--name-only",base,"HEAD","--","content/chapters").stdout.splitlines()
    count=0;issues=[]
    for path in changed:
        if not QUESTION_PATH.fullmatch(path):
            continue
        previous=_git("show",f"{base}:{path}",check=False)
        if previous.returncode!=0:
            continue # New study records are covered by new-ID validators.
        original=json.loads(previous.stdout)
        current=json.loads((ROOT/path).read_text())
        slug=Path(path).parent.name
        n,problems=inspect_revisions(original,current,slug)
        count+=n;issues+=problems
    if issues:raise ValueError("Revised existing-answer quality gate failed:\n"+"\n".join(issues[:80]))
    return count


def check_fixtures():
    old={"Q":"Why isolate a tenant?","A":"Short answer."}
    new={**old,"A":"**Mechanism.** "+("Scoped retrieval checks owner eligibility before ranking, cites exact source revisions and rejects cross-tenant data. "*5),
         "citations":["https://docs.python.org/3/library/asyncio-task.html"],
         "follow_ups":[{"Q":"What if the owner is revoked between retrieval and citation?",
                        "A":"Recheck ACL/owner access at citation resolution and reject the stale result; revision-scoped cache invalidation prevents replay."}],
         "reviewer_status":{"status":"draft","reviewer":"Independent review pending"}}
    count,errors=inspect_revisions([old],[new],"security")
    assert count==1 and not errors,errors
    for bad in ({**new,"A":"tiny"}, {**new,"citations":[]}, {**new,"follow_ups":[]},
                {**new,"reviewer_status":{"status":"approved","reviewer":"none"}}):
        n,errors=inspect_revisions([old],[bad],"security")
        assert n==1 and errors,bad
    # Changing unrelated, non-answer metadata does not pretend to be an
    # independently approved substantive revision.
    assert inspect_revisions([old],[{**old,"Try":"explain it"}],"security")== (0,[])
    print("Revised legacy answer gate: valid draft, missing sources, shallow answer, follow-up and forged approval PASS")


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base",help="Git base commit/ref to compare with HEAD")
    args=p.parse_args()
    check_fixtures()
    if args.base:print(json.dumps({"checked_revised_interview_questions":validate_changed_git_records(args.base)}))
