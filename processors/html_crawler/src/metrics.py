from prometheus_client import Counter

SOURCE_CRAWLER_REQUEST_RECEIVED_CNT = Counter(
    "SOURCE_CRAWLER_REQUEST_RECEIVED_CNT", "The number of consumed crawler request"
)
SOURCE_CRAWLER_REQUEST_FAILED_CNT = Counter(
    "SOURCE_CRAWLER_REQUEST_FAILED_CNT", "The number of failed crawler request"
)
SOURCE_CRAWLER_REQUEST_COMPLETE_CNT = Counter(
    "SOURCE_CRAWLER_REQUEST_COMPLETE_CNT", "The number of completed crawler request"
)
