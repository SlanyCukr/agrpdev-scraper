## Agrpdev-scrapper
This repository contains functioning scrapper - created using Scrapy package and Flask API.
### Installation
```shell
pip3 install -r requirements.txt
```
### Running scrapper
```shell
scrapy runspider scrapper.py
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
