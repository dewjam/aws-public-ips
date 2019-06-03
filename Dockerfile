FROM python:3.6

RUN pip3 install boto3 \
 && pip3 install awscli

COPY aws-public-ips.py .

CMD python3 aws-public-ips.py
