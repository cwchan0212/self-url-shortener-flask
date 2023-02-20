import requests, secrets, math
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from url_shortener import app, visitor_views
from .visitor_views import categorise_browser, categorise_os, create_small_bar, create_special_bar, create_small_pie, create_small_line, dashboard_index
from datetime import datetime
from flask import Flask, render_template, request, redirect, make_response, jsonify, flash, session, url_for
from user_agents import parse
from .models import URL, Visitor

# *********************************************************************************************************************
# Environment variables
# Set page_size to 20
page_size = 20
#
# *********************************************************************************************************************
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
# Route: /statistics - Render the statistics.html with the dataframe group by "url_short_url", "url_title", "url_description"
#
@app.route("/statistics")
def statistics():	
	df = pd.read_csv("url_visitor.csv")	
	groupby_cols = ['url_short_url', 'url_title', 'url_description']
	count_col = "visitor_ip"
	df_count_list = create_df_count_list(df, groupby_cols, count_col)
	current_page = 1
	total_page = math.ceil(len(df_count_list) / page_size)
	df_count_list = df_count_list[:page_size]
	return render_template("public/statistics.html", df_data=df_count_list, current_page=current_page, total_page=total_page)
# ---------------------------------------------------------------------------------------------------------------------
# Route: /statistics/<int:current_page> - Render the statistics.html with the dataframe group by "url_short_url", "url_title", "url_description" 
# with pagination
#
@app.route("/statistics/<int:current_page>")
def statistics_page(current_page=1):
	df = pd.read_csv("url_visitor.csv")
	groupby_cols = ['url_short_url', 'url_title', 'url_description']
	count_col = "visitor_ip"
	df_count_list = create_df_count_list(df, groupby_cols, count_col)
	total_page = math.ceil(len(df_count_list) / page_size)
	start_index = (current_page - 1) * page_size
	end_index = min(start_index + page_size, len(df_count_list))
	df_count_list = df_count_list[start_index:end_index]
	return render_template("public/statistics.html", df_data=df_count_list, current_page=current_page, total_page=total_page)
# ---------------------------------------------------------------------------------------------------------------------
# Route: /contact - Render contact.html
@app.route("/contact")
def contact():
	return render_template("/public/contact.html")
# ---------------------------------------------------------------------------------------------------------------------
# Route: /info/<string:short_url> - Render detail.html with "url_info, "referrer", "visitor_data", "plots"
@app.route("/info/<string:short_url>")
def detail(short_url):
	df = pd.read_csv("url_visitor.csv", index_col=0)
	df_short_url = df[df["url_short_url"] == short_url]	
	new_df = df_short_url.loc[:, ['url_short_url', 'url_long_url', 'url_title', 'url_description', 'url_created_date', 'visitor_ip', 'visitor_visited_date', 'visitor_city', 'visitor_country', 'visitor_machine', 'visitor_os', 'visitor_browser']]
	new_df.loc[:, 'url_created_date'] = pd.to_datetime(new_df['url_created_date'])
	new_df.loc[:, 'visitor_visited_date'] = pd.to_datetime(new_df['visitor_visited_date'])
	url_info = {
		"short_url": new_df['url_short_url'].values[0],
		"long_url": new_df['url_long_url'].values[0],
		"title": new_df['url_title'].values[0],
		"description":  new_df['url_description'].values[0],
		"created_date": new_df['url_created_date'].values[0],
	}
	visitor_ip_all = df.groupby(["visitor_ip"])
	visitor_ip_once = visitor_ip_all.filter(lambda x: len(x) == 1)
	visitor_ip_return = len(visitor_ip_all) - len(visitor_ip_once)
	visitor_new_return = [len(visitor_ip_once), visitor_ip_return]
	df_visitor_new_return = pd.DataFrame({
		"visitor_type": ["New", "Return"],
		"count": visitor_new_return,
	})
	number_of_visitors = len(new_df)
	new_df['visit_count'] = new_df.groupby(['visitor_ip'])['visitor_visited_date'].transform('count')
	new_df['first_visit_return'] = new_df.groupby(['visitor_ip'])['visitor_visited_date'].transform(lambda x: 'return' if len(x) > 1 else 'first')
	first_visit_return = new_df['first_visit_return'].value_counts()
	visitor_ip_all = new_df.groupby(["visitor_ip"])
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
	df_city = new_df.groupby(["visitor_city"])
	visitor_cities = df_city["visitor_country"].value_counts().sort_values(ascending=False).head()
	country_groupby = new_df.groupby("visitor_country")
	df_country = country_groupby["visitor_ip"].nunique()
	visitor_countries = df_country.sort_values(ascending=False).head()
	country_data = visitor_countries
	country_title = "Top 5 Countries that Visitors are from"
	country_values = "visitor_ip"
	country_width = 400
	country_plot = create_small_pie(country_data, country_title, country_values, country_width)
	today = datetime.now()
	today_string = today.strftime("%Y-%m-%d")
	start_date = pd.to_datetime("2022-10-01")
	end_date = pd.to_datetime(today_string)
	# end_date = pd.to_datetime("2023-01-31")
	weeks = pd.date_range(start_date, end_date, freq="W-SUN")
	df['week'] = pd.to_datetime(new_df['visitor_visited_date']).dt.to_period("W").astype(str)
	df_week = df.groupby(["week"])
	week_count_data = df_week.size().reset_index(name="count_per_week")
	week_count_width = 400
	week_count_x = "week"
	week_count_y = "count_per_week"
	week_count_title = "Visits by Weeks of Year"
	week_count_plot = create_small_line(week_count_data, week_count_title, week_count_width, week_count_x, week_count_y, True)


	machine_width = 300 
	machine_title = "Machine Used"
	machine_orientation = "v"
	machine_group = new_df.groupby(["visitor_machine"])
	machine_data = machine_group.count()["visitor_ip"].sort_values(ascending=False)		
	machine_plot = create_small_bar(machine_data, machine_title, machine_width, fig_orientation=machine_orientation)
	df["os_category"] = new_df["visitor_os"].apply(lambda x: categorise_os(x))
	os_group = df.groupby(["os_category"])
	os_data = os_group["visitor_os"].count().sort_values(ascending=False).head()
	# print(os_group)
	os_title = "OS Used"
	os_width = 300
	os_orientation = "v"
	os_plot = create_small_bar(os_data, os_title, os_width, fig_orientation=os_orientation)
	# df["browser_category"] = new_df["visitor_browser"].apply(lambda x: categorise_browser(x))
	# browser_group = df.groupby(["browser_category"])
	# visitor_browser = browser_group["visitor_browser"].count().sort_values(ascending=False).head()
	# df["os_category"] = new_df["visitor_os"].apply(lambda x: categorise_os(x))
	# os_group = df.groupby(["os_category"])
	# os_data = os_group["visitor_os"].count().sort_values(ascending=False).head()
	df["browser_category"] = new_df["visitor_browser"].apply(lambda x: categorise_browser(x))
	browser_group = df.groupby(["browser_category"])	
	browser_data = browser_group["visitor_browser"].count().sort_values(ascending=False).head()
	browser_title = "Browser Used"
	browser_width = 300
	browser_orientation = "v"
	browser_plot = create_small_bar(browser_data, browser_title, browser_width, fig_orientation=browser_orientation)
	# create on
	# of visit
	# first visit / return
	# city
	# country
	# OS
	# browser
	plots = {
		"visitor_new_return_plot": visitor_new_return_plot,
		"country_plot": country_plot,
		"week_count_plot": week_count_plot,
		"machine_plot": machine_plot,
		"os_plot": os_plot,
		"browser_plot": browser_plot,
	}
	visitor_data = {
		"number_of_visitors": number_of_visitors, 
		"first_visit_return": first_visit_return, 
		# "visitor_city": visitor_cities,
		"visitor_country": visitor_countries,
		# "visitor_os": visitor_os,
		# "visitor_browser": visitor_browser,
	}
	print(f"{request.referrer}\n{request.url}")
	referrer = request.referrer if request.referrer else request.url
	return render_template("public/detail.html", url_info=url_info, referrer=referrer, visitor_data=visitor_data, plots=plots)
# ---------------------------------------------------------------------------------------------------------------------
# Lists
@app.route("/lists")
def lists():
	# messages = f"Hello"
	# flash(messages)
	short = secrets.token_hex(3)
	urls  = URL.all_url_pages(1)
	# urls = URL.all_url()
	return render_template("public/lists.html", urls=urls, short=short)
# ---------------------------------------------------------------------------------------------------------------------
@app.route("/lists/<int:current_page>")
def page(current_page=None):
	short = secrets.token_hex(3)
	urls  = URL.all_url_pages(current_page)
	return render_template("public/lists.html", urls=urls, short=short)
# ---------------------------------------------------------------------------------------------------------------------
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
	print(url_dictionary)
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
		return render_template("public/index.html", urls=urls, short=short)
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
			return redirect("/")
	elif mode == "delete":
		url_id = None
		row_affected = 0
		if "url_id" in request.form:
			url_id = request.form["url_id"]
			url_dictionary["id"] = url_id
			row_affected = URL.delete_by_id(url_id)
			message = f"The URL #{url_dictionary['short_url']} is deleted successfully. [{row_affected}]"
			flash(message)
			return redirect("/")
		else:
			message = f"No id for url is found."
			flash(message)
			return redirect("/")
	else:
		pass
		return redirect("/")
# *********************************************************************************************************************
# Filter: datetime	
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
		# dt_py = dt.astype(datetime)
		# return dt_py.strftime('%Y-%m-%d %H:%M:%S.%f')
# ---------------------------------------------------------------------------------------------------------------------
# Filter: 
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