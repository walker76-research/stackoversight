# Code Duplication

This application is a naive way to find code duplicated from StackOverflow

## Getting Started

These instructions will get a copy of the project up and running on your local machine

### Prerequisites

Before running the project you will need to install the StackOverflow API and BeautifulSoup 4 libraries. Additionally you will need Redis and Dotenv

```
> pip install stackapi beautifulsoup4 redis python-dotenv
```

With Python 3

```
> pip3 install stackapi beautifulsoup4 redis python-dotenv
```

#### Redis Configuration

In the project rename the '.env-example' to '.env'

You shouldn't have to change the REDIS_HOST or REDIS_PORT if running locally. Set the REDIS_PASSWORD to whatever you set when configuring the redis.conf file.

## Built With

* [StackApi](https://stackapi.readthedocs.io/en/latest/) - Python library for connecting to StackOverflow
* [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/) - Python library for extracting HTML and XML data


## Authors

* [**Andrew Walker**](https://github.com/walker76)
* [**Jonathan Simmons**](https://github.com/johnsimmons2)
* [**Michael Coffey**](https://github.com/CoffeyBean60)
* [**Asher Snavely**](https://github.com/ashersnavely)
* [**Jan Svacina**](https://github.com/svacina)
