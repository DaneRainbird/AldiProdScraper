# AldiProductScraper

**Usage:** 

```python main.py [start] [end] [batch_size]```

`start` and `end` define the total range of product IDs to scrape, while `batch_size` is the number of products per request. I'd recommend limiting the batches to 2500 or so, otherwise you'll get a 504 Gateway Timeout Error.