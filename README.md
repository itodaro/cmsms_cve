###Cms Made Simple Multiple Vulnerability

####General description：

**[1]CMS Made Simple (CMSMS) 2.2.7 contains the privilege escalation vulnerability from ordinary user to admin user**

**[2]CMS Made Simple (CMSMS) <=2.2.7 "module import" operation in the admin dashboard contains remote code execution vulnerabilities(admin user)**

**[3]CMS Made Simple (CMSMS) <=2.2.7 "file unpack" operation in the admin dashboard contains remote code execution vulnerability(admin user)**

**[4]CMS Made Simple (CMSMS) <=2.2.7 "file view" operation in the admin dashboard contains sensitive information disclose vulnerability(ordinary user)**

**[5]CMS Made Simple (CMSMS) <=2.2.7 "file rename" operation in the admin dashboard contains sensitive information disclose vulnerability that can cause DOS(admin user)**

**[6]CMS Made Simple (CMSMS) <=2.2.7 "module remove" operation in the admin dashboard contains arbitrary file deletion vulnerability that can cause DOS(admin user)**

**[7]CMS Made Simple (CMSMS) <=2.2.7 "file delete" operation in the admin dashboard contains arbitrary file deletion vulnerability that can cause DOS(admin user)**

**[8]CMS Made Simple (CMSMS) <=2.2.7 "file move" operation in the admin dashboard contains arbitrary file movement vulnerability that can cause DOS(admin user)**

**[9]CMS Made Simple (CMSMS) <=2.2.7 contains web Site physical path leakage Vulnerability**

_ _ _

**Environment: **
apache/php 7.0.12/cms made simple 2.2.6 and cms made simple 2.2.7


_ _ _

**[1]The privilege escalation from ordinary user to admin user (2.2.7)**

The previous CVE(http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-10084) existed in cmsms version <=2.2.6,and the authentication method was updated in the latest 2.2.7 version.
However, there is still a privilege escalation vulnerability from ordinary user to admin user.

Call the check_login function in line 35 of /admin/index.php

![1.png](./img/1.png)

In \lib\page.functions.php, line 88 calls the get_userid function

![2.png](./img/2.png)

In \lib\page.functions.php, line 43 calls the get_effective_uid function

![3.png](./img/3.png)

In \lib\classes\internal\class.LoginOperations.php, line 183 calls the _get_data function

![4.png](./img/4.png)

On line 182, if the data exists and both eff_uid and eff_uid exist in the data, the value of eff_uid is returned (**problem 1**).

**(The following is the function updated in version 2.2.7)**

In the _get_data function of \lib\classes\internal\class.LoginOperations.php

![5.png](./img/5.png)

Line 106 gets data from ```$_COOKIE[$this->_loginkey]```

```$this->_loginkey``` comes from ```sha1( CMS_VERSION.$this->_get_salt() );```

The admin dashboard users can get the value in the cookie after logging in, and can also be guessed directly

```CMS_VERSION``` -->2.2.7 (fixed value)

get_salt function is as follows

![6.png](./img/6.png)

Line 51 calls \cms_siteprefs::get(\_\_CLASS\_\_) to get the value of ```$salt```

\_\_CLASS\_\_ is a fixed value: CMSMS\LoginOperations

In the \cms_siteprefs::get function of \lib\classes\class.cms_siteprefs.php

![7.png](./img/7.png)

Line 86 calls the global_cache::get function, the current \_\_CLASS\_\_ is a fixed value: cms_siteprefs

In the global_cache::get function of \lib\classes\internal\class.global_cache.php

![8.png](./img/8.png)

Line 23 calls the _load function
In the _load function

![9.png](./img/9.png)

Line 76 calls the get function of \lib\classes\class.cms_filecache_driver.php

![10.png](./img/10.png)

Line 146 calls the _get_filename function to get the name of the last cached file

Line 147 reads the value of the cache file through the _read_cache_file function

![11.png](./img/11.png)

You can see that the parameters that make up the cache file name are both fixed and guessable (**problem 2**)

And the files in the /tmp/ directory are all directly accessible via the web (**problem 3**)

And the value read from the cache file is also the encrypted value to be used later in the data tamper verification.
So we can get this value by guessing the file name and then reading the cache file directly.

Back to _get_data function

![12.png](./img/12.png)

Line 115 gets the value in the cookie and is divided into ```part0::part1```

Line 118 checks the data to prevent data from being tampered with

If the value of ```part0``` is not equal to ```sha1 ($salt.part1)``` cmsms will not continue to execute the code

We already mentioned that this ```$salt``` value can be obtained, so we can bypass this check

The line 119 performs base64decode processing on the ```part1``` value and then processes it with json_decode (<2.2.7 version uses unserialize function, which also leads to the PHP object injection vulnerability).

![13.png](./img/13.png)

Line 128 also checks the ``` hash``` in the data. This value is related to the user's password, so we need to have a ordinary user account in the admin dashboard.

To sum up: the key to exploiting the vulnerability is to falsify the ```eff_uid``` value in ```$_COOKIE[$this->_loginkey]``` to 1 (the admin user's id), and then bypass the data's anti-counterfeiting verification.

Exploits: I wrote a vulnerability verification script. simply fill in the relevant parameters and you can let the admin dashboard ordinary users upgrade to the admin user.

python cmsms_2_2_7_poc.py

![14.png](./img/14.png)

Using browser to open /admin/index.php will jump to /admin/login.php

Emptying cookies

Then add the cookie generated by the POC
```
8624fce6d211b248d0ec7f93c4797b3ad80e8308
-->4a81ada13ba84ebaa0956bb1b287d333a605d424::eyJ1c2VybmFtZSI6ICJhZG1pbiIsICJlZmZfdWlkIjogMSwgImVmZl91c2VybmFtZSI6IG51bGwsICJ1aWQiOiAyLCAiaGFzaCI6ICIkMnkkMTAkL3d0c2poZ2ZmM25kOG5oWkIxdGVsTzdJZFFKR1o2L0htLnZjQy56aE8xTE01bko1Z1FMOHUifQ==

__c
-->512919d4312874cba5d
```


![15.png](./img/15.png)


![16.png](./img/16.png)

Then revisit /admin/index.php

![17.png](./img/17.png)

Successfully become a admin user!

Vulnerability fix recommendations: Modify the user authentication logic and also restrict the direct access to the tmp directory.

**[2]CMS Made Simple (CMSMS) <=2.2.7 "module import" operation in the admin dashboard contains remote code execution vulnerabilities(admin user)**

In \modules\ModuleManager\action.local_import.php

![18.png](./img/18.png)

Line 23 calls the ExpandXMLPackage function of \lib\classes\class.moduleoperations.inc.php

This function will call xml to read the contents of the file

![19.png](./img/19.png)

This function reads the value of <file><filename> as the file name
Read the value of <file><data> as the contents of the file
Then generate the file

To sum up: the whole process, CMSMS does not restrict the file type in the process of generating files, resulting in hackers can generate executable .PHP files.

Exploits:
Create a test.xml first

![20.png](./img/20.png)

Enter

![21.png](./img/21.png)

Click on "Import Module" operation and select test.xml
Visit /modules/test/test.php after submitting

![22.png](./img/22.png)

Vulnerability fix recommendations: This may be a function rather than a vulnerability for developers. But from the website security point of view, I still recommend that developers should modify this function: after all the module code is uploaded to the server via FTP(rather than by importing xml and automatically generating a file), the admin can choose to install the module.The consideration for this is that the admin is sure to have permission to upload code via FTP, but the hackers do not, so the security of the website is guaranteed.

**[3]CMS Made Simple (CMSMS) <=2.2.7 "file unpack" operation in the admin dashboard contains remote code execution vulnerability(admin user)**

In the \modules\FileManager\action.fileaction.php file

![23.png](./img/23.png)

Enter the decompression process when there is a m1_fileactionunpack parameter or its value is unpack.

Call \modules\FileManager\action.unpack.php

![24.png](./img/24.png)

Line 25 gets the name of the file to extract

Line 35 calls the extract function of class EasyArchive

In the extract function of \modules\FileManager\easyarchives\EasyArchive.class.php

![25.png](./img/25.png)

Line 165 determines that the file is a zip archive
Line 168 decompresses the file directly

To sum up: you can see that the file in the compressed package is not judged in the whole process, so if the .php file is included in the compressed package, it will be released to the server directory after the decompression, causing the code to execute!

Exploits:
Prepare a test.php file first

Content is ```<?php phpinfo();?>```

Compress it into test.zip

![26.png](./img/26.png)

Enter

![27.png](./img/27.png)

Upload test.zip file

Select test.zip and select "Unpack" operation

![28.png](./img/28.png)

Will generate test.php in the current directory

![29.png](./img/29.png)

Access the file, the php file is executed

![31.png](./img/31.png)

Vulnerability fix recommendations: when decompressing a file, determine the file type and limit the .php file to be uncompressed to the server.

**[4]CMS Made Simple (CMSMS) <=2.2.7 "file view" operation in the admin dashboard contains sensitive information disclose vulnerability(ordinary user)**

In \modules\FileManager\action.view.php

![32.png](./img/32.png)

Line 12 gets the value of file and handles it with the base64decode function

Line 13 gets the absolute address of the file

Line 14 determines that the file exists

![33.png](./img/33.png)

Line 30 gets the contents of the file

To sum up: the whole process, after obtaining the file name submitted by the user, CMSMS only carries out the identification of the file existence, does not restrict the directory, and does not judge whether the user is the admin,so any ordinary user in the admin dashboard can read any file content of the website.

Exploits:
Use admin dashboard ordinary user test1 to log in

Then request the following URL (replace the value of __c with your own value, base64decode('Li5cY29uZmlnLnBocA==') is ..\config.php)
```
/admin/moduleinterface.php?mact=FileManager,m1_,view,0&__c=b3d2a517e18bf23a60b&m1_ajax=1&showtemplate=false&m1_file=Li5cY29uZmlnLnBocA==
```

Click "view-source" to see the contents of /config.php

![34.png](./img/34.png)

**[5]CMS Made Simple (CMSMS) <=2.2.7 "file rename" operation in the admin dashboard contains sensitive information disclose vulnerability that can cause DOS(admin user)**

In \modules\FileManager\action.fileaction.php

![35.png](./img/35.png)

Enter the file rename process when m1_fileactionrename parameter exists or its value is rename.

Call \modules\FileManager\action.rename.php

![36.png](./img/36.png)

Line 31 verifies the new file name and cannot contain characters such as .., /, \\, php to prevent .php file generation.

Line 40 gets the file name to be renamed, and ```$oldname``` comes from line 26

![37.png](./img/37.png)

```$oldname``` is handled by the decodefilename function, but this function simply performs a base64decode on the characters without any filtering

To sum up: hackers can move /config.php across directories to the /upload/ directory, causing websites to be inaccessible(DOS) and sensitive database information disclose.

Exploits:
Enter

![38.png](./img/38.png)

Just select a file, click on the "Rename" operation, and then use burp to grab packets

![39.png](./img/39.png)

Modify the value of ```&m1_selall[]``` to ```Li4vY29uZmlnLnBocA==```
Add ```&m1_newname=test```

![40.png](./img/40.png)

Then submit the request

/config.php has been moved to the /upload/ directory and renamed test

![41.png](./img/41.png)

And the site cannot be accessed(DOS) because it lacks the config.php configuration file

![42.png](./img/42.png)

**[6]CMS Made Simple (CMSMS) <=2.2.7 "module remove" operation in the admin dashboard contains arbitrary file deletion vulnerability that can cause DOS(admin user)**

In \modules\ModuleManager\action.local_remove.php

![43.png](./img/43.png)

Line 11 get the absolute address of the directory to delete

Line 13 calls recursive_delete function for recursive file deletion

![44.png](./img/44.png)

To sum up: hackers can delete /lib/ all files across directories, causing websites to be inaccessible(DOS).

Exploits:
Enter

![45.png](./img/45.png)

Just select a module, click on the "Remove" operation, and then use burp to grab packets

![46.png](./img/46.png)

Modify ```m1_mod``` to ```..\test``` to delete all files under /test/ (the directories and files are created for testing)

![47.png](./img/47.png)

**[7]CMS Made Simple (CMSMS) <=2.2.7 "file delete" operation in the admin dashboard contains arbitrary file deletion vulnerability that can cause DOS(admin user)**

In \modules\FileManager\action.fileaction.php

![48.png](./img/48.png)

Enter the file deletion process when there is a m1_fileactiondelete parameter or its value is delete.

Call \modules\FileManager\action.delete.php

![49.png](./img/49.png)

Line 17 gets the file name and calls the base64decode function to decode

![50.png](./img/50.png)

Line 29 gets the absolute address of the file

![51.png](./img/51.png)

Line 30 determines if the file exists

Line 32 determines whether the file is writable

Lines 37-43 determine that it is a directory and the directory is not empty

![52.png](./img/52.png)

Line 57 deletes the file

To sum up: the whole process, after getting the file name submitted by the user, CMSMS will use base64decode function to decode it, and then only judge the existence of the file and the file can be written,the hacker can delete arbitrary files and cause dos.

Exploits:
Enter

![53.png](./img/53.png)

![54.png](./img/54.png)

Just select a file, click on the "Delete" operation, and then use burp to grab packets

![55.png](./img/55.png)

Add ```&m1_submit=submit```

Modify ```m1_selall[]``` to ```Li5cbGliXHRlc3QucGhw```

Submit the request, the \lib\test.php(files created for testing) file will be deleted

**[8]CMS Made Simple (CMSMS) <=2.2.7 "file move" operation in the admin dashboard contains arbitrary file movement vulnerability that can cause DOS(admin user)**

In \modules\FileManager\action.fileaction.php

![56.png](./img/56.png)

Enter the file move process when there is a m1_fileactionmove parameter or its value is move.

Call \modules\FileManager\action.move.php

![57.png](./img/57.png)

![58.png](./img/58.png)

Get the file name processed by the base64decode function

![59.png](./img/59.png)

![60.png](./img/60.png)

Get the destination directory and determine the file write permissions

![61.png](./img/61.png)

Judging the source file exists and the source file is readable

![62.png](./img/62.png)

Line 85 directly renames the file

To sum up: the whole process, after getting the file name submitted by the user, CMSMS will use base64decode function to decode it, and then only judge the existence of the file and the file readable,hackers can move /config.php to other directories resulting in website DOS.

Exploits:
Enter

![53.png](./img/53.png)

Just select a file, click on the "Move" operation, and then use burp to grab packets

![63.png](./img/63.png)

Modify ```m1_selall=``` to ```m1_selall[]=Li5cY29uZmlnLnBocA==```

```m1_destdir=/NCleanBlue```

Submit the request, /config.php becomes /upload/config.php

Request /index.php and display it as follows

![64.png](./img/64.png)

**[9]CMS Made Simple (CMSMS) <=2.2.7 contains web Site physical path leakage Vulnerability**

the following links can get the absolute path to the site

/modules/DesignManager/action.ajax_get_templates.php

![65.png](./img/65.png)

/modules/DesignManager/action.ajax_get_stylesheets.php

![66.png](./img/66.png)

/modules/FileManager/dunzip.php

![67.png](./img/67.png)

/modules/FileManager/untgz.php

![68.png](./img/68.png)


