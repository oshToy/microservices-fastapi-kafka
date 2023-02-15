from prometheus_client import Counter

POST_CRAWLER_STATUS_CNT = Counter(
    "post_crawler_status", "The number of post crawler status"
)
PUT_CRAWLER_STATUS_CNT = Counter(
    "put_crawler_status", "The number of put crawler status"
)
BEGIN_UPDATE_CRAWLER_STATUS_BY_MESSAGE_CNT = Counter(
    "BEGIN_UPDATE_CRAWLER_STATUS_BY_MESSAGE_CNT",
    "The number of update crawler status by kafka messages",
)


DONE_UPDATE_CRAWLER_STATUS_BY_MESSAGE_CNT = Counter(
    "DONE_UPDATE_CRAWLER_STATUS_BY_MESSAGE_CNT",
    "The number of  update crawler status DONE by kafka messages",
)
FAILED_UPDATE_CRAWLER_STATUS_BY_MESSAGE_CNT = Counter(
    "FAILED_UPDATE_CRAWLER_STATUS_BY_MESSAGE_CNT",
    "The number of  update crawler status failed by kafka messages",
)
GET_CRAWLER_STATUS_BY_ID_CNT = Counter(
    "get_crawler_status_by_id", "The number of crawler status"
)
GET_CRAWLER_STATUS_BY_CRAWLER_ID_CNT = Counter(
    "get_crawler_status_by_crawler_id", "get_crawler_status_by_crawler_id"
)
