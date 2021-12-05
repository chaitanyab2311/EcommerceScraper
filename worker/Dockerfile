FROM dirkcgrunwald/flair:latest

ADD worker-server.py /

RUN pip3 install --upgrade pika redis jsonpickle 

COPY . /root/sentiment_analysis

CMD cd /root/sentiment_analysis && \
    python3 worker-server.py