import requests, secrets, math, time, random, json
import plotly.express as px
import pandas as pd
import numpy as np
from tqdm import tqdm
from bs4 import BeautifulSoup
from url_shortener import app, visitor_views
# from .visitor_views import categorise_browser, categorise_os, create_small_bar, create_special_bar, create_small_pie, create_small_line, dashboard_index
from datetime import datetime
from flask import Flask, render_template, request, redirect, make_response, jsonify, flash, session, url_for
from user_agents import parse
from .models import URL, Visitor, page_size

# *********************************************************************************************************************
# Environment variables
# Set page_size to 20
page_size = 20
#
# *********************************************************************************************************************
# ******* Self defined functions **********
# ---------------------------------------------------------------------------------------------------------------------
# Create a function "get_ip_dictionary" with the parameter "ip_address"
def get_ip_dictionary(ip_json):
	ip_dictionary = {}
	city, region, country, coords, isp = "", "", "", "", ""
	if ip_json:
		if "error" not in ip_json:
			ip = ip_json["query"]
			city = ip_json["city"]
			region = ip_json["regionName"]
			country = ip_json["country"]
			coords = f"{ip_json['lat']}, {ip_json['lon']}"
			isp = ip_json["isp"]
		ip_dictionary = {
			"ip": ip,
			"city": city,
			"region": region,
			"country": country,
			"coords": coords,
			"isp": isp,
		}
	return ip_dictionary
#
# ---------------------------------------------------------------------------------------------------------------------
# Create a function "get_user_agent_dictionary" with the parameter "user_agent_string"
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
		machine = "Desktop" if user_agent.is_pc else "Mobile" if user_agent.is_mobile else "Tablet" if user_agent.is_tablet else "Other"
		bot = user_agent.is_bot if user_agent.is_bot else False
		user_agent_dictionary = {
			"bot": bot,
			"os": f"{os} {os_version}",
			"device": f"{device} {brand} {model}".strip(),
			"browser": f"{browser} {browser_version}".strip(),
			"machine": machine,
			"user_agent": user_agent_string,
		}
	return user_agent_dictionary
#
# ---------------------------------------------------------------------------------------------------------------------
# Create a function "progress_bar" to load the progress bar
def progress_bar(wait_time, description):
    for i in tqdm(range(wait_time), desc=description, unit="seconds"):
        time.sleep(1)  
# ---------------------------------------------------------------------------------------------------------------------
# Create a function "load_ip_file" to load ip text file
def load_ip_file():
	ip_list = []
	with open("url_shortener/templates/public/data/ip.txt", "r") as file:
		ip_list = file.read().splitlines()
	return ip_list
#
# ---------------------------------------------------------------------------------------------------------------------
# Create a function "load_user_agent_file" to load user agent text file
def load_user_agent_file():
	user_agent_list = []
	with open("url_shortener/templates/public/data/user_agent.txt", "r") as file:
		user_agent_list = file.read().splitlines()
	return user_agent_list
#
# ---------------------------------------------------------------------------------------------------------------------
# Create a function "figure_lines" to formulate the html of figure lines of the side bar
def figure_lines(figure, suffix_first=None, suffix_second=None, font_icon=None):
	line_break = "<br>" if suffix_second else ""
	second_div_class = "style='margin-top:auto; margin-bottom:auto'" if suffix_second else ""
	figure_html = f"<div><span class='figure'>{figure}</span> <span class='unit'>{suffix_first}</span> {line_break} <span class='unit2'>{ suffix_second }</span></div>\n"
	figure_html += f"<div {second_div_class}><i id='figure-icon' class='{font_icon} fa-2xl'></i></div>"
	return figure_html
#
# ---------------------------------------------------------------------------------------------------------------------
# Create a function "categorise_os" to categorise the os of the DataFrame
#
def categorise_os(os):
	os_list = ["Windows", "Mac OS X", "Linux", "iOS", "Android"]
	for os_one in os_list:
		if os_one.lower() in os.lower():
			return os_one
	return "Others"
#
# ---------------------------------------------------------------------------------------------------------------------
# Create a function "categorise_browser" to categorise the browser of the DataFrame
def categorise_browser(browser):
	browser_list = ["Chrome", "Chromium",
					"Firefox", "Opera", "Safari", "Edge", "IE"]
	for browser_one in browser_list:
		if browser_one.lower() in browser.lower():
			return browser_one
	return "Others"
#
# ---------------------------------------------------------------------------------------------------------------------
# Create a function "create_special_bar" to plot the specific bar - new/return visitors
def create_special_bar(df_data, fig_title, fig_x, fig_y, fig_width, fig_height):
	
	fig = px.bar(df_data, x=fig_x, y=fig_y, color=fig_x)
	for trace in fig.data:
		trace.showlegend = False

	fig.update_layout(
		title=fig_title, 
		width=fig_width, height=fig_height,
		yaxis_title="",
		xaxis_title="",
		margin=dict(l=10, r=10, t=50, b=0),
		xaxis_showgrid=False,
		yaxis_showgrid=False,
		plot_bgcolor='rgba(0,0,0,0)',
		paper_bgcolor='rgba(0,0,0,0)',
	)

	fig.update_yaxes(showticklabels=False)	

	for bar in fig.data:
		bar.text = bar.y
		bar.textposition = "auto"
		bar.hovertemplate = '%{text}'

	return {
		"plot": fig.to_html(full_html=False) if fig else "",
		"width": fig_width,
	}
#
# ---------------------------------------------------------------------------------------------------------------------
# Create a function "create_small_line" to plot the line chart with option of the "shaded area"
def create_small_line(df_data, fig_title, fig_width, fig_x, fig_y, shade=None):
	fig = None
	if shade:
		fig = px.area(df_data, x=fig_x, y=fig_y, text=fig_y)
	else:
		fig = px.line(df_data, x=fig_x, y=fig_y, text=fig_y)

	annotations = []
	for i in range(len(df_data)):
		annotations.append(dict(x=df_data[fig_y][i],
								y=df_data[fig_x][i],
								text=str(df_data[fig_y][i]),
								xanchor='center',
								yanchor='top',
								showarrow=False))

	fig.update_traces(textposition="top center")
	fig.update_layout(
		title=fig_title,
		yaxis_title="",
		xaxis_title="",
		width=fig_width,
		height=fig_width,
		xaxis_showticklabels=False,
		yaxis_showticklabels=False,
		margin=dict(l=10, r=10, t=50, b=10),
		xaxis_showgrid=False,
		yaxis_showgrid=False,
		plot_bgcolor='rgba(0,0,0,0)',
		paper_bgcolor='rgba(0,0,0,0)',
	)

	return {
		"plot": fig.to_html(full_html=False) if fig else "",
		"width": fig_width,
	}
#
# ---------------------------------------------------------------------------------------------------------------------
# Create a function "create_small_pie" to plot the pie chart 
def create_small_pie(df_data, fig_title, fig_values, fig_width):
	
	fig = px.pie(df_data, values=fig_values, names=df_data.index)
	fig.update_layout(
		title=fig_title,
		width=fig_width,
		height=fig_width,
		showlegend=False,
		margin=dict(l=10, r=10, t=50, b=40),
		paper_bgcolor='rgba(0,0,0,0)',
		plot_bgcolor='rgba(0,0,0,0)',
	)

	fig.update_traces(
		textposition='inside', 
		textinfo='percent+label', 
		direction='clockwise'
	)	

	return {
		"plot": fig.to_html(full_html=False) if fig else "",
		"width": fig_width,
	}
#
# ---------------------------------------------------------------------------------------------------------------------
# Create a function "create_small_bar" to plot the bar chart 
def create_small_bar(df_data, fig_title, fig_width, fig_height=None, fig_orientation="h", fig_inside_label=False):

	fig = px.bar(
		df_data,
		x=df_data.values if fig_orientation == "h" else df_data.index,
		y=df_data.index if fig_orientation == "h" else df_data.values,
		color=df_data.index,
		orientation=fig_orientation,
	)

	annotations = []
	inside_label = None

	for i in range(len(df_data)):
		if fig_inside_label:
			inside_label = f'{df_data.index[i]} - {df_data.values[i]}'
		else:
			inside_label = str(df_data.values[i])
		annotations.append(dict(
								x=df_data.values[i] / 2 if fig_orientation == "h" else df_data.index[i] ,
								y=df_data.index[i] if fig_orientation == "h" else df_data.values[i] / 2,
								text=inside_label,
								xanchor='auto',
								yanchor='middle',
								showarrow=False))

	fig.update_layout(
		title=fig_title, 
		width=fig_width, 
		height=fig_height if fig_height else fig_width,
		yaxis_title="",
		xaxis_title="",
		margin=dict(l=10, r=10, t=50, b=10),
		paper_bgcolor='rgba(0,0,0,0)',
		plot_bgcolor='rgba(0,0,0,0)',
		yaxis_showticklabels=False,
		xaxis_showticklabels=False,
		showlegend=False,
		annotations=annotations,
	)

	return {
		"plot": fig.to_html(full_html=False) if fig else "",
		"width": fig_width,
	}
#
# ---------------------------------------------------------------------------------------------------------------------
# Create a function "convert_to_seconds" to convert the timestamp from the DataFrame to second
def convert_to_seconds(timestamp):
	timestamp = str(timestamp).split("days")[1]
	parts = [float(part) for part in str(timestamp).split(":")]
	return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
#
# ---------------------------------------------------------------------------------------------------------------------
# Create a function "create_url_list" to form the list of the dictionary of the DataFrame
def create_df_count_list(df, groupby_cols, count_col, start_index=None, end_index=None):
	df_count_list = []
	df_group = df.groupby(groupby_cols)	
	df_group_count = df_group[count_col].count()
	if start_index is None:
		start_index = 0
	if end_index is None:
		end_index = len(df_group_count)
	for groups, count in df_group_count.items():
		df_dictionary = dict(zip(groupby_cols, groups))
		df_dictionary["count"] = count
		df_count_list.append(df_dictionary)
	return df_count_list
#
# *********************************************************************************************************************
# ********** Routes **********
# ---------------------------------------------------------------------------------------------------------------------
# Route: / - Redirect to dashboard
@app.route("/")
def index():
	return redirect(url_for('dashboard_index'))
#
# ---------------------------------------------------------------------------------------------------------------------
# Route: /search - render "search.html"
@app.route("/search", methods=["GET", "POST"])
def search():
	ip_address, visitors = "", None
	if request.method == "GET":
		return render_template("/public/search.html", ip_address=ip_address, visitors=visitors)
	else:
		ip_address = request.form["ip_address"]
		if ip_address:
			session["ip_address"] = ip_address
			visitors = Visitor.get_url_visitor_by_ip(ip_address, 1, page_size)
		return render_template("/public/search.html", ip_address=ip_address, visitors=visitors, per_page=page_size)
	#
# ---------------------------------------------------------------------------------------------------------------------
# Route: /search - render "search.html"
@app.route("/search/<int:current_page>", methods=["GET"])
def search_page(current_page=1):	
	if "ip_address" in session:
		ip_address = session["ip_address"]		
		visitors = Visitor.get_url_visitor_by_ip(ip_address, current_page, page_size)
		return render_template("/public/search.html", ip_address=ip_address, visitors=visitors, per_page=page_size)
	else:
		return redirect(url_for("search"))

# ---------------------------------------------------------------------------------------------------------------------
# Route: /statistics - Render "statistics.html" with the DataFrame group by "url_short_url", "url_title", "url_description"
#
@app.route("/statistics")
def statistics():	
	df, total = Visitor.visitors_df()
	groupby_cols = ['url_short_url', 'url_title', 'url_description']
	count_col = "visitor_ip"
	df_count_list = create_df_count_list(df, groupby_cols, count_col)
	total_records = len(df_count_list)
	current_page = 1	
	total_pages = math.ceil(len(df_count_list) / page_size)
	start_record = (current_page - 1) * page_size + 1
	end_record = min(start_record + page_size - 1, total_records)
	
	df_data = df_count_list[:end_record]
	pages_dictionary = {
		"current_page": current_page,
		"total_pages": total_pages,
		"start_record": start_record,
		"end_record": end_record,
		"total_records": total_records,
		"page_size": page_size,
	}
	return render_template("public/statistics.html", df_data=df_data, pages=pages_dictionary)
#
# ---------------------------------------------------------------------------------------------------------------------
# Route: /statistics/<int:current_page> - Render "statistics.html" with the DataFrame group by "url_short_url", 
# "url_title", "url_description", with pagination
#
@app.route("/statistics/<int:current_page>")
def statistics_page(current_page=1):
	
	df, total = Visitor.visitors_df()
	groupby_cols = ['url_short_url', 'url_title', 'url_description']
	count_col = "visitor_ip"
	df_count_list = create_df_count_list(df, groupby_cols, count_col)
	total_records = len(df_count_list)
	
	total_pages = math.ceil(len(df_count_list) / page_size)
	start_record = (current_page - 1) * page_size + 1
	end_record = min(start_record + page_size - 1, total_records)	
	df_data = df_count_list[start_record-1:end_record]

	pages_dictionary = {
		"current_page": current_page,
		"total_pages": total_pages,
		"start_record": start_record,
		"end_record": end_record,
		"total_records": total_records,
		"page_size": page_size,
	}

	return render_template("public/statistics.html", df_data=df_data, pages=pages_dictionary)
#
# ---------------------------------------------------------------------------------------------------------------------
# Route: /contact - Render "contact.html"
@app.route("/contact")
def contact():
	return render_template("/public/contact.html")
#
# ---------------------------------------------------------------------------------------------------------------------
# Route: /info/<string:short_url> - Render "detail.html" with "url_info, "referrer", "visitor_data", "plots"
@app.route("/info/<string:short_url>")
def detail(short_url):
	df, total = Visitor.visitors_df()
	# df = pd.read_csv("url_visitor.csv", index_col=0)
	# Select the Dataframe with "url_short_url"
	df_short_url = df[df["url_short_url"] == short_url]	
	# Select the sub-DataFrame with the columns url_short_url', 'url_long_url', 'url_title', 'url_description', 
	# 'url_created_date', 'visitor_ip', 'visitor_visited_date', 'visitor_city', 'visitor_country', 'visitor_machine', 
	# 'visitor_os', 'visitor_browser'
	
	new_df = df_short_url.loc[:, ['url_short_url', 'url_long_url', 'url_title', 'url_description', 'url_created_date', 'visitor_ip', 'visitor_visited_date', 'visitor_city', 'visitor_country', 'visitor_machine', 'visitor_os', 'visitor_browser']]
	new_df.loc[:, 'url_created_date'] = pd.to_datetime(new_df['url_created_date'])
	new_df.loc[:, 'visitor_visited_date'] = pd.to_datetime(new_df['visitor_visited_date'])

	# Plot -  Number of first/return visitors
	visitor_ip_all = new_df.groupby(["visitor_ip"])
	visitor_ip_once = visitor_ip_all.filter(lambda x: len(x) == 1)
	visitor_ip_return = len(visitor_ip_all) - len(visitor_ip_once)
	visitor_new_return = [len(visitor_ip_once), visitor_ip_return]
	# Form the DataFrame for number of first/return visitors
	df_visitor_new_return = pd.DataFrame({
		"visitor_type": ["New", "Return"],
		"count": visitor_new_return,
	})
	visitor_new_return_title = "Visitors by User Type"
	visitor_new_return_x = "visitor_type"
	visitor_new_return_y = "count"
	visitor_new_return_width = 220
	visitor_new_return_height = 200
	visitor_new_return_plot = create_special_bar(df_visitor_new_return, visitor_new_return_title, visitor_new_return_x, visitor_new_return_y, visitor_new_return_width, visitor_new_return_height)
	
	# Plot - Countries that Visitors are from	
	country_groupby = new_df.groupby("visitor_country")
	df_country = country_groupby["visitor_ip"].nunique()
	visitor_countries = df_country.sort_values(ascending=False).head()
	country_data = visitor_countries
	country_title = "Top 5 Countries that Visitors are from"
	country_values = "visitor_ip"
	country_width = 400
	country_plot = create_small_pie(country_data, country_title, country_values, country_width)

	# Plot - Visits by Weeks of Year
	df['week'] = pd.to_datetime(new_df['visitor_visited_date']).dt.to_period("W").astype(str)
	df_week = df.groupby(["week"])
	week_count_data = df_week.size().reset_index(name="count_per_week")
	week_count_width = 400
	week_count_x = "week"
	week_count_y = "count_per_week"
	week_count_title = "Visits by Weeks of Year"
	week_count_plot = create_small_line(week_count_data, week_count_title, week_count_width, week_count_x, week_count_y, True)

	# Plot - Machine used by the visitors
	machine_width = 300 
	machine_title = "Machine"
	machine_orientation = "v"
	machine_group = new_df.groupby(["visitor_machine"])
	machine_data = machine_group.count()["visitor_ip"].sort_values(ascending=False)		
	machine_plot = create_small_bar(machine_data, machine_title, machine_width, fig_orientation=machine_orientation)

	# Plot - OS used by the visitors
	df["os_category"] = new_df["visitor_os"].apply(lambda x: categorise_os(x))
	os_group = df.groupby(["os_category"])
	os_data = os_group["visitor_os"].count().sort_values(ascending=False).head()
	os_title = "OS"
	os_width = 300
	os_orientation = "v"
	os_plot = create_small_bar(os_data, os_title, os_width, fig_orientation=os_orientation)

	# Plot - Browser used by the visitors
	df["browser_category"] = new_df["visitor_browser"].apply(lambda x: categorise_browser(x))
	browser_group = df.groupby(["browser_category"])	
	browser_data = browser_group["visitor_browser"].count().sort_values(ascending=False).head()
	browser_title = "Browser"
	browser_width = 300
	browser_orientation = "v"
	browser_plot = create_small_bar(browser_data, browser_title, browser_width, fig_orientation=browser_orientation)

	# Set "url_info" dictionary to store the figures: "short_url", "long_url", "title", "description", "created_date", "number_of_visitors"
	url_info = {
		"short_url": new_df['url_short_url'].values[0],
		"long_url": new_df['url_long_url'].values[0],
		"title": new_df['url_title'].values[0],
		"description":  new_df['url_description'].values[0],
		"created_date": new_df['url_created_date'].values[0],
		"number_of_visitors": len(new_df), 
	}

	# Set "plots" dictionary to store the plots: "visitor_new_return_plot", "country_plot", "week_count_plot", "machine_plot", 
	# "os_plot", "browser_plot"
	plots = {
		"visitor_new_return_plot": visitor_new_return_plot,
		"country_plot": country_plot,
		"week_count_plot": week_count_plot,
		"machine_plot": machine_plot,
		"os_plot": os_plot,
		"browser_plot": browser_plot,
	}

	# Set the referrer to store the referrer link for backward
	referrer = request.referrer if request.referrer else request.url
	return render_template("public/detail.html", referrer=referrer, url_info=url_info, plots=plots)
#
# ---------------------------------------------------------------------------------------------------------------------
# Route: /redirect - render "redirect.html" with "url_short_url"
@app.route("/redirect/<string:short_url>")
def redirect_short(short_url):
	headers = {'Accept': 'application/json'	}
	base_url = "http://ip-api.com/json"
	query = f"fields=status,message,country,regionName,city,lat,lon,isp,asname,query"
	ip_dictionary, user_agent_dictionary, visitor_dictionary = {}, {}, {}
	count = 0
	# ip_address = request.remote_addr
	# Check the validity of ip address
	response = requests.get(base_url, headers=headers)
	ip_data = response.json()

	if ip_data["status"] == "success":
		ip_dictionary = get_ip_dictionary(ip_data)
		user_agent_string = request.user_agent.string
		user_agent_dictionary = get_user_agent_dictionary(user_agent_string)
	else:
		ip_list = load_ip_file()
		ip_index = random.randrange(len(ip_list))
		fake_ip = ip_list[ip_index]
		query_url = f"{base_url}/{fake_ip}?{query}"
		response = requests.get(query_url, headers=headers)
		ip_data = response.json()
		ip_dictionary = get_ip_dictionary(ip_data)
		user_agent_list = load_user_agent_file()	
		user_agent_index = random.randrange(len(user_agent_list))
		user_agent_string = user_agent_list[user_agent_index]
		user_agent_dictionary = get_user_agent_dictionary(user_agent_string)
		user_agent_dictionary["bot"] = True

	visitor_dictionary = {**ip_dictionary, **user_agent_dictionary}
	url = URL.find_by_short_url(short_url)
	if url:
		visitor_dictionary["url_id"] = url.url_id
		count = Visitor.add_visitor(**visitor_dictionary)
	return render_template("/public/redirect.html", url=url, visitor=visitor_dictionary)
#
# ---------------------------------------------------------------------------------------------------------------------
# Route: /lists - render "lists.html" with "urls", "short"
@app.route("/lists")
def lists():
	short = secrets.token_hex(3)
	urls  = URL.all_url_pages(1, page_size)
	total_records = len(URL.all_url())
	current_page = 1

	total_pages = math.ceil(total_records / page_size)
	start_record = (current_page - 1) * page_size + 1
	end_record = min(start_record + page_size - 1, total_records)

	pages_dictionary = {
		"current_page": current_page,
		"total_pages": total_pages,
		"start_record": start_record,
		"end_record": end_record,
		"total_records": total_records,
		"page_size": page_size,
	}
	print(pages_dictionary)

	return render_template("public/lists.html", urls=urls, short=short, pages=pages_dictionary)
#
# ---------------------------------------------------------------------------------------------------------------------
# Route: /lists/<int:current_page> - render "lists.html" with "urls", "short"
@app.route("/lists/<int:current_page>")
def lists_page(current_page=None):
	short = secrets.token_hex(3)
	urls  = URL.all_url_pages(current_page, page_size)
	total_records = len(URL.all_url())
	total_pages = math.ceil(total_records / page_size)
	start_record = (current_page - 1) * page_size + 1
	end_record = min(start_record + page_size - 1, total_records)

	pages_dictionary = {
		"current_page": current_page,
		"total_pages": total_pages,
		"start_record": start_record,
		"end_record": end_record,
		"total_records": total_records,
		"page_size": page_size,
	}
	print(pages_dictionary)
	return render_template("public/lists.html", urls=urls, short=short, pages=pages_dictionary)

#
# ---------------------------------------------------------------------------------------------------------------------
# Route: /dashboard - display the overview of short urls - Statistics and Charts
@app.route("/dashboard")
def dashboard_index():
	df, total = Visitor.visitors_df()
	# df = pd.read_csv("url_visitor.csv")

	machine_width, os_width, browser_width = 0, 0, 0
	row_width_first, row_width_second, row_width_third = 400, 400, 250
	row_orientation_third = "v"

	week_count_plot, bounce_count_plot, short_url_plot = None, None, None
	machine_plot, os_plot, browser_plot = None, None, None
	country_fig, machine_fig, os_fig, browser_fig = None, None, None, None

	# Figures
	# 1. No of visitors (group visitors visit on the same date), 
	# #regardless their countries,
	country_cols = ["visitor_country", "visitor_ip", "url_short_url"]
	country = df.groupby(country_cols)
	visitor_count = f"{len(country['visitor_id'].count()):,}"

	# 2. Average time they stay in the page
	# No of visitors visits more than one -> Average Session Time
	# Filter visitors who visit only once per day
	df['visitor_visited_date'] = pd.to_datetime(df['visitor_visited_date'])
	df_filtered = df.groupby(['visitor_ip', df['visitor_visited_date'].dt.date]).filter(lambda x: len(x) > 1)
	# Calculate the difference between max and min visitor_visited_date
	df_filtered['visit_duration'] = df_filtered.groupby(['visitor_ip', df_filtered['visitor_visited_date'].dt.date])['visitor_visited_date'].transform('max') - df_filtered.groupby(['visitor_ip', df_filtered['visitor_visited_date'].dt.date])['visitor_visited_date'].transform('min')
	visitor_duration = df_filtered['visit_duration'].mean()
	visitor_duration_seconds = convert_to_seconds(visitor_duration)

	# 3. No. of page views per visitor on average (Average Page View)
	df_ip = df.groupby(["visitor_ip", "url_id"])
	visitor_average_page_view = round(df_ip["visitor_ip"].count().mean(), 2)

	# 4. bounce rate (overall) of this month
	visitor_ip_all = df.groupby(["visitor_ip"])
	visitor_ip_once = visitor_ip_all.filter(lambda x: len(x) == 1)
	bounce_rate_one = round(visitor_ip_once.shape[0] / len(visitor_ip_all["visitor_ip"]) * 100, 2)

	# 5. total number of pages views
	total_pages_view = f"{df['visitor_ip'].count():,}"

	figures = {
		"visitor_count": f"{figure_lines(visitor_count, '', 'Visits', 'fa-regular fa-user')}",
		"visitor_duration_seconds": f"{figure_lines(visitor_duration_seconds, 'sec', 'Avg Session Time', 'fa-regular fa-clock')}",
		"visitor_average_page_view": f"{figure_lines(visitor_average_page_view, 'pages', 'Per Visit', 'fa-regular fa-eye')}",
		"bounce_rate": f"{figure_lines(bounce_rate_one, '', 'Bounce Rate', 'fa-solid fa-forward-fast')}",
		"total_pages_view": f"{figure_lines(total_pages_view, '', 'Page Views', 'fa-regular fa-file-lines')}",
	}

	# 6 New return 
	visitor_ip_all = df.groupby(["visitor_ip"])
	visitor_ip_once = visitor_ip_all.filter(lambda x: len(x) == 1)
	visitor_ip_return = len(visitor_ip_all) - len(visitor_ip_once)
	visitor_new_return = [len(visitor_ip_once), visitor_ip_return]
	df_visitor_new_return = pd.DataFrame({
		"visitor_type": ["New", "Return"],
		"count": visitor_new_return,
	})
	visitor_new_return_title = "Visitors by User Type"
	visitor_new_return_x = "visitor_type"
	visitor_new_return_y = "count"
	visitor_new_return_width = 220
	visitor_new_return_height = 200
	visitor_new_return_plot = create_special_bar(df_visitor_new_return, visitor_new_return_title, visitor_new_return_x, visitor_new_return_y, visitor_new_return_width, visitor_new_return_height)

	# 7: Week Visit
	df['week'] = pd.to_datetime(df['visitor_visited_date']).dt.to_period("W").astype(str)
	df_week = df.groupby(["week"])
	week_count_data = df_week.size().reset_index(name="count_per_week")
	week_count_width = row_width_first
	week_count_x = "week"
	week_count_y = "count_per_week"
	week_count_title = "Visits by Weeks of Year"
	week_count_plot = create_small_line(week_count_data, week_count_title, week_count_width, week_count_x, week_count_y, True)

	# 8: bounce rate
	total_per_week = df_week["url_id"].count()
	bounce_per_week = df_week.apply(lambda x: x[x["url_id"].duplicated() == False].shape[0])
	bounce_rate = pd.concat([total_per_week, bounce_per_week], axis=1)
	bounce_rate.columns = ["total_per_week", "bounce_per_week"]
	bounce_rate["bounce_rate"] = bounce_rate["bounce_per_week"] / bounce_rate["total_per_week"] * 100
	bounce_rate_data = round(bounce_rate["bounce_rate"], 2)
	bounce_rate_data = bounce_rate_data.reset_index()
	bounce_rate_width = row_width_first
	bounce_count_x = "week"
	bounce_count_y = "bounce_rate"
	bounce_count_title = "Bounce Rate by Weeks of Year"
	bounce_count_plot = create_small_line(bounce_rate_data, bounce_count_title, bounce_rate_width, bounce_count_x, bounce_count_y, False)

	# 9: country
	country_title = "Top 5 Countries that Visitors are from"
	country_values = "visitor_ip"
	country_width = row_width_second
	country_group = df.groupby(["visitor_country"])["visitor_ip"]
	country_data = country_group.count().sort_values(ascending=False)
	country_data_top4 = country_data[:5]
	country_plot = create_small_pie(country_data_top4, country_title, country_values, country_width)

	# 10. most visited short url
	short_url_fig = None
	short_url_width = row_width_second
	short_url_height = row_width_second
	short_url_title = "Top 3 Favourite URLs"
	short_url_plot = {
		"plot": short_url_fig,
		"width": short_url_width,
	}
	short_url_group = df.groupby(["url_title"])
	short_url_data = short_url_group.count()["url_id"].head().sort_values(ascending=False)	
	short_url_data_top3 = short_url_data[:3]
	short_url_plot = create_small_bar(short_url_data_top3, short_url_title, short_url_width, fig_height=short_url_height, fig_orientation="h", fig_inside_label=True)

	# 11. Machine
	machine_fig = None
	machine_width = row_width_third 
	machine_title = "Machine"
	machine_plot = {
		"plot": machine_fig,
		"width": machine_width,
	}
	machine_group = df.groupby(["visitor_machine"])
	machine_data = machine_group.count()["visitor_ip"].sort_values(ascending=False)		
	machine_plot = create_small_bar(machine_data, machine_title, machine_width, fig_orientation=row_orientation_third)

	# 12. OS
	os_width = row_width_third 
	os_title = "OS"
	os_plot = {
		"plot": os_fig,
		"width": os_width,
	}
	df["os_category"] = df["visitor_os"].apply(lambda x: categorise_os(x))
	os_group = df.groupby(["os_category"])
	os_data = os_group["visitor_os"].count().sort_values(ascending=False).head()
	os_plot = create_small_bar(os_data, os_title, os_width, fig_orientation=row_orientation_third)

	# 13. browser type
	browser_width = row_width_third 
	browser_title = "Browser"
	browser_plot = {
		"plot": browser_fig,
		"width": browser_width,
	}
	df["browser_category"] = df["visitor_browser"].apply(lambda x: categorise_browser(x))
	browser_group = df.groupby(["browser_category"])
	browser_data = browser_group["visitor_browser"].count().sort_values(ascending=False).head()
	browser_plot = create_small_bar(browser_data, browser_title, browser_width, fig_orientation=row_orientation_third)

	# Set "plots" dictionary to store the plots: "week_count", "bounce_count", "country", "short_url", "machine", "os", "browser"
	plots = {
		"week_count": week_count_plot,
		"bounce_count": bounce_count_plot,
		"country": country_plot,
		"short_url": short_url_plot,
		"machine": machine_plot,
		"os": os_plot,		
		"browser": browser_plot,
	}

	# Set "special_plots" dictionary to store the plot: "visitor_new_return"
	special_plots = {
		"visitor_new_return": visitor_new_return_plot,
	}
	
	# Set "div_list" to store the list of the div of the plots
	div_list  = [ ["week_count", "bounce_count"], ["country", "short_url"], ["machine", "os", "browser"]]

	return render_template("/public/dashboard.html", plot=plots, special_plot=special_plots, figure=figures, divs=div_list)
#
# ---------------------------------------------------------------------------------------------------------------------
# Route: /shorten - render "index.html" with "urls", "short"
@app.route("/shorten", methods=["POST"])
def shorten():
	short = secrets.token_hex(3)
	row_count, message = 0, ""
	urls = None
	mode = request.form["mode"]
	url_list = ["short_url", "long_url", "title", "description"]
	url_dictionary = {}
	for key, value in request.form.items():
		if key in url_list:
			url_dictionary[key] = value

	if mode == "add": 
		if url_dictionary:
			row_count = URL.add_url(**url_dictionary)
			if row_count:
				message = f"The URL #{url_dictionary['short_url']} is created successfully."
			else:
				message = f"Fail to create shorten url."
			flash(message)
		# urls = URL.all_url()
		urls  = URL.all_url_pages(1)
		return render_template("public/lists.html", urls=urls, short=short)
	elif mode == "edit":		
		url_id = None
		row_affected = 0
		if "url_id" in request.form:
			url_id = request.form["url_id"]
			url_dictionary["id"] = url_id
			row_affected = URL.update_by_id(**url_dictionary)
			message = f"The URL #{url_dictionary['short_url']} is updated successfully. [{row_affected}]"
			flash(message)
			return redirect(request.referrer)	
		else:
			message = f"No id for url is found."
			flash(message)
			return redirect(url_for('lists'))
	elif mode == "delete":
		url_id = None
		row_affected = 0
		if "url_id" in request.form:
			url_id = request.form["url_id"]
			url_dictionary["id"] = url_id
			row_affected = URL.delete_by_id(url_id)
			message = f"The URL #{url_dictionary['short_url']} is deleted successfully. [{row_affected}]"
			flash(message)
			return redirect(url_for('lists'))
		else:
			message = f"No id for url is found."
			flash(message)
			return redirect(url_for('lists'))
	else:
		return redirect(url_for('lists'))
#
# *********************************************************************************************************************
# Filter: datetime - convert the datetime to string format "%Y-%m-%d %H:%M:%S"
@app.template_filter()
def date_string(dt):
	# Convert "numpy" datetime object to "datetime" object and return string object
	if isinstance(dt, np.datetime64):
		unix_epoch = np.datetime64(0, "s")
		one_second = np.timedelta64(1, "s")
		seconds_since_epoch = (dt - unix_epoch) / one_second
		new_datetime = datetime.utcfromtimestamp(seconds_since_epoch) 
		return new_datetime.strftime("%Y-%m-%d %H:%M:%S")
	# Convert "datetime" object to string object
	elif isinstance(dt, datetime):
		return dt.strftime("%Y-%m-%d %H:%M:%S")
	else:
		return str(dt)
#
# ---------------------------------------------------------------------------------------------------------------------
# Filter: sub_text - slice the string with the range (start, end)
# 
@app.template_filter()
def sub_text(text, start, end):
	output_text = ""
	if text:
		if len(text) < end:
			return text
		else:
			output_text = f"{text[start: end+1]} ..."
	return output_text
#
# ---------------------------------------------------------------------------------------------------------------------
# Filter: os_filter - convert OS of user-agent to os type
# 
@app.template_filter()
def os_filter(os):
	return categorise_os(os)
#
# ---------------------------------------------------------------------------------------------------------------------
# Filter: browser_filter - convert Browser of user-agent to browser type
# 
@app.template_filter()
def browser_filter(browser):
	return categorise_browser(browser)