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

## Structure
### Procedure
We use the StackAPI to query for URLs containing Python code snippets and then use regular web scraping procedures to gather the "\<code\>" blocks to parse.

The list of code snippets is then added to a Redis queue which is processed through our pipeline and added to a locality sensitive hash forest for querying similarities.

### Pipeline Structure 
The pipeline is organized as such:
-link to image-

The proxies gather URLs from the StackAPI load balanced so that we do not overload their systems or run out of queries.

The URLs are sent to the Scraper which produces the the page information for the Processor.

#### Processor
The processor separates out the plaintext and code snippets and sends the code snippets down the pipeline.

The main components of the pipeline are as follows:
* Processor
* Sanitizer
* Filter
* Tokenizer
* Keyword Extractor

#### Sanitizer
The Sanitizer cleans the gathered code snippets by making sure that indentations are following Python requirements 
(sometimes indentations can be messed up by web formatting). It also strips the snippets of obvious plaintext or 
comments by parsing each line into an AST (does not need to parse for comments, since they are easily denoted by 
pound signs). Consequently, this implies that code sent to the filter is most likely Python. Thus this is a 
naive method of stripping whitespace.

#### Filter
The Filter makes sure that any code snippet handed to it is valid Python 3. Future work would be to provide a 
method of either translating Python 2 into 3 or validating code using a Google code detecting library instead 
of Python ASTs which can only compile code of the same version the script is running in.

#### Tokenizer
The Tokenizer creates a list of tokens in order of appearance from the code snippet so that similarity detection 
can be accomplished.

#### Keyword Extractor
The Keyword Extractor component takes the list of tokens and extracts standardized keywords out of them into a 
list of keywords. Thus, every code snippet at this point becomes an array of keyword strings. At this point 
the data may be serialized or put into the Hash to be serialized.

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
