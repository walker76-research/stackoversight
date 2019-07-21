# Code Duplication

This application is a naive way to find code duplicated from StackOverflow

## Getting Started

These instructions will get a copy of the project up and running on your local machine

### Prerequisites

Before running the project you will need to install the StackOverflow API and BeautifulSoup 4 libraries. Additionally you will need Redis, RQ and Dotenv

```
> pip install stackapi beautifulsoup4 redis rq python-dotenv
```

With Python 3

```
> pip3 install stackapi beautifulsoup4 redis python-dotenv
```

#### Redis Configuration

Download Redis for Windows from [ServiceStack](https://github.com/ServiceStack/redis-windows)

Configure the redis.windows.conf to use a password and run with the following command

```
> redis-server.exe redis.windows.conf
```

In the project rename the '.env-example' to '.env'

You shouldn't have to change the REDIS_HOST or REDIS_PORT if running locally. Set the REDIS_PASSWORD to whatever you set when configuring the redis.windows.conf file.

To run a worker:
```
> rq worker -u redis://:<password>@localhost:6379
```

To open RQ dashboard:
```
> rq-dashboard -H localhost -p 3000 --redis-password <password>
```
Once the dashboard is running you can navigate to [localhost:3000](http://localhost:3000) to access it.

## Built With

* [StackApi](https://stackapi.readthedocs.io/en/latest/) - Python library for connecting to StackOverflow
* [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/) - Python library for extracting HTML and XML data
* [Redis](https://redis.io/) - Redis is an in-memory key-value database
* [RQ](https://python-rq.org/) - Python library for queueing jobs and processing them in the background

## Authors

* [**Andrew Walker**](https://github.com/walker76)
* [**Jonathan Simmons**](https://github.com/johnsimmons2)
* [**Michael Coffey**](https://github.com/CoffeyBean60)
* [**Asher Snavely**](https://github.com/ashersnavely)
* [**Jan Svacina**](https://github.com/svacina)
