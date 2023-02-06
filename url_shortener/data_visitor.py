import requests, secrets, random, json, time
from tqdm import tqdm
from datetime import datetime, timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from url_shortener import app, views, visitor_views
from .models import db, URL, Visitor

from user_agents import parse

# ---------------------------------------------------------------------------------------------------------------------
# Create a function "progress_bar" with the parameters "wait_time" and "description" to display the loading time
#
def progress_bar(wait_time, description):
    for i in tqdm(range(wait_time), desc=description, unit="seconds"):
        time.sleep(1)  

def load_ip_file():
	ip_list = []
	with open("url_shortener/templates/public/data/ip.txt", "r") as file:
		ip_list = file.read().splitlines()
	return ip_list

def load_user_agent_file():
	user_agent_list = []
	with open("url_shortener/templates/public/data/user_agent.txt", "r") as file:
		user_agent_list = file.read().splitlines()
	return user_agent_list
	
def update_ip_list(ip_list, error_ip):
	if ip_list and error_ip:
		new_ip_list = ip_list[:]
		new_ip_list.remove(error_ip)
		# print(f"{len(new_ip_list)} {len(ip_list)}")
		try:
			print(f"\nTry to update the file ip.txt.")
			with open("url_shortener/templates/public/data/ip.txt", "w") as file:
				file.write("\n".join(new_ip_list))
			print(f"Record the ip address [{error_ip}] with error.\n")
			with open("url_shortener/templates/public/data/error_ip.txt", "a") as file:
				file.write(f"{error_ip}\n")
		except IOError as e:
			print(e)

# ---------------------------------------------------------------------------------------------------------------------
# For ip-api only
def random_ip_april():
	user_agent_list = load_user_agent_file()
	headers = {'Accept': 'application/json'	}
	base_url = "http://ip-api.com/json/"
	query=f"fields=status,message,country,regionName,city,lat,lon,isp,asname,query"
	visitor_dictionary = {}	
	count = 1
	visit_range_start = datetime(2022, 10, 1, 0, 0, 0)
	visit_range_end = datetime(2023, 1, 31, 23, 59, 59)
	limit = 1000
	print(f"\nThe total number of clicks is {limit}.")
	while count <= limit:
		visitor_datetime = visit_range_start + timedelta(seconds=random.randint(0, int((visit_range_end - visit_range_start).total_seconds())))
		ip_list = load_ip_file()
		ip_index = random.randrange(len(ip_list))
		fake_ip = ip_list[ip_index]
		user_agent_index = random.randrange(len(user_agent_list))
		fake_user_agent = user_agent_list[user_agent_index]
		headers["User-Agent"] = fake_user_agent
		query_url = f"{base_url}{fake_ip}?{query}"
		response = requests.get(query_url, headers=headers)
		print(f"{query_url}")

		if response.json()["status"] == "fail":
			wait_time = random.randrange(10,15)					
			description = f"Waiting:"
			progress_bar(wait_time, description)
			update_ip_list(ip_list, fake_ip)
		else:
			ip_data = response.json()
			ip_dictionary = visitor_views.get_ip_dictionary_april(ip_data)
			# user_agent = parse(fake_user_agent)
			user_agent_dictionary = visitor_views.get_user_agent_dictionary(fake_user_agent)
			visitor_dictionary = {**ip_dictionary, **user_agent_dictionary}
			random_loop = random.randrange(1, 5)
			print(f"\nNew IP {fake_ip} will attempt [{random_loop}] click(s).")				
			for index in range(random_loop):
				url = URL.random_url()
				url_id = url[0].url_id
				visitor_dictionary["visited_date"] = visitor_datetime
				visitor_dictionary["url_id"] = url_id
				row_affected = Visitor.add_visitor(**visitor_dictionary)
				random_seconds = random.randint(0, 100)
				visitor_datetime = visitor_datetime + timedelta(seconds=random_seconds)
				print(f"#{count}/{limit} click on {url[0].url_short_url} -> [Attempt: {index+1}/{random_loop}]")
				wait_time = random.randrange(10,15)					
				description = f"Waiting:"
				progress_bar(wait_time, description)
				if count > limit:
					break
				count += 1
	exit()



# ---------------------------------------------------------------------------------------------------------------------
# For ipapi only
def random_ip():
	
	user_agent_list = load_user_agent_file()
	headers = {'Accept': 'application/json'	}
	base_url = "https://ipapi.co"
	format = "json"
	visitor_dictionary = {}	
	# print(len(urls))
	count = 1
	visit_range_start = datetime(2022, 10, 1, 0, 0, 0)
	visit_range_end = datetime(2023, 1, 31, 23, 59, 59)
	limit = 1000
	print(f"\nThe total number of clicks is {limit}.")
	while count <= limit:
		visitor_datetime = visit_range_start + timedelta(seconds=random.randint(0, int((visit_range_end - visit_range_start).total_seconds())))
		ip_list = load_ip_file()
		ip_index = random.randrange(len(ip_list))
		fake_ip = ip_list[ip_index]
		user_agent_index = random.randrange(len(user_agent_list))
		fake_user_agent = user_agent_list[user_agent_index]
		headers["User-Agent"] = fake_user_agent
		ipapi_url = f"{base_url}/{fake_ip}/{format}" 
		response = requests.get(ipapi_url, headers=headers)		
		
		if "Sorry, you have been blocked" in response.text:
			wait_time = random.randrange(5,10)
			description = "Cooling down"
			progress_bar(wait_time, description)
			# time.sleep(5)
		else:
			if "error" not in response.json():
				ip_data = response.json()
				ip_dictionary = visitor_views.get_ip_dictionary(ip_data)
				# user_agent = parse(fake_user_agent)
				user_agent_dictionary = visitor_views.get_user_agent_dictionary(fake_user_agent)
				visitor_dictionary = {**ip_dictionary, **user_agent_dictionary}
				random_loop = random.randrange(1, 5)
				print(f"\nNew IP {fake_ip} will attempt [{random_loop}] click(s).")				
				for index in range(random_loop):
					url = URL.random_url()
					url_id = url[0].url_id
					visitor_dictionary["visited_date"] = visitor_datetime
					visitor_dictionary["url_id"] = url_id
					row_affected = Visitor.add_visitor(**visitor_dictionary)
					random_seconds = random.randint(0, 100)
					visitor_datetime = visitor_datetime + timedelta(seconds=random_seconds)
					print(f"#{count}/{limit} click on {url[0].url_short_url} -> [Attempt: {index+1}/{random_loop}]")
					wait_time = random.randrange(10,15)					
					description = f"Waiting:"
					progress_bar(wait_time, description)
					if count > limit:
						break
					count += 1
			else:

				if response.json()["error"]:
					print(f"{response.json()}")
					exit()
				else:
					update_ip_list(ip_list, fake_ip)
					continue		
	exit()

app.config.from_prefixed_env()
print(app.config["SQLALCHEMY_DATABASE_URI"])

try:
	with app.app_context():
		random_ip_april()		

		pass
		# db.drop_all()
		# db.create_all()
		# print("Tables created successfully")
except Exception as e:
	print("An error occurred while update the VISITOR table:", e)
	exit()



# def faked_vistor():
# 	is_faked = True
# 	ip_data = {}

# 	if is_faked:
# 		ua = UserAgent()
# 		fake_user_agent = ua.random
# 		ip_list = load_ip_file()
# 		headers = {
# 			'Accept': 'application/json',
# 			'User-Agent': fake_user_agent,
# 			}
# 		base_url = "https://ipapi.co"
# 		format = "json"
# 		while True:
# 			fake_ip = ip_list[random.randrange(0, len(ip_list))]
# 			ipapi_url = f"{base_url}/{fake_ip}/{format}" 
# 			try: 
# 				response = requests.get(ipapi_url, headers=headers)	
# 				print(response.text)		
# 				ip_data = response.json()
# 				if not "error" in ip_data:
# 					break
# 			except json.JSONDecodeError as e:
# 				# handle the error
# 				return f"Error: Invalid JSON response from server, {e}"
# 	else:
# 		#use real
# 		pass
	
# 	return ip_data