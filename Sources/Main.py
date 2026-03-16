import sys
import os
import json
import argparse
from datetime import datetime
from typing import Dict, List
from strutil import StrDecode, PatternScan
from luarun import LuaRunner


class Pipeline:
    def __init__(self):
        self.decoder = StrDecode()
        self.scanner = PatternScan()
        self.runner = LuaRunner()
        self.started = datetime.now()

    def analyze(self, path: str, mode: str = "full") -> Dict:
        res = {
            'file': path,
            'mode': mode,
            'strings': None,
            'patterns': None,
            'exec': None,
        }

        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            src = f.read()

        if mode in ("strings", "full"):
            res['strings'] = self.decoder.scan(path)

        if mode in ("patterns", "full"):
            res['patterns'] = self.scanner.run(src)

        if mode in ("execute", "full"):
            res['exec'] = self.runner.process(path)

        return res

    def summary(self, results: List[Dict]) -> Dict:
        total_str = 0
        total_pat = 0

        for r in results:
            if r.get('strings'):
                total_str += len(r['strings'].get('strings', []))
            if r.get('patterns'):
                total_pat += len(r['patterns'])

        return {
            'files': len(results),
            'strings': total_str,
            'patterns': total_pat,
            'elapsed': str(datetime.now() - self.started),
        }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--mode", choices=["strings", "patterns", "execute", "full"], default="full")
    ap.add_argument("--output")
    args = ap.parse_args()

    pipe = Pipeline()
    targets = []

    if os.path.isfile(args.input):
        targets.append(args.input)
    elif os.path.isdir(args.input):
        for root, _, files in os.walk(args.input):
            for f in files:
                if f.endswith('.lua'):
                    targets.append(os.path.join(root, f))

    print(f"found {len(targets)} file(s)")

    all_res = []
    for t in targets:
        print(f"-> {t}")
        all_res.append(pipe.analyze(t, args.mode))

    sm = pipe.summary(all_res)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump({'summary': sm, 'results': all_res}, f, indent=2, ensure_ascii=False)
        print(f"saved: {args.output}")

    print(f"done in {sm['elapsed']} | {sm['files']} files | {sm['strings']} strings | {sm['patterns']} patterns")


if __name__ == "__main__":
    main()
