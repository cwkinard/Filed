#!/usr/bin/python

import time

from ghost import Ghost
ghost = Ghost()

with ghost.start(wait_timeout=10, download_images=True) as session:
	print 'opening page'
	#page, extra_resources = session.open("https://investor.vanguard.com/home/")
	page, extra_resources = session.open("https://personal.vanguard.com/us/hnwnesc/nesc/LoginPage?TYPE=33554433&REALMOID=06-ab51763e-ad80-45e0-859b-b9381dc0b154&GUID=0&SMAUTHREASON=0&METHOD=GET&SMAGENTNAME=personalprd01&TARGET=$SM$%2fus%2fMyHome")

	assert page.http_status == 200

	print 'setting username and pass'
	result, resources = session.set_field_value("input[id='LoginForm:USER']", "")
	result, resources = session.set_field_value("input[id='LoginForm:PASSWORD']", "")

	print 'clicking signin'
	session.evaluate("document.getElementById('LoginForm:submitInput').click();", expect_loading=True)

	#file_ = open('session.html', 'w')
	#file_.write(session.content.encode('utf-8'))
	#file_.close()	

	assert page.http_status == 200 and 'Security question' in session.content

	#text, resources = session.evaluate("tr[index=1] td:nth-child(2)", expect_loading=False)
	text, resources = session.evaluate("document.getElementsByClassName('noTopBorder')[3].innerHTML", expect_loading=False)

	answer = raw_input(text)

	result, resources = session.set_field_value("input[id='LoginForm:ANSWER']", answer)
	session.evaluate("document.getElementById('LoginForm:DEVICE:1').click();", expect_loading=False)

	session.capture_to("prelogin.png")

	print 'clicking continue...'
	session.evaluate("document.getElementById('LoginForm:ContinueInput').click();", expect_loading=False)

	time.sleep(5)
	session.capture_to("postlogin.png")

	assert page.http_status == 200 and 'wilsonkinard@gmail.com' in session.content
	print 'logged in'
	
	#session.exit()
