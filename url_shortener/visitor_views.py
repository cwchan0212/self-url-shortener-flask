import requests, secrets, time
import plotly.express as px
import pandas as pd

from url_shortener import app
from datetime import datetime
from flask import Flask, render_template, request, redirect, make_response, jsonify, flash, session, url_for
from user_agents import parse
from .models import URL, Visitor

# https://www.browserling.com/tools/random-ip
# https://developers.whatismybrowser.com/useragents/database/


def convert_to_seconds(timestamp):
	timestamp = str(timestamp).split("days")[1]
	parts = [float(part) for part in str(timestamp).split(":")]
	return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])


def categorize_os(os):
	os_list = ["Windows", "Mac OS X", "Linux", "iOS", "Android"]
	for os_one in os_list:
		if os_one.lower() in os.lower():
			return os_one
	return "Others"


def categorize_browser(browser):
	browser_list = ["Chrome", "Chromium",
					"Firefox", "Opera", "Safari", "Edge", "IE"]
	for browser_one in browser_list:
		if browser_one.lower() in browser.lower():
			return browser_one
	return "Others"

# ---------------------------------------------------------------------------------------------------------------------

def create_special_bar(df_data, fig_title, fig_x, fig_y, fig_width, fig_height):

	fig = px.bar(df_data, x=fig_x, y=fig_y, color=fig_x)
	for trace in fig.data:
		trace.showlegend = False

	fig.update_layout(
		title=fig_title, 
		width=fig_width, height=fig_height,
		yaxis_title="",
		xaxis_title="",
		margin=dict(l=20, r=20, t=50, b=0),
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

# ---------------------------------------------------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------------------------------------------------

# def create_small_chart(df_data, fig_title, fig_width, fig_height=None, fig_inside_label=None):
# 	fig = px.bar(
# 		df_data,
# 		x=df_data.values,
# 		y=df_data.index,
# 		color=df_data.index,
# 		orientation='h',
# 	)
# 	annotations = []
# 	inside_label = None

# 	for i in range(len(df_data)):
# 		if fig_inside_label:
# 			inside_label = f'{df_data.index[i]} - <b>{df_data.values[i]}</b>'
# 		else:
# 			inside_label = str(df_data.values[i])
# 		annotations.append(dict(
# 								x=df_data.values[i] / 2,
# 								y=df_data.index[i],
# 								# text=str(df_data.values[i]),
# 								# text=str(df_data.index[i]),
# 								text=inside_label,
# 								xanchor='auto',
# 								yanchor='middle',
# 								showarrow=False))

# 	fig.update_layout(
# 		title=fig_title, 
# 		width=fig_width, 
# 		height=fig_height if fig_height else fig_width,
# 		yaxis_title="",
# 		xaxis_title="",
# 		margin=dict(l=10, r=50, t=50, b=0),
# 		paper_bgcolor='rgba(0,0,0,0)',
# 		plot_bgcolor='rgba(0,0,0,0)',
# 		yaxis_showticklabels=False if fig_inside_label else True,
# 		xaxis_showticklabels=False,
# 		showlegend=False,
# 		annotations=annotations,
# 	)

# 	return {
# 		"plot": fig.to_html(full_html=False) if fig else "",
# 		"width": fig_width,
# 	}


# ---------------------------------------------------------------------------------------------------

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
								# text=str(df_data.values[i]),
								# text=str(df_data.index[i]),
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
		margin=dict(l=10, r=50, t=50, b=0),
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
				user_agent_dictionary = get_user_agent_dictionary(
					user_agent_string)
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

	fig = px.bar(df, x="Country", y="Count",
				 color_discrete_sequence=['blue']*len(df))
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

	url = URL.find_by_short_url(short_url)
	fig = px.pie(df, values="Count", names="Country")
	fig.update_traces(textposition='inside')
	fig.update_layout(uniformtext_minsize=12,
					  uniformtext_mode='hide', margin=dict(t=0, b=0, l=0, r=0))

	return render_template("/public/info.html", visitors=visitors, url=url, plot=fig.to_html(full_html=False))

#=====================================================================================

def figure_lines(figure, suffix_first=None, suffix_second=None, font_icon=None):
	line_break = "<br>" if suffix_second else ""
	second_div_class = "style='margin-top:auto; margin-bottom:auto'" if suffix_second else ""
	figure_html = f"<div><span class='figure'>{figure}</span> <span class='unit'>{suffix_first}</span> {line_break} <span class='unit2'>{ suffix_second }</span></div>\n"
	figure_html += f"<div {second_div_class}><i class='{font_icon} fa-2xl'></i></div>"
	#   <div>{{ data["visitor_average_page_view"] }} pages <br>Per Visit</div>
	#   <div style="margin-top:auto; margin-bottom:auto"><i class="fa-regular fa-eye fa-2xl"></i></div>

	#   <div>{{ data["visitor_duration_seconds"] }} sec <br>Avg Session Time</div>
	#   <div style="margin-top:auto; margin-bottom:auto"><i class="fa-regular fa-clock fa-2xl"></i></div>
	return figure_html
# ---------------------------------------------------------------------------------------------------------------------
@app.route("/dashboard")
def dashboard_index():
	
	df = pd.read_csv("url_visitor.csv")
	visitor_return_width = 0
	machine_width = 0
	os_width = 0
	browser_width = 0
	row_width_first = 400
	row_width_second = 400
	row_width_third = 250
	row_orientation_third = "v"

	week_count_plot = None
	bounce_count_plot = None
	short_url_plot = None
	machine_plot, os_plot, browser_plot = None, None, None

	visitor_new_return_fig, machine_fig, os_fig, browser_fig = None, None, None, None

# ------------------------------------------------------------------------------------------------------------
# 1 - 5 Figures:
	# 1. No of visitors (group visitors visit on the same date), regardless their countries,
	country_cols = ["visitor_country", "visitor_ip", "url_short_url"]
	country = df.groupby(country_cols)
	visitor_count = f"{len(country['visitor_id'].count()):,}"

	# 2. Average time they stay in the page
	df['visitor_visited_date'] = pd.to_datetime(df['visitor_visited_date'])
	# -----------------------------------
	# No of visitors visits more than one -> Average Session Time
	# Filter visitors who visit only once per day
	df_filtered = df.groupby(['visitor_ip', df['visitor_visited_date'].dt.date]).filter(lambda x: len(x) > 1)
	# Calculate the difference between max and min visitor_visited_date
	df_filtered['visit_duration'] = df_filtered.groupby(['visitor_ip', df_filtered['visitor_visited_date'].dt.date])['visitor_visited_date'].transform('max') - df_filtered.groupby(['visitor_ip', df_filtered['visitor_visited_date'].dt.date])['visitor_visited_date'].transform('min')
	visitor_duration = df_filtered['visit_duration'].mean()
	visitor_duration_seconds = convert_to_seconds(visitor_duration)

	# 3. No. of page views per visitor on average
	# Average Page View
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
	# def create_special_bar(df_data, fig_title, fig_x, fig_y, fig_width, fig_height):
	visitor_new_return_title = "Visitors by User Type"
	visitor_new_return_x = "visitor_type"
	visitor_new_return_y = "count"
	visitor_new_return_width = 220
	visitor_new_return_height = 200
	visitor_new_return_plot = create_special_bar(df_visitor_new_return, visitor_new_return_title, visitor_new_return_x, visitor_new_return_y, visitor_new_return_width, visitor_new_return_height)

	# visitor_new_return_fig = px.bar(df_visitor_new_return, x="visitor_type", y="count", color="visitor_type")
	# for trace in visitor_new_return_fig.data:
	# 	trace.showlegend = False

	# visitor_return_width = 250
	# visitor_new_return_fig.update_layout(
	# 	title='Visitors by User Type', 
	# 	width=visitor_return_width, height=200,
	# 	yaxis_title="",
	# 	xaxis_title="",
	# 	margin=dict(l=50, r=0, t=50, b=0),
	# 	xaxis_showgrid=False,
	# 	yaxis_showgrid=False,
	# 	plot_bgcolor='rgba(0,0,0,0)',
	# 	paper_bgcolor='rgba(0,0,0,0)',

	# )

	# visitor_new_return_fig.update_yaxes(showticklabels=False)

	# for bar in visitor_new_return_fig.data:
	# 	bar.text = bar.y
	# 	bar.textposition = "auto"
	# 	bar.hovertemplate = '%{text}'


	# 1st Rows: Week Vist / Bounce
	# 7: Week Visit


	today = datetime.now()
	today_string = today.strftime("%Y-%m-%d")
	start_date = pd.to_datetime("2022-10-01")
	end_date = pd.to_datetime(today_string)
	# end_date = pd.to_datetime("2023-01-31")
	weeks = pd.date_range(start_date, end_date, freq="W-SUN")

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
	country_fig = None
	country_plot = None
	country_title = "Top 5 Countries that Visitors are from"
	country_values = "visitor_ip"
	country_width = row_width_second

	country_group = df.groupby(["visitor_country"])["visitor_ip"]
	country_data = country_group.count().sort_values(ascending=False)
	# print(f"8. {country_data}")
	# country_values = "visitor_ip"
	country_data_top4 = country_data[:5]
	# country_title = "Visitors from"
	# country_width = 450
	# create_small_pie(df_data, fig_title, fig_values, fig_width):
	country_plot = create_small_pie(country_data_top4, country_title, country_values, country_width)
	# print(country_fig)


# 10. most visited short url
	short_url_fig = None
	short_url_width = row_width_second
	short_url_height = row_width_second
	short_url_plot = None
	short_url_title = "Top 3 Favourite URLs"

	short_url_plot = {
		"plot": short_url_fig,
		"width": short_url_width,
	}

	short_url_group = df.groupby(["url_title"])
	short_url_data = short_url_group.count()["url_id"].head().sort_values(ascending=False)	
	short_url_data_top3 = short_url_data[:3]
	short_url_plot = create_small_bar(short_url_data_top3, short_url_title, short_url_width, fig_height=short_url_width, fig_orientation="h", fig_inside_label=True)

# ---------------------------------------------------------------------------------------------------------------------
	# 11. Machine

	machine_fig = None
	machine_width = row_width_third 
	machine_title = "Machine Used"

	machine_plot = {
		"plot": machine_fig,
		"width": machine_width,
	}

	machine_group = df.groupby(["visitor_machine"])
	machine_data = machine_group.count()["visitor_ip"].sort_values(ascending=False)		
	machine_plot = create_small_bar(machine_data, machine_title, machine_width, fig_orientation=row_orientation_third)


	# 12. OS
	# if number == 12:

	os_fig = None
	os_width = row_width_third 
	os_title = "OS Used"

	os_plot = {
		"plot": os_fig,
		"width": os_width,
	}

	df["os_category"] = df["visitor_os"].apply(lambda x: categorize_os(x))
	os_group = df.groupby(["os_category"])
	os_data = os_group["visitor_os"].count().sort_values(ascending=False).head()
	os_plot = create_small_bar(os_data, os_title, os_width, fig_orientation=row_orientation_third)


#----------------------------------------------------------------------------------------------------------------------
	# 13. browser type
	# if number == 13:
	
	browser_fig = None
	browser_width = row_width_third 
	browser_title = "Browser Used"

	browser_plot = {
		"plot": browser_fig,
		"width": browser_width,
	}

	df["browser_category"] = df["visitor_browser"].apply(lambda x: categorize_browser(x))
	browser_group = df.groupby(["browser_category"])
	browser_data = browser_group["visitor_browser"].count().sort_values(ascending=False).head()
	browser_plot = create_small_bar(browser_data, browser_title, browser_width, fig_orientation=row_orientation_third)


	plots = {
		"week_count": week_count_plot,
		"bounce_count": bounce_count_plot,
		"country": country_plot,
		"short_url": short_url_plot,
		"machine": machine_plot,
		"os": os_plot,		
		"browser": browser_plot,
	}

	special_plots = {
		"visitor_new_return": visitor_new_return_plot,
	}
	
	div_list  = [ ["week_count", "bounce_count"], ["country", "short_url"], ["machine", "os", "browser"]]

	return render_template("/public/board2.html", plot=plots, special_plot=special_plots, figure=figures, divs=div_list)








"""

	if number == 6:
		visitor_ip_all = df.groupby(["visitor_ip"])
		visitor_ip_once = visitor_ip_all.filter(lambda x: len(x) == 1)
		visitor_ip_return = len(visitor_ip_all) - len(visitor_ip_once)
		visitor_new_return = [len(visitor_ip_once), visitor_ip_return]
		df_visitor_new_return = pd.DataFrame({
			"visitor_type": ["New", "Return"],
			"count": visitor_new_return,
		})

		visitor_new_return_fig = px.bar(df_visitor_new_return, x="visitor_type", y="count", color="visitor_type")
		for trace in visitor_new_return_fig.data:
			trace.showlegend = False
		visitor_return_width = 250
		visitor_new_return_fig.update_layout(
			title='Visitors by User Type', 
			width=visitor_return_width, height=200,
			yaxis_title="",
			xaxis_title="",
			margin=dict(l=50, r=0, t=50, b=0),
			xaxis_showgrid=False,
			yaxis_showgrid=False,
			plot_bgcolor='rgba(0,0,0,0)',
			paper_bgcolor='rgba(0,0,0,0)',

		)

		visitor_new_return_fig.update_yaxes(showticklabels=False)

		for bar in visitor_new_return_fig.data:
			bar.text = bar.y
			bar.textposition = "auto"
			bar.hovertemplate = '%{text}'

	if number >= 7 and number <= 8:

		today = datetime.now()
		today_string = today.strftime("%Y-%m-%d")
		start_date = pd.to_datetime("2022-10-01")
		end_date = pd.to_datetime(today_string)
		# end_date = pd.to_datetime("2023-01-31")
		weeks = pd.date_range(start_date, end_date, freq="W-SUN")

		df['week'] = pd.to_datetime(df['visitor_visited_date']).dt.to_period("W").astype(str)
		df_week = df.groupby(["week"])
		week_count_data = df_week.size().reset_index(name="count_per_week")
		week_count_width = 400
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
		bounce_rate_width = 400
		bounce_count_x = "week"
		bounce_count_y = "bounce_rate"
		bounce_count_title = "Bounce Rate by Weeks of Year"
		bounce_count_plot = create_small_line(bounce_rate_data, bounce_count_title, bounce_rate_width, bounce_count_x, bounce_count_y, False)





# 9: country
	country_fig = None
	country_plot = None
	country_title = "Top 5 Countries that Visitors are from"
	country_values = "visitor_ip"
	country_width = 400
	if number == 9:
		country_group = df.groupby(["visitor_country"])["visitor_ip"]
		country_data = country_group.count().sort_values(ascending=False)
		# print(f"8. {country_data}")
		# country_values = "visitor_ip"
		country_data_top4 = country_data[:5]
		# country_title = "Visitors from"
		# country_width = 450
		# create_small_pie(df_data, fig_title, fig_values, fig_width):
		country_plot = create_small_pie(country_data_top4, country_title, country_values, country_width)
		# print(country_fig)


# 10: Short url
	short_url_fig = None
	short_url_width = 450
	short_url_plot = None
	if number == 10:
		# 10. most visited short url

		short_url_fig = None
		short_url_width = 450 
		short_url_title = "Top 3 Favourite URLs"

		short_url_plot = {
			"plot": short_url_fig,
			"width": short_url_width,
		}

		short_url_group = df.groupby(["url_title"])
		short_url_data = short_url_group.count()["url_id"].head().sort_values(ascending=False)	
		short_url_data_top3 = short_url_data[:3]
		short_url_plot = create_small_chart(short_url_data_top3, short_url_title, short_url_width, True)

# ---------------------------------------------------------------------------------------------------------------------
	# 11. Machine

	if number >= 11 and number <= 13:
		machine_fig = None
		machine_width = 300 
		machine_title = "Machine Used"

		machine_plot = {
			"plot": machine_fig,
			"width": machine_width,
		}

		machine_group = df.groupby(["visitor_machine"])
		machine_data = machine_group.count()["visitor_ip"].sort_values(ascending=False)		
		machine_plot = create_small_chart(machine_data, machine_title, machine_width)


	# 12. OS
	# if number == 12:

		os_fig = None
		os_width = 300 
		os_title = "OS Used"

		os_plot = {
			"plot": os_fig,
			"width": os_width,
		}

		df["os_category"] = df["visitor_os"].apply(lambda x: categorize_os(x))
		os_group = df.groupby(["os_category"])
		os_data = os_group["visitor_os"].count().sort_values(ascending=False).head()
		os_plot = create_small_chart(os_data, os_title, os_width)


#----------------------------------------------------------------------------------------------------------------------
	# 13. browser type
	# if number == 13:
	
		browser_fig = None
		browser_width = 300 
		browser_title = "Browser Used"

		browser_plot = {
			"plot": browser_fig,
			"width": browser_width,
		}

		df["browser_category"] = df["visitor_browser"].apply(lambda x: categorize_browser(x))
		browser_group = df.groupby(["browser_category"])
		browser_data = browser_group["visitor_browser"].count().sort_values(ascending=False).head()
		browser_plot = create_small_chart(browser_data, browser_title, browser_width)

	plots = {

		
		# "short_url": {
		# 	"plot": short_url_fig.to_html(full_html=False) if short_url_fig else "",
		# 	"width": short_url_width,
		# },
		# "visitor_return": {
		# 	"plot": visitor_new_return_fig.to_html(full_html=False) if visitor_new_return_fig else "",
		# 	"width": visitor_return_width,
		# },

		"week_count": week_count_plot,
		"bounce_count": bounce_count_plot,

		"country": country_plot,

		"short_url": short_url_plot,

		"machine": machine_plot,

		"os": os_plot,
		
		"browser": browser_plot,

	}
	print(len(plots))


	return render_template("/public/board2.html", plot=plots)


"""



# ---------------------------------------------------------------------------------------------------------------------
@app.route("/dash", methods=["GET"])
def dashboard():
	# Total number of visitors
	# df = Visitor.get_url_visitor_df()
	# df.to_csv("url_visitor.csv")

	df = pd.read_csv("url_visitor.csv")
	# print(df)

	# Statistics
	# 1. No of visitors (group visitors visit on the same date), regardless their countries,
	country_cols = ["visitor_country", "visitor_ip", "url_short_url"]
	country = df.groupby(country_cols)
	visitor_count = f"{len(country['visitor_id'].count()):,}"

	# 2. Average time they stay in the page
	df['visitor_visited_date'] = pd.to_datetime(df['visitor_visited_date'])
	# -----------------------------------
	# No of visitors visits more than one -> Average Session Time
	# Filter visitors who visit only once per day
	df_filtered = df.groupby(
		['visitor_ip', df['visitor_visited_date'].dt.date]).filter(lambda x: len(x) > 1)
	# Calculate the difference between max and min visitor_visited_date
	df_filtered['visit_duration'] = df_filtered.groupby(['visitor_ip', df_filtered['visitor_visited_date'].dt.date])['visitor_visited_date'].transform(
		'max') - df_filtered.groupby(['visitor_ip', df_filtered['visitor_visited_date'].dt.date])['visitor_visited_date'].transform('min')
	visitor_duration = df_filtered['visit_duration'].mean()
	visitor_duration_seconds = convert_to_seconds(visitor_duration)

	# print(visitor_duration_seconds)

	# 3. No. of page views per visitor on average
	# Average Page View
	df_ip = df.groupby(["visitor_ip", "url_id"])
	visitor_average_page_view = round(df_ip["visitor_ip"].count().mean(), 2)
	# print(df_ip.size().mean())

	# 4. bounce rate (overall) of this month
	visitor_ip_all = df.groupby(["visitor_ip"])
	visitor_ip_once = visitor_ip_all.filter(lambda x: len(x) == 1)
	bounce_rate_one = round(
		visitor_ip_once.shape[0] / len(visitor_ip_all["visitor_ip"]) * 100, 2)
	print("4. bounce_rate", f"{bounce_rate_one}")

	# 5. total number of pages views
	total_pages_view = f"{df['visitor_ip'].count():,}"
	# print(total_pages_view)

	# 6. visits by week of year
	start_date = pd.to_datetime("2022-10-01")
	end_date = pd.to_datetime("2023-01-31")
	# here we specify "W-SUN" to use the Sunday of each week as the week's representative date
	weeks = pd.date_range(start_date, end_date, freq="W-SUN")
	df['week'] = df['visitor_visited_date'].dt.to_period("W").astype(str)
	df_week = df.groupby(["week"])
	week_count_data = df_week.size().reset_index(name="count_per_week")

	week_count_fig = px.area(week_count_data, x='week', y='count_per_week', text="count_per_week")
	annotations = []
	for i in range(len(week_count_data)):
		annotations.append(dict(x=week_count_data['count_per_week'][i],
								y=week_count_data['week'][i],
								text=str(week_count_data['count_per_week'][i]),
								xanchor='center',
								yanchor='top',
								showarrow=False))

	week_count_fig.update_traces(textposition="top center")
	week_count_fig.update_layout(
		title="Visit by Week of Year",
		yaxis_title="",
		xaxis_title="",
		width=400, 
		height=300,
		# xaxis=dict(
		# 	tickvals=list(range(len(week_count_data))),
		# 	# ticktext=list(range(1, len(week_count_data)+1))
		# 	ticktext=list(week_count_data['week'])

		# ),
		# yaxis = dict(
		# 	ticktext=list(week_count_data['week']),
		# ),
		xaxis_showticklabels=False,
		yaxis_showticklabels=False,
		margin=dict(l=10, r=10, t=50, b=10),

		# shapes=[dict(
		# 	type='rect',
		# 	x0=week_count_data['week'].min(),
		# 	x1=week_count_data['week'].max(),
		# 	y0=0,
		# 	y1=week_count_data['count_per_week'].max(),
		# 	# fillcolor='lightgray',
		# 	# opacity=0.5,
		# 	layer='below',
		# 	line=dict(width=0),
		# )],
		xaxis_showgrid=False,
		yaxis_showgrid=False,
		plot_bgcolor='rgba(0,0,0,0)',
		paper_bgcolor='rgba(0,0,0,0)',
	)

	# 7. bounce rate by week of the year
	start_date = pd.to_datetime("2022-10-01")
	end_date = pd.to_datetime("2023-01-31")
	weeks = pd.date_range(start_date, end_date, freq="W-SUN")
	df['week'] = df['visitor_visited_date'].dt.to_period("W").astype(str)

	df_week = df.groupby("week")
	total_per_week = df_week["url_id"].count()
	bounce_per_week = df_week.apply(
		lambda x: x[x["url_id"].duplicated() == False].shape[0])
	bounce_rate = pd.concat([total_per_week, bounce_per_week], axis=1)
	bounce_rate.columns = ["total_per_week", "bounce_per_week"]
	bounce_rate["bounce_rate"] = bounce_rate["bounce_per_week"] / \
		bounce_rate["total_per_week"] * 100
	bounce_rate_data = round(bounce_rate["bounce_rate"], 2)
	bounce_rate_data = bounce_rate_data.reset_index()
	bounce_rate_fig = px.line(bounce_rate_data, x='week', y='bounce_rate')

	bounce_rate_fig = px.line(bounce_rate_data, x='week', y='bounce_rate')
	bounce_rate_fig.update_layout(
		title="Bounce Rate by Week of Year",
		xaxis=dict(
			tickvals=list(range(len(bounce_rate_data))),
			# ticktext=list(range(1, len(week_count_data)+1))
			# ticktext=['']*len(bounce_rate_data)
			ticktext=list(bounce_rate_data['week'])

		),
		# template="simple_white",
		shapes=[dict(
			type='rect',
			x0=bounce_rate_data['week'].min(),
			x1=bounce_rate_data['week'].max(),
			y0=0,
			y1=bounce_rate_data['bounce_rate'].max(),
			# fillcolor='lightgray',
			# opacity=0.5,
			layer='below',
			line=dict(width=0),
		)],
		xaxis_showgrid=False,
		yaxis_showgrid=False,
		paper_bgcolor='rgba(0,0,0,0)',
		plot_bgcolor='rgba(0,0,0,0)',
		# template="simple_white"
	)

	# print(bounce_rate["bounce_rate"])

	# 8. visitors from different countries (overall)
	country_group = df.groupby(["visitor_country"])["visitor_ip"]
	visitor_country_data = country_group.count().sort_values(ascending=False)
	print(f"8. {visitor_country_data}")

	visitor_country_data_top4 = visitor_country_data[:5]

	visitor_country_fig = px.pie(visitor_country_data_top4, values='visitor_ip', names=visitor_country_data_top4.index)
	visitor_country_fig.update_layout(
		title='Top 5 Country that Visitors are from', 
		width=450, height=450,
		showlegend=False,
		)
	visitor_country_fig.update_traces(textposition='inside', textinfo='percent+label', direction='clockwise')




	# 9. visitors by user type: new and returning
	visitor_ip_all = df.groupby(["visitor_ip"])
	visitor_ip_once = visitor_ip_all.filter(lambda x: len(x) == 1)
	visitor_ip_return = len(visitor_ip_all) - len(visitor_ip_once)
	visitor_new_return = [len(visitor_ip_once), visitor_ip_return]
	df_visitor_new_return = pd.DataFrame({
		"visitor_type": ["New", "Return"],
		"count": visitor_new_return,
	})

	visitor_new_return_fig = px.bar(df_visitor_new_return, x="visitor_type", y="count", color="visitor_type", width=200, height=200)

	for trace in visitor_new_return_fig.data:
		trace.showlegend = False

	visitor_new_return_fig.update_layout(title=None)
	visitor_new_return_fig.update_layout(xaxis_title=None, yaxis_title=None)
	visitor_new_return_fig.update_layout(
		xaxis_showline=False, yaxis_showline=False)
	visitor_new_return_fig.update_yaxes(showticklabels=False)

	for bar in visitor_new_return_fig.data:
		bar.text = bar.y
		bar.textposition = "auto"
		bar.hovertemplate = '%{text}'

	# 10. machine type
	machine_group = df.groupby(["visitor_machine"])
	machine_group_data = machine_group.count()["visitor_ip"].sort_values(ascending=False)

	# print(machine_group_data.index.tolist())
	machine_group_fig = px.bar(machine_group_data,  y=machine_group_data.values, x=machine_group_data.index, color=machine_group_data.index)
	annotations = []
	for i in range(len(machine_group_data)):
		annotations.append(dict(x=machine_group_data.index[i], y=machine_group_data.values[i], text=machine_group_data.index[i], showarrow=False))

	machine_group_fig.update_layout(
		title='Machines', width=300, height=250,
		yaxis_title="Number of Visitors",
		xaxis_title="Types of Machine",
		margin=dict(l=50, r=50, t=50, b=50),
		paper_bgcolor='rgba(0,0,0,0)',
		plot_bgcolor='rgba(0,0,0,0)',
		xaxis=dict(
		tickmode='array',
		tickvals=machine_group_data.values.tolist(),
		ticktext=machine_group_data.index.tolist(),
		tickangle=0,
		tickfont=dict(size=9),
		ticklen=4,
		tickwidth=2,
		showticklabels=False
		),
		showlegend=False,
		annotations= annotations,
	)






	# 11. os type
	df["os_category"] = df["visitor_os"].apply(lambda x: categorize_os(x))
	os_group = df.groupby(["os_category"])
	os_data = os_group["visitor_ip"].count().sort_values(ascending=False).head()
	# print(os_group["visitor_ip"].count().sort_values(ascending=False).head())
	# print(os_data)


	os_fig = px.bar(os_data,  y=os_data.values, x=os_data.index, color=os_data.index)
	annotations = []
	for i in range(len(os_data)):
		annotations.append(dict(x=os_data.index[i], y=os_data.values[i], text=os_data.index[i], showarrow=False))

	os_fig.update_layout(
		title='Machines', width=300, height=250,
		yaxis_title="Number of Visitors",
		xaxis_title="OS Type",
		margin=dict(l=50, r=50, t=50, b=50),
		paper_bgcolor='rgba(0,0,0,0)',
		plot_bgcolor='rgba(0,0,0,0)',
		xaxis=dict(
		tickmode='array',
		tickvals=os_data.values.tolist(),
		ticktext=os_data.index.tolist(),
		tickangle=0,
		tickfont=dict(size=9),
		ticklen=4,
		tickwidth=2,
		showticklabels=False
		),
		showlegend=False,
		annotations= annotations,
	)




	# 12. browser type
	df["browser_category"] = df["visitor_browser"].apply(lambda x: categorize_browser(x))
	browser_group = df.groupby(["browser_category"])
	browser_data = browser_group["visitor_browser"].count(
	).sort_values(ascending=False).head()

	browser_fig = px.bar(browser_data,  y=browser_data.values, x=browser_data.index, color=browser_data.index, orientation='h')
	annotations = []

	browser_fig.update_layout(
		title='Browsers Used', width=300, height=250,
		yaxis_title="Number of Visitors",
		xaxis_title=" ",
		margin=dict(l=60, r=60, t=60, b=60),
		paper_bgcolor='rgba(0,0,0,0)',
		plot_bgcolor='rgba(0,0,0,0)',
		xaxis=dict(
		tickmode='array',
		tickvals=browser_data.values.tolist(),
		ticktext=browser_data.index.tolist(),
		tickangle=0,
		tickfont=dict(size=9),
		ticklen=4,
		tickwidth=2,
		showticklabels=False
		),
		showlegend=False,
		annotations= annotations,
	)







	# 13. most visited short url
	short_url_group = df.groupby(["url_title"])
	short_url_data = short_url_group.count()["url_id"].head().sort_values(ascending=False)
	# print(short_url_data)

	# bar
	short_url_data_top3 = short_url_data[:3]
	short_url_fig = px.bar(short_url_data_top3,  y=short_url_data_top3.values, x=short_url_data_top3.index, color=short_url_data_top3.index)

	annotations = []
	short_url_fig.update_layout(
		title='Top 3 Short URL', width=450, height=450,
		yaxis_title="Number of Visitors",
		xaxis_title="Title",
		margin=dict(l=50, r=50, t=50, b=50),
		paper_bgcolor='rgba(0,0,0,0)',
		plot_bgcolor='rgba(0,0,0,0)',
		xaxis=dict(
			tickmode='array',
			tickvals=short_url_data_top3.values,
			ticktext=short_url_data_top3.index,
			tickangle=0,
			tickfont=dict(size=9),
			ticklen=5,
			tickwidth=2,
			showticklabels=True
		),
		showlegend=False,
		# annotations=annotations,
	)



	data = {
		"visitor_count": visitor_count,
		"visitor_duration_seconds": visitor_duration_seconds,
		"visitor_average_page_view": visitor_average_page_view,
		"bounce_rate": bounce_rate_one,
		"total_pages_view": total_pages_view,
		"week_count_data": week_count_data,
		"bounce_rate_data": bounce_rate_data,
		"visitor_country_data": visitor_country_data,
		"machine_group_data": machine_group_data,
		"visitor_new_return": visitor_new_return,
		"os_data": os_data,
		"browser_data": browser_data,
		"short_url_data": short_url_data,

	}
	return render_template("/public/board.html", data=data, plot=visitor_new_return_fig.to_html(full_html=False),
						   plot2=week_count_fig.to_html(full_html=False), plot3=bounce_rate_fig.to_html(full_html=False),
						   plot4=visitor_country_fig.to_html(full_html=False), plot5=machine_group_fig.to_html(full_html=False), \
						   plot6=short_url_fig.to_html(full_html=False), plot7=os_fig.to_html(full_html=False),\
						   plot8=browser_fig.to_html(full_html=False) \
						   )

	# print("Q1. number of visitor", df.count()[0])
	# print("Q1. number of visitor", df.count()[0])
	# print("Q1. number of visitor", df.count()[0])
	# print("Q1. number of visitor", df.count()[0])
	# print("Q1. number of visitor", df.count()[0])

	# get_url_visitor_all


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
			"device": f"{device} {brand} {model}".strip(),
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
		"device": f"{device} {brand} {model}".strip()
	}
	short = secrets.token_hex(3)
	print(short)
	return data
# @app.route("/<short>")
# def redirect_to(short):
# 	long_url = "http://www.google.com"
# 	return redirect(long_url, code=302)
