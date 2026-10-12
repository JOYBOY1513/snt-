import os
from pathlib import Path
os.environ['SNT_DB']='/tmp/snt-test.db'
try:Path(os.environ['SNT_DB']).unlink()
except FileNotFoundError:pass
from backend.app import app
client=app.test_client()
def test_health():
 r=client.get('/api/health');assert r.status_code==200 and r.json['service']=='SNT API'
def test_auth_scan_history_logout():
 r=client.post('/api/auth/register',json={'name':'Asha Rao','email':'asha@example.com','password':'safe-pass-123'});assert r.status_code==200
 r=client.post('/api/scan',json={'kind':'message','text':'You are guaranteed a job. Pay a $99 registration fee immediately and share your OTP.'});assert r.status_code==200;d=r.json;assert d['risk_score']>=80 and d['category']=='Critical Risk';assert d['warning_signs']
 r=client.get('/api/scans');assert r.status_code==200 and len(r.json)==1
 r=client.post('/api/auth/logout');assert r.status_code==200
 assert client.get('/api/scans').status_code==401
def test_login_and_profile():
 r=client.post('/api/auth/login',json={'email':'asha@example.com','password':'safe-pass-123'});assert r.status_code==200
 r=client.put('/api/profile',json={'name':'Asha Verma','theme':'light'});assert r.status_code==200 and r.json['user']['name']=='Asha Verma'
def test_contact_validation():
 assert client.post('/api/contact',json={'name':'A','email':'bad','message':'short'}).status_code==422
 assert client.post('/api/contact',json={'name':'Asha','email':'asha@example.com','message':'This is a valid contact message.'}).status_code==200
