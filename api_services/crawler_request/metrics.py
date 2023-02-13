from prometheus_client import Counter

POST_CRAWLER_CNT = Counter("post_crawler", "The number of post crawler request")
GET_CRAWLER_BY_ID_CNT = Counter(
    "get_crawler_by_id", "The number of post crawler request"
)
GET_ALL_CRAWLERS_CNT = Counter("get_all_crawlers", "The number of post crawler request")
