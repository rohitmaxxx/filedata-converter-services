# Policy Pal document conversion service

## Setup


Create a virtual environment to install dependencies in and activate it:

```sh
$ python -m venv doc_venv
$ source env/bin/activate
```

Then install the dependencies:

```sh
(env)$ pip install -r requirements.txt
```
Note the `(env)` in front of the prompt. This indicates that this terminal
session operates in a virtual environment.

Once `pip` has finished downloading the dependencies:

Run the following command
```sh
(env)$ python main.py
```

## Walkthrough
Navigate to `http://127.0.0.1:8000/get_csv_pdf/` in postman and chosse method POST. After that in body section formdata upload your csv and submit. After submission api will return pdf file with json data.
