FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY evi3.py .

CMD [ "python", "./evi3.py" ]

# pip install --no-cache-dir -r requirements.txt
# docker build -t uanl/facpya .
# docker run -it --rm --name my-running-app uanl/facpya
