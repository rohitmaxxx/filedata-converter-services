FROM python:3.9-alpine

WORKDIR /home/

# COPY ./scripts ./
# COPY main.py ./
# COPY requirements.txt ./
# Earlier above was written to copy but 'COPY ./scripts ./' was not working properly so below used
COPY . ./

RUN pip install -r requirements.txt

CMD ["python", "main.py"]