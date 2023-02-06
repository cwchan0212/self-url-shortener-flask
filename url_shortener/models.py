
from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, asc, desc, exists, text, inspect, func
from flask_sqlalchemy import SQLAlchemy
from url_shortener import app
from random import shuffle

db = SQLAlchemy(app)

class URL(db.Model):
	url_id = db.Column(db.Integer, primary_key=True)
	url_short_url = db.Column(db.String(25), unique=True)
	url_long_url = db.Column(Text, nullable=False)
	url_title = db.Column(db.String(100), nullable=False)
	url_description = db.Column(Text)
	url_created_date = db.Column(db.DateTime, server_default=text("CURRENT_TIMESTAMP"))
	url_updated_date = db.Column(db.DateTime, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))
	
	def __str__(self):		
		return f"[{self.url_id}, '{self.url_short_url}', '{self.url_long_url}', '{self.url_description}', '{self.url_created_date.isoformat()}', '{self.url_updated_date.isoformat()}']"

	def add_url(short_url, long_url, title, description):
		count = 0
		try:
			url = URL(url_short_url=short_url, url_long_url=long_url, url_title=title, url_description=description)
			db.session.add(url)
			db.session.commit()
			count = 1
		except Exception as e:
			print(f"Error in adding new url {e}")
			db.session.rollback()
		return count
	
	def all_url_pages(current_page):
		per_page = 10
		urls = db.session.query(URL).order_by(URL.url_id.desc()).paginate(page=current_page, per_page=per_page)
		# items = db.session.query(Item).offset((page - 1) * page_size).limit(page_size).all()
		# urls = db.session.paginate(db.session.filter.query(URL).order_by(URL.url_id.desc()).all(), page=current_page)
		return urls

	def all_url():
		urls = None
		try:
			urls = db.session.query(URL).order_by(URL.url_id.desc()).all()
		except Exception as e:
			print(e)
		return urls
	
	
	def update_by_id(id, short_url, long_url, title, description):
		row_affected = 0
		try:
			row_affected = db.session.query(URL).filter(URL.url_id==id).update({
				"url_short_url": short_url, 
				"url_long_url": long_url, 
				"url_title": title,
				"url_description": description
				})
			db.session.commit()
		except Exception as e:
			print(e)
			db.session.rollback()
		return row_affected

	def delete_by_id(id):
		row_affected = 0
		try:
			row_affeced = db.session.query(URL).filter(URL.url_id==id).delete()
			db.session.commit()
		except Exception as e:
			print(e)
			db.session.rollback()
		return row_affeced

	def find_by_short_url(short_url):
		url = None
		try:
			url	= db.session.query(URL).filter(URL.url_short_url==short_url).first()
		except Exception as e:
			print(e)
		return url
	
	def random_url():
		url = None
		try:
			# url_rows = URL.query.order_by(func.random()).limit(1).all()
			url = db.session.query(URL).order_by(db.func.random()).limit(1).all()
		except Exception as e:
			print(e)
		return url
		

class Visitor(db.Model):
	visitor_id = db.Column(db.Integer, primary_key=True)
	url_id = db.Column(db.Integer, db.ForeignKey('url.url_id'), nullable=False)
	visitor_ip = db.Column(db.String(50), nullable=False)
	visitor_city = db.Column(db.String(100), nullable=True)
	visitor_region = db.Column(db.String(100), nullable=True)
	visitor_country = db.Column(db.String(100), nullable=True)
	visitor_coords = db.Column(db.String(100), nullable=True)
	visitor_isp  = db.Column(db.String(100), nullable=True)
	visitor_bot  = db.Column(db.Boolean, default=False)
	visitor_os  = db.Column(db.String(100), nullable=True)
	visitor_device = db.Column(db.String(100), nullable=True)
	visitor_browser = db.Column(db.String(100), nullable=True)
	visitor_machine = db.Column(db.String(50), nullable=True)
	visitor_user_agent = db.Column(Text, nullable=False)
	visitor_visited_date = db.Column(db.DateTime, server_default=text("CURRENT_TIMESTAMP"))

	def add_visitor(url_id, ip, city, region, country, coords, isp, bot, os, device, browser, machine, user_agent, visited_date=None):
		count = 0
		try:
			if visited_date:
				visitor = Visitor(url_id=url_id, visitor_ip=ip, visitor_city=city, visitor_region=region, visitor_country=country, visitor_coords=coords, visitor_isp=isp, visitor_bot=bot, visitor_os=os, visitor_device=device, visitor_browser=browser, visitor_machine=machine, visitor_visited_date=visited_date, visitor_user_agent=user_agent)
			else:
				visitor = Visitor(url_id=url_id, visitor_ip=ip, visitor_city=city, visitor_region=region, visitor_country=country, visitor_coords=coords, visitor_isp=isp, visitor_bot=bot, visitor_os=os, visitor_device=device, visitor_browser=browser, visitor_machine=machine, visitor_user_agent=user_agent)
			db.session.add(visitor)
			db.session.commit()
			count = 1
		except Exception as e:
			print(f"Error in adding new visitor {e}")
			db.session.rollback()
		return count

	def get_visitor_count_by_country_and_url(short_url, sorting=False):
		if sorting:
			visitor = db.session.query(
				Visitor.visitor_country, 
				db.func.count(db.func.distinct(Visitor.visitor_ip)).label("distinct_visitor_ips"),
				db.func.count(db.func.distinct(Visitor.url_id)).label("distinct_urls")
			).join(URL, URL.url_id == Visitor.url_id).filter(URL.url_short_url == short_url).order_by(db.func.count(db.func.distinct(Visitor.visitor_ip)).desc()).group_by(Visitor.visitor_country, URL.url_long_url).all()
		else:
			visitor = db.session.query(
				Visitor.visitor_country, 
				db.func.count(db.func.distinct(Visitor.visitor_ip)).label("distinct_visitor_ips"),
				db.func.count(db.func.distinct(Visitor.url_id)).label("distinct_urls")
			).join(URL, URL.url_id == Visitor.url_id).filter(URL.url_short_url == short_url).group_by(Visitor.visitor_country, URL.url_long_url).all()

		return visitor

	# visitor_counts = db.session.query(Visitor.visitor_country, func.count(Visitor.visitor_country)).group_by(Visitor.visitor_country).all()

    # SELECT visitor_country, count(distinct visitor_ip) as unique_visitors
	# FROM visitor
	# GROUP BY visitor_country
	# ORDER BY unique_visitors DESC;

	# SELECT visitor_country, count(distinct visitor_ip) as unique_visitors
	# FROM visitor
	# WHERE url_id = <specific_url_id>
	# GROUP BY visitor_country
	# ORDER BY unique_visitors DESC;