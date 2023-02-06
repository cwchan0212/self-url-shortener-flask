import requests, secrets, random, json, time
import plotly.express as px
import pandas as pd

from url_shortener import app
from datetime import datetime
from flask import Flask, render_template, request, redirect, make_response, jsonify, flash, session, url_for
from user_agents import parse
from .models import URL, Visitor

# https://www.browserling.com/tools/random-ip
# https://developers.whatismybrowser.com/useragents/database/

# ---------------------------------------------------------------------------------------------------------------------
@app.route("/links", methods=["GET"])
def links_index():
	urls = URL.all_url() 
	return render_template("/public/links.html", urls=urls)

# ---------------------------------------------------------------------------------------------------------------------
@app.route("/links/<string:short_url>", methods=["GET"])
def links_clicked(short_url):
	url = URL.find_by_short_url(short_url)
	visitor_dictionary = {}
	if url:
		headers = {
			'Accept': 'application/json',
			}
		baseURL = "https://ipapi.co"
		format = "json"
		# ip = request.remote_addr
		ip = "77.100.117.248"	
		ipapi_url = f"{baseURL}/{ip}/{format}" 		
		while True:
			response = requests.get(ipapi_url, headers=headers)
			if "Sorry, you have been blocked" in response.text:
				print("Website is blocked, waiting for 5 seconds")
				time.sleep(5)
			else:
				ip_data = response.json()
				# print(ip_data)
				ip_dictionary = get_ip_dictionary(ip_data)
				user_agent_string = request.user_agent.string
				user_agent_dictionary = get_user_agent_dictionary(user_agent_string)
				visitor_dictionary = {**ip_dictionary, **user_agent_dictionary}
				url = URL.find_by_short_url(short_url)
				# print(visitor_dictionary)
				if url:
					visitor_dictionary["url_id"] = url.url_id
					count = Visitor.add_visitor(**visitor_dictionary)
				break
		message = f"#{short_url} is clicked."
		flash(message)
		# urls = URL.all_url()
		return redirect("/links")
	else:
		message = f"No URL id is found."
		return {"message": message}

@app.route("/links/bar/<string:short_url>", methods=["GET"])
def visitor_bar(short_url):
	visitors = Visitor.get_visitor_count_by_country_and_url(short_url)
	x_list, y_list = [], []
	for visitor in visitors:
		x_list.append(visitor.visitor_country)
		y_list.append(visitor.distinct_visitor_ips)

	df = pd.DataFrame({		
		"Country": x_list,
		"Count": y_list
	})
	
	url = URL.find_by_short_url(short_url)

	fig = px.bar(df, x="Country", y="Count", color_discrete_sequence =['blue']*len(df))
	fig.update_layout(title={
		"text": f"Visitor Count by Country - {short_url} clicked<br>",
		"y": 0.9,
		"x": 0.5,
        "xanchor": "center",
        "yanchor": "top"
	},
	margin=dict(t=0, b=0, l=0, r=0)
	)

	return render_template("/public/info.html", visitors=visitors, url=url, plot=fig.to_html(full_html=False))
# ---------------------------------------------------------------------------------------------------------------------

@app.route("/links/pie/<string:short_url>", methods=["GET"])
def visitor_pie(short_url):
	visitors = Visitor.get_visitor_count_by_country_and_url(short_url, True)
	x_list, y_list = [], []

	for visitor in visitors:
		x_list.append(visitor.visitor_country)
		y_list.append(visitor.distinct_visitor_ips)

	df = pd.DataFrame({		
		"Country": x_list,
		"Count": y_list
	})

	print(df)
	url = URL.find_by_short_url(short_url)
	fig = px.pie(df, values="Count", names="Country")
	fig.update_traces(textposition='inside')
	fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide', margin=dict(t=0, b=0, l=0, r=0))

	return render_template("/public/info.html", visitors=visitors, url=url, plot=fig.to_html(full_html=False))

# ---------------------------------------------------------------------------------------------------------------------
# For ip-api pro only
def get_ip_dictionary_april(ip_data):
	ip_dictionary = {}
	city, region, country, coords, isp = "", "", "", "", ""
	if ip_data:
		if "error" not in ip_data:
			ip = ip_data["query"]
			city = ip_data["city"]
			region = ip_data["regionName"]
			country = ip_data["country"]
			coords = f"{ip_data['lat']}, {ip_data['lon']}"
			isp = ip_data["isp"]
		ip_dictionary = {
			"ip": ip,
			"city": city,
			"region": region,
			"country": country,
			"coords": coords,
			"isp": isp,
		}
	return ip_dictionary

# ---------------------------------------------------------------------------------------------------------------------
# For ipapi.com only
def get_ip_dictionary(ip_data):
	ip_dictionary = {}
	city, region, country, coords, isp = "", "", "", "", ""
	if ip_data:
		if "error" not in ip_data:
			ip = ip_data["ip"]
			city = ip_data["city"]
			region = ip_data["region"]
			country = ip_data["country_name"]
			coords = f"{ip_data['latitude']}, {ip_data['longitude']}"
			isp = ip_data["org"]
		ip_dictionary = {
			"ip": ip,
			"city": city,
			"region": region,
			"country": country,
			"coords": coords,
			"isp": isp,
		}
	return ip_dictionary
# ---------------------------------------------------------------------------------------------------------------------
# For ipapi.com only
def get_user_agent_dictionary(user_agent_string):
	user_agent_dictionary = {}
	bot, os, device, browser, machine, user_agent = False, "", "", "", "Other", ""
	if user_agent_string:
		user_agent = parse(user_agent_string)
		# browser
		browser = user_agent.browser.family
		browser_version = user_agent.browser.version_string
		# os
		os = user_agent.os.family
		os_version = user_agent.os.version_string
		# device
		device = user_agent.device.family if user_agent.device.family else ""
		brand = user_agent.device.brand if user_agent.device.brand else ""
		model = user_agent.device.model if user_agent.device.model else ""
		# PC/Table/Mobile/Bot ?
		# if user_agent.is_pc:
		# 	machine = "Desktop"
		# if user_agent.is_mobile:
		# 	machine = "Mobile"
		# if user_agent.is_tablet:
		# 	machine = "Tablet"
		machine = "Desktop" if user_agent.is_pc else "Mobile" if user_agent.is_mobile else "Tablet" if user_agent.is_tablet else "Other"
		bot = user_agent.is_bot if user_agent.is_bot else False
		user_agent_dictionary = {
			"bot": bot,
			"os": f"{os} {os_version}",
			"device" : f"{device} {brand} {model}".strip(),
			"browser": f"{browser} {browser_version}".strip(),
			"machine": machine,
			"user_agent": user_agent_string,
		}
	return user_agent_dictionary
# ---------------------------------------------------------------------------------------------------------------------
# For ipapi.com only
def link_clicked():
	headers = {'Accept': 'application/json'}
	# response = requests.get(request.url, headers=headers)
	# data = response.json()
	# print(response.json())
	baseURL = "https://ipapi.co"
	format = "json"
	ip = request.remote_addr
	ipapi_url = f"{baseURL}/{ip}/{format}" 
	response = requests.get(ipapi_url, headers=headers)
	data = response.json()
	city, region, country, coords, isp = "", "", "", "", ""
	if "error" not in data:
		city = data.city
		region = data.region
		country = data.country_name
		coords = f"{data.latitude}, {data.latitude}"
		isp = data.org
	user_agent = request.user_agent.string
	# user_agent = request.headers.get("User-Agent")
	user_agent = parse(user_agent)
	# browser
	browser = user_agent.browser.family
	browser_version = user_agent.browser.version_string
	# os
	os = user_agent.os.family
	os_version = user_agent.os.version_string
	# device
	device = user_agent.device.family if user_agent.device.family else ""
	brand = user_agent.device.brand if user_agent.device.brand else ""
	model = user_agent.device.model if user_agent.device.model else ""
	# PC/Table/Mobile/Bot ?
	type = ""
	type = "Desktop" if user_agent.is_pc else "Mobile" if user_agent.is_mobile else "Tablet" if user_agent.is_tablet else ""
	bot = user_agent.is_bot if user_agent.is_bot else ""
	data = {        
		"ip": ip,
		"city": city,
		"region": region,
		"country": country,
		"coords": coords,
		"isp": isp,
		"bot": bot,
		"type": type,
		"browser": f"{browser} {browser_version}".strip(),
		"os": f"{os} {os_version}",
		"device" : f"{device} {brand} {model}".strip()
	}
	short = secrets.token_hex(3)
	print(short)
	return data
# @app.route("/<short>")
# def redirect_to(short):
# 	long_url = "http://www.google.com"
# 	return redirect(long_url, code=302)