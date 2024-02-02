import os

from flask import Flask, request, jsonify
import requests
import redis
import logging

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
API_KEY = os.getenv("API_KEY", "waSUbz0YclQkXRErgqLM3g==CfH9igxWNSa3aoaY")

app = Flask(__name__)
redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_temp_from_ninjas_api(city: str):
    API_URL = 'https://api.api-ninjas.com/v1/weather?city={}'.format(city)
    response = requests.get(API_URL, headers={'X-Api-Key': API_KEY})
    if response.status_code == 200:
        min_temp = str(response.json().get("min_temp"))
        max_temp = str(response.json().get("max_temp"))
        return min_temp, max_temp
    else:
        logger.error(f"Ninjas API Request Failed for Given City: {city}")
        return None


def redis_get(city):
    cached_temp = redis_client.get(city)
    if cached_temp:
        min_temp, max_temp = cached_temp.split(',')
        logger.info(f"Temperature Data Retrieved from Redis City: {city}")
        return str(min_temp), str(max_temp)
    else:
        temps = get_temp_from_ninjas_api(city)
        if temps:
            logger.info(f"Temperature Data Retrieved from Ninjas City: {city}")
            min_temp, max_temp = temps
            redis_ttl = int(os.getenv("REDIS_TTL", 300))
            redis_client.setex(city, redis_ttl, f'{min_temp},{max_temp}')
            return str(min_temp), str(max_temp)
        else:
            logger.warning(f"City Not Found: {city}")
            return None


@app.route('/temp', methods=['GET'])
def get_temperature():
    city = request.args.get('city')
    if not city:
        logger.warning("City Is Missing")
        return jsonify(error="City Is Missing"), 400

    temps = redis_get(city)
    logger.info(temps)
    if temps:
        min_temp, max_temp = temps
        return jsonify(city=city, min_temperature=min_temp, max_temperature=max_temp)
    else:
        return jsonify(error="City Not Found"), 404


if __name__ == '__main__':
    server_port = int(os.getenv("SERVER_PORT", "5001"))
    app.run(debug=True, port=server_port, host="0.0.0.0")
