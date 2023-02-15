# Microservices - Kafka, FastAPI, Fasut

## Project Description
The Application is real time web crawler system.
[Full deatils](https://medium.com/@oshri1992/scaling-for-success-building-a-high-performance-app-with-microservices-fastapi-fasut-and-kafka-25437e006500) 

It includes three main components :

1.Crawl Request — Api that receive multiple HTML page crawl requests from clients.
The service should return to the client acknowledge that the process began and provide a unique crawler id within the response. NFR: working under heavy load

2.Crawl Process — A service that download the HTML pages and save it in data store. For efficiency, we will implement an option for steraming framework that can scaled easliy.
In addition we will support file caching , its mean same url requests will avoid refetch the page for 7 days ( imidiatly get cached file)

3.Crawl Status — Api that serve the status of crawling request by crawler id. The status can be one of : Accepted ( received and is pending
processing ) , Running, Error ( error occurred during the crawl ) , Complete. It returns 404 error if the crawler id did not found. if the status is completed we expect to get the location of the HTML in the data store. NFR: Status checks should not create additional loads on any other system.

## Architecture
![Architecture](https://user-images.githubusercontent.com/35071710/219124194-1d110218-909e-4f89-8a93-9784117f8093.png)

## Postman Collection
[public collection](https://elements.getpostman.com/redirect?entityId=10168156-2950ceb9-e306-4e3a-8c2c-3d0e8523dd6b&entityType=collection)

The collection contains 2 dierctory
1. Crawler requests API
2. Crawler Status API


## Local Development
1.apis are bindede to local storage with hot-reload, each code change will reload the service


### Build
`docker-compose up -d --build`

### Linters

pre commit hook before each git commit 
```shell
  pre-commit install 
```

Format the code
```shell
black .
```

### HTML CRAWLER
```shell
faust -A main worker -l info
```

### DEbug
- kafka consumers
```shell
kafka-console-consumer.sh --topic crawler-request --from-beginning --bootstrap-server localhost:9093
kafka-console-consumer.sh --topic crawler-status --from-beginning --bootstrap-server localhost:9093
```

Run tests
- api services
```shell
python -m pytest
```
