SELECT visitor_country, count(distinct visitor_ip) as unique_visitors
FROM visitor
WHERE url_id = 5
GROUP BY visitor_country
ORDER BY unique_visitors DESC;