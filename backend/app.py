from __future__ import annotations
import os, re, secrets, sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse
from flask import Flask, jsonify, request, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash

ROOT=Path(__file__).resolve().parents[1]; DB=Path(os.getenv('SNT_DB',ROOT/'snt.db')); DIST=ROOT/'frontend'/'dist'
app=Flask(__name__, static_folder=str(DIST), static_url_path='')
app.secret_key=os.getenv('SNT_SECRET','snt-dev-secret-change-me')
app.config.update(SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE='Lax',SESSION_COOKIE_SECURE=bool(os.getenv('SNT_PUBLIC_PREVIEW')))

def conn():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def init_db():
 c=conn(); c.executescript('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password TEXT NOT NULL,theme TEXT DEFAULT 'system',created_at TEXT DEFAULT CURRENT_TIMESTAMP); CREATE TABLE IF NOT EXISTS scans(id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL,kind TEXT NOT NULL,subject TEXT NOT NULL,result TEXT NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP); CREATE TABLE IF NOT EXISTS contacts(id INTEGER PRIMARY KEY,name TEXT NOT NULL,email TEXT NOT NULL,message TEXT NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP);'''); c.commit(); c.close()
init_db()

def current_user():
 uid=session.get('uid')
 if not uid:return None
 c=conn(); u=c.execute('SELECT id,name,email,theme,created_at FROM users WHERE id=?',(uid,)).fetchone(); c.close(); return dict(u) if u else None

def auth():
 u=current_user()
 if not u:return jsonify({'error':'Authentication required'}),401
 return u

def analyze(text,kind='message'):
 t=(text or '')[:20000]; low=t.lower(); score=0; signs=[]; evidence=[]; checks=['payment demand rules','compensation and urgency rules','sensitive-data request rules','recruiter language rules']
 rules=[('fee',r'\b(registration|interview|training|processing|security|activation|equipment)\s+(fee|charge|payment)|pay\s+(?:a|the)?\s*(fee|money)',28,'Fee requested before employment','critical'),('salary',r'(?:\$|usd\s*)\s?\d{2,3},?\d{3}|\b\d{2,3}k\s+(?:per|a)\s+(?:week|day)',18,'Unrealistic compensation promise','high'),('urgency',r'\b(urgent|immediately|act\s+now|today only|within\s+24|limited\s+time|last chance)\b',16,'Pressure to act before verification','medium'),('sensitive',r'\b(otp|one[- ]time password|password|passport|ssn|social security|bank(?:ing)? details|card number|crypto wallet)\b',24,'Sensitive credential or financial data requested','critical'),('guarantee',r'\b(guaranteed|100%\s+selected|no\s+interview|you\s+are\s+hired|instant\s+joining)\b',18,'Hiring process is presented as guaranteed','high'),('contact',r'\b(telegram|whatsapp only|gmail\.com|outlook\.com|kindly)\b',10,'Recruiter contact pattern is difficult to verify','medium'),('language',r'\b(congradulations|recieve|plese|benifit|dear candidate)\b',7,'Unusual recruitment language detected','low')]
 for code,pat,w,msg,sev in rules:
  m=re.search(pat,low)
  if m:
   score+=w; signs.append({'code':code,'severity':sev,'message':msg}); evidence.append(t[max(0,m.start()-45):m.end()+85].strip())
 if kind=='url' or re.match(r'https?://',t.strip()):
  checks.append('URL structure and transport rules'); p=urlparse(t.strip()); host=(p.hostname or '').lower()
  if p.scheme!='https': score+=15; signs.append({'code':'http','severity':'high','message':'Link does not use encrypted HTTPS'}); evidence.append(t.strip())
  if host.startswith('xn--') or any(x in host for x in ('.tk','.top','.click','.work')): score+=20; signs.append({'code':'domain','severity':'critical','message':'Domain has a risky or lookalike pattern'}); evidence.append(host)
  if host.count('-')>=3 or len(host)>45: score+=8; signs.append({'code':'structure','severity':'medium','message':'Domain structure deserves independent verification'}); evidence.append(host)
 score=min(score,100); category='Critical Risk' if score>=80 else 'High Risk' if score>=60 else 'Medium Risk' if score>=30 else 'Low Risk'
 return {'risk_score':score,'category':category,'warning_signs':signs,'evidence':evidence[:6],'recommendations':['Never pay to access a job, interview, or training.','Verify the company using contact details found independently.','Do not share OTPs, passwords, banking details, or identity documents.','Use the employer\'s official careers page instead of unsolicited links.'],'checks_performed':checks,'limitations':['Automated results are estimates and cannot guarantee whether an offer is genuine or fraudulent.','External reputation databases are not connected in this local deployment.'],'rule_version':'snt-rules-1.0'}

def need_user():
 u=auth()
 return u if isinstance(u,dict) else None

@app.get('/api/health')
def health():return jsonify({'status':'ok','service':'SNT API','database':'sqlite','rule_version':'snt-rules-1.0'})
@app.post('/api/auth/register')
def register():
 d=request.get_json(silent=True) or {}; name=str(d.get('name','')).strip(); email=str(d.get('email','')).strip().lower(); password=str(d.get('password',''))
 if len(name)<2 or not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+',email) or len(password)<8:return jsonify({'error':'Name, valid email, and password of 8+ characters are required'}),422
 c=conn()
 try:c.execute('INSERT INTO users(name,email,password) VALUES(?,?,?)',(name,email,generate_password_hash(password))); c.commit(); uid=c.execute('SELECT id FROM users WHERE email=?',(email,)).fetchone()['id']
 except sqlite3.IntegrityError:return jsonify({'error':'An account with that email already exists'}),409
 finally:c.close()
 session['uid']=uid; return jsonify({'user':current_user()})
@app.post('/api/auth/login')
def login():
 d=request.get_json(silent=True) or {}; email=str(d.get('email','')).strip().lower(); password=str(d.get('password','')); c=conn(); u=c.execute('SELECT * FROM users WHERE email=?',(email,)).fetchone(); c.close()
 if not u or not check_password_hash(u['password'],password):return jsonify({'error':'Invalid email or password'}),401
 session['uid']=u['id']; return jsonify({'user':current_user()})
@app.post('/api/auth/logout')
def logout():session.clear(); return jsonify({'ok':True})
@app.get('/api/me')
def me():return jsonify({'user':current_user()})
@app.put('/api/profile')
def profile():
 u=need_user()
 if not u:return jsonify({'error':'Authentication required'}),401
 d=request.get_json(silent=True) or {}; name=str(d.get('name','')).strip()
 if len(name)<2:return jsonify({'error':'Name is required'}),422
 c=conn(); c.execute('UPDATE users SET name=?,theme=? WHERE id=?',(name,str(d.get('theme','system')),u['id'])); c.commit(); c.close(); return jsonify({'user':current_user()})
@app.post('/api/scan')
def scan():
 u=need_user()
 if not u:return jsonify({'error':'Authentication required'}),401
 d=request.get_json(silent=True) or {}; text=str(d.get('text','')).strip(); kind=str(d.get('kind','message'))
 if len(text)<3 or len(text)>20000:return jsonify({'error':'Enter between 3 and 20,000 characters'}),422
 result=analyze(text,kind); import json; c=conn(); cur=c.execute('INSERT INTO scans(user_id,kind,subject,result) VALUES(?,?,?,?)',(u['id'],kind,text[:240],json.dumps(result))); c.commit(); scan_id=cur.lastrowid; c.close(); result['scan_id']=scan_id; return jsonify(result)
@app.get('/api/scans')
def scans():
 u=need_user()
 if not u:return jsonify({'error':'Authentication required'}),401
 import json; c=conn(); rows=c.execute('SELECT id,kind,subject,result,created_at FROM scans WHERE user_id=? ORDER BY id DESC',(u['id'],)).fetchall(); c.close(); return jsonify([{'id':r['id'],'kind':r['kind'],'subject':r['subject'],'created_at':r['created_at'],'result':json.loads(r['result'])} for r in rows])
@app.post('/api/contact')
def contact():
 d=request.get_json(silent=True) or {}; name=str(d.get('name','')).strip(); email=str(d.get('email','')).strip(); message=str(d.get('message','')).strip()
 if len(name)<2 or not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+',email) or len(message)<10:return jsonify({'error':'Please provide a valid name, email, and message'}),422
 c=conn(); c.execute('INSERT INTO contacts(name,email,message) VALUES(?,?,?)',(name,email,message)); c.commit(); c.close(); return jsonify({'ok':True,'message':'Thanks — your message was received.'})

@app.route('/',defaults={'path':''})
@app.route('/<path:path>')
def frontend(path):
 if path.startswith('api/'):return jsonify({'error':'Not found'}),404
 if DIST.exists() and (DIST/path).is_file():return send_from_directory(DIST,path)
 if (DIST/'index.html').exists():return send_from_directory(DIST,'index.html')
 return 'Run npm run build first, then start Flask.',503
if __name__=='__main__':app.run(host='0.0.0.0',port=int(os.getenv('PORT','5000')),debug=False)
