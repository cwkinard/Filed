#!/usr/bin/python

from ghost import Ghost
ghost = Ghost()

with ghost.start() as session:
	print 'opening page'
	page, extra_resources = session.open("https://www.chase.com/")
	assert page.http_status == 200

	print 'setting username and pass'
	result, resources = session.set_field_value("input[id=usr_name_home]", "")
	result, resources = session.set_field_value("input[id=usr_password_home]", "")

	#result, resources = session.fill("MAINFORM", {
	#	"txtUser": "",
	#	"txtPassword": ""
	#})
	#page, resources = ghost.call("MAINFORM", "submit", expect_loading=True)

	print 'clicking signin'
	#session.click("a[class=signin--button]")	
	session.evaluate("document.getElementsByClassName('signin--button')[0].click();", expect_loading=True)

	assert page.http_status == 200 and 'CHARLES W KINARD' in page.content

	#session.exit()
	
