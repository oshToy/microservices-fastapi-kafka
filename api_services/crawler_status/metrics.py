from prometheus_client import Counter

POST_CRAWLER_STATUS_CNT = Counter(
    "post_crawler_status", "The number of post crawler status"
)
PUT_CRAWLER_STATUS_CNT = Counter(
    "put_crawler_status", "The number of put crawler status"
)
GET_CRAWLER_STATUS_BY_ID_CNT = Counter(
    "get_crawler_status_by_id", "The number of crawler status"
)
GET_CRAWLER_STATUS_BY_CRAWLER_ID_CNT = Counter(
    "get_crawler_status_by_crawler_id", "get_crawler_status_by_crawler_id"
)
