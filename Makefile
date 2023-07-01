up:
	docker-compose up activemq -d

down:
	docker-compose stop activemq

clean:
	docker rmi -f $(shell docker images -aq)
	docker rm -f $(shell docker ps -aq)
	docker ps -a
	docker images -a


workers:
	source venv/bin/activate && python src/audio_worker/client.py

server:
	source venv/bin/activate && python src/main.py
