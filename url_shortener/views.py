import requests, secrets
from bs4 import BeautifulSoup
from url_shortener import app, visitor_views
from datetime import datetime
from flask import Flask, render_template, request, redirect, make_response, jsonify, flash, session, url_for
from user_agents import parse
from .models import URL, Visitor

# ---------------------------------------------------------------------------------------------------------------------
# Statistics
@app.route("/statistics")
def statistics():
	
	short = secrets.token_hex(3)
	urls  = URL.all_url_pages(1)
	# urls = URL.all_url()

	return render_template("public/statistics.html", urls=urls, short=short)

# ---------------------------------------------------------------------------------------------------------------------

@app.route("/statistics/<int:current_page>")
def statistics_page(current_page=None):
	short = secrets.token_hex(3)
	urls  = URL.all_url_pages(current_page)
	return render_template("public/statistics.html", urls=urls, short=short)

# ---------------------------------------------------------------------------------------------------------------------

# main
@app.route("/lists")
def index():
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
	
# ---------------------------------------------------------------------------------------------------------------------
	


@app.template_filter()
def datetime(dt):

	return dt.strftime("%Y-%m-%d %H:%M:%S")

