# Goal
University of Aveiro

The goal of this project was to implement a distributed system to process time-costly audio processing jobs, by distributing them across many remote workers.

The end-user doesn't need to wait years, but seconds.

# Prominent project highlights
 - **Fanout exchange queue** - allows to send exactly one message to every subscribed client
 - **Fault Tolerance** - ACK/NACK messages, adjusting clients' heartbeats
 - **Performance** - Identifying bottlenecks is the first thing to consider to tune performance.

## Dependencies

For Ubuntu (and other debian based linux), run the following commands:

```bash
sudo apt install ffmpeg
sudo apt install make
```

## setup local python environment
Run the following commands to setup the environement:
```bash
python3 -m venv venv
source venv/bin/activate

pip install pip --upgrade
python3 -m venv --upgrade venv
pip install -r requirements.txt
```
## setup the broker
- `docker-compose up -d`
- **IMPORTANT!!!** - Create an exchange queue using the broker's UI!
    - Go to http://localhost:7777/#/exchanges, login with user: admin, pass: admin
    - Add a new exchange
        - Name: `reset`
        - Type: `fanout`
        - Press Add exchange
## Start the server
```
export PYTHONPATH=$PWD
make server
```
## Start workers
- You can start the workers to run on a different machine.
- Before run, since they subscribe to the broker, make sure to set the broker IP in the `src/config.py` file. E.g. `BROKER_HOST = '192.168.0.4'`. By default it is `localhost`, if the server and the workers run on the same machine.
```
export PYTHONPATH=$PWD
make workers
```

# Usage
1. Open the Web Page. Open `templates/index.html` file using browser.
2. Drop an MP3 file, and wait for the progress to go 100% (don't refresh the page while processing, the output will disappear), afterwards you can download your files:
    - Separated drums track
    - Separated vocals track
    - Separated other instruments (mostly guitar + keyboard) track
    - Separated bass track
    - Mix of chosen instruments (default is drums + bass)

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Fault Tolerance
- This system is resillient to worker crashes, please see the `WORKERS_UNHEALTHY` parameter to simulate the crash after `WORKER_SIMULATE_CRASH_AFTER` time.

## Configurations
- in `src/config.py` you can find a number of parameters to be adjusted, e.g.:
```python
### User Conf ###
BROKER_HOST = 'localhost'           # broker IP
WORKERS_HEALTHY = 10                # Amount of workers that do not crash
WORKERS_UNHEALTHY = 2               # Amount of workers that crash (their process terminates)
WORKER_SIMULATE_CRASH_AFTER = 20    # After this amount of seconds.
### User Conf ###
```

# Techstack
 - Backend: FastAPI
 - Middlewares: RabbitMQ
 - Frontend: Bootstrap, html, css

# Authors

Student: Miron Oskroba

NMEC: 112169

University of Aveiro

Computação Distribuída


