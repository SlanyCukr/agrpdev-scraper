## Agrpdev-scraper
This repository contains functioning scraper - created using Scrapy package and Flask API.
### Installation
```shell
git clone https://github.com/SlanyCukr/agrpdev-scraper.git
pip3 install -r requirements.txt
```
### Running scraper
```shell
scrapy runspider scraper.py
```
##### Optional arguments  
```shell
-a url_limit=20 date_limit=2020-03-22
```
### Running Flask API
#### Linux:
First-time only:
```shell
export PYTHONPATH="${PYTHONPATH}:/<absolute_path_to_cloned_git>/api"
```
Every other time:
```shell
cd <absolute_path_to_cloned_git>/api
python3 -m flask run api.py --host=0.0.0.0
```
#### Windows: [use Pycharm](https://www.jetbrains.com/help/pycharm/creating-flask-project.html)

**API is live on** [this server](http://slanycukr.hopto.org:5000/ "this server")  
Scraper is run every minute, and downloads 5 articles.
