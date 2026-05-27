FROM python:3.11-slim

# Oracle Instant Client (necessário para cx_Oracle)
RUN apt-get update && apt-get install -y libaio1 wget unzip && \
    wget -q https://download.oracle.com/otn_software/linux/instantclient/2112000/instantclient-basiclite-linux.x64-21.12.0.0.0dbru.zip && \
    unzip instantclient-basiclite-linux.x64-21.12.0.0.0dbru.zip -d /opt/oracle && \
    rm instantclient-basiclite-linux.x64-21.12.0.0.0dbru.zip && \
    echo /opt/oracle/instantclient_21_12 > /etc/ld.so.conf.d/oracle.conf && ldconfig

ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_21_12

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
