import os
import sys
import subprocess
import argparse
import json
import re
import requests
import hashlib
from pathlib import Path
from urllib.parse import urlparse

class TWR:
    def __init__(self):
        self.home = Path.home()
        self.wd = self.home / ".twr"
        self.wd.mkdir(exist_ok=True)
        self.out = self.home / "storage/downloads/nowm"
        self.out.mkdir(parents=True, exist_ok=True)
        self.tmp = self.wd / "temp"
        self.tmp.mkdir(exist_ok=True)
        self.check()
    
    def check(self):
        cmds = ['ffmpeg', 'ffprobe', 'yt-dlp']
        for cmd in cmds:
            if subprocess.run(['which', cmd], capture_output=True).returncode != 0:
                print(f"[!] Install: pkg install {cmd}")
                if cmd == 'yt-dlp':
                    print("[!] Or: pip install yt-dlp")
                sys.exit(1)
    
    def extract(self, url):
        cmd = [
            'yt-dlp', '-j', '--no-warnings', url
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            return None
        return json.loads(r.stdout)
    
    def download(self, url):
        data = self.extract(url)
        if not data:
            return None
        
        video_url = None
        for f in data.get('formats', []):
            if f.get('ext') == 'mp4' and not f.get('format_note') == 'watermarked':
                if 'video' in f.get('format', ''):
                    video_url = f.get('url')
                    break
        
        if not video_url:
            return None
        
        vid = data.get('id', hashlib.md5(url.encode()).hexdigest()[:8])
        tmp_path = self.tmp / f"{vid}.mp4"
        
        r = requests.get(video_url, stream=True)
        with open(tmp_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return tmp_path
    
    def info(self, p):
        cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', str(p)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        d = json.loads(r.stdout)
        for s in d['streams']:
            if s['codec_type'] == 'video':
                return {'w': int(s.get('width', 0)), 'h': int(s.get('height', 0))}
        return None
    
    def crop(self, inp, out, pos='br'):
        i = self.info(inp)
        if not i:
            return False
        
        w, h = i['w'], i['h']
        
        if pos == 'br':
            cw, ch = int(w * 0.85), int(h * 0.85)
            x, y = 0, 0
        elif pos == 'bl':
            cw, ch = int(w * 0.85), int(h * 0.85)
            x, y = int(w * 0.15), 0
        elif pos == 'tr':
            cw, ch = int(w * 0.85), int(h * 0.85)
            x, y = 0, int(h * 0.15)
        else:
            cw, ch = int(w * 0.85), int(h * 0.85)
            x, y = int(w * 0.15), int(h * 0.15)
        
        cmd = ['ffmpeg', '-i', str(inp), '-vf', f'crop={cw}:{ch}:{x}:{y}', '-c:a', 'copy', '-preset', 'fast', '-y', str(out)]
        r = subprocess.run(cmd, capture_output=True)
        return r.returncode == 0
    
    def blur(self, inp, out, pos='br'):
        i = self.info(inp)
        if not i:
            return False
        
        w, h = i['w'], i['h']
        
        if pos == 'br':
            x, y = int(w * 0.85), int(h * 0.85)
            bw, bh = int(w * 0.15), int(h * 0.15)
        elif pos == 'bl':
            x, y = 0, int(h * 0.85)
            bw, bh = int(w * 0.15), int(h * 0.15)
        elif pos == 'tr':
            x, y = int(w * 0.85), 0
            bw, bh = int(w * 0.15), int(h * 0.15)
        else:
            x, y = 0, 0
            bw, bh = int(w * 0.15), int(h * 0.15)
        
        vf = f"[0:v]split[orig][wm];[wm]crop={bw}:{bh}:{x}:{y},boxblur=10:5,scale={bw}:{bh}[blurred];[orig]overlay={x}:{y}[outv]"
        cmd = ['ffmpeg', '-i', str(inp), '-filter_complex', vf, '-map', '[outv]', '-map', '0:a?', '-c:a', 'copy', '-preset', 'fast', '-y', str(out)]
        r = subprocess.run(cmd, capture_output=True)
        return r.returncode == 0
    
    def delogo(self, inp, out, pos='br'):
        i = self.info(inp)
        if not i:
            return False
        
        w, h = i['w'], i['h']
        
        if pos == 'br':
            x, y = int(w * 0.85), int(h * 0.85)
            bw, bh = int(w * 0.15), int(h * 0.15)
        elif pos == 'bl':
            x, y = 0, int(h * 0.85)
            bw, bh = int(w * 0.15), int(h * 0.15)
        elif pos == 'tr':
            x, y = int(w * 0.85), 0
            bw, bh = int(w * 0.15), int(h * 0.15)
        else:
            x, y = 0, 0
            bw, bh = int(w * 0.15), int(h * 0.15)
        
        cmd = ['ffmpeg', '-i', str(inp), '-vf', f'delogo=x={x}:y={y}:w={bw}:h={bh}:show=0', '-c:a', 'copy', '-preset', 'fast', '-y', str(out)]
        r = subprocess.run(cmd, capture_output=True)
        return r.returncode == 0
    
    def clean(self):
        for f in self.tmp.glob('*'):
            f.unlink()
    
    def process(self, url, method='delogo', pos='br'):
        print(f"[*] Downloading: {url}")
        tmp = self.download(url)
        
        if not tmp:
            print("[!] Download failed")
            return False
        
        vid = tmp.stem
        out = self.out / f"{vid}_nowm.mp4"
        
        print(f"[*] Removing watermark using {method}")
        
        if method == 'crop':
            ok = self.crop(tmp, out, pos)
        elif method == 'blur':
            ok = self.blur(tmp, out, pos)
        else:
            ok = self.delogo(tmp, out, pos)
        
        if ok:
            print(f"[+] Saved: {out}")
            tmp.unlink()
            return True
        else:
            print("[!] Failed to remove watermark")
            return False

def main():
    p = argparse.ArgumentParser(description='TikTok Watermark Remover')
    p.add_argument('-u', '--url', help='TikTok video URL')
    p.add_argument('-m', '--method', choices=['crop', 'blur', 'delogo'], default='delogo', help='Removal method')
    p.add_argument('-p', '--position', choices=['br', 'bl', 'tr', 'tl'], default='br', help='Watermark position')
    
    args = p.parse_args()
    
    if not args.url:
        p.print_help()
        sys.exit(1)
    
    tw = TWR()
    tw.process(args.url, args.method, args.position)
    tw.clean()

if __name__ == "__main__":imports
