FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    proj-bin \
    proj-data \
    gcc \
    openjdk-17-jdk-headless \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

ENV ICEBERG_VERSION=1.6.1
ENV SPARK_ICEBERG_JAR=/opt/spark-jars/iceberg-spark-runtime-3.5_2.12-${ICEBERG_VERSION}.jar

RUN mkdir -p /opt/spark-jars && \
    curl -fsSL -o ${SPARK_ICEBERG_JAR} \
    "https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/${ICEBERG_VERSION}/iceberg-spark-runtime-3.5_2.12-${ICEBERG_VERSION}.jar"

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-cache search openjdk

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] my current docker file