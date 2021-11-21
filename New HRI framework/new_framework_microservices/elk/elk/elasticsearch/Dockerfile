# https://github.com/elastic/elasticsearch-docker
FROM docker.elastic.co/elasticsearch/elasticsearch-oss:6.1.0

ADD ./config /usr/share/elasticsearch/config
USER root
RUN chown -R elasticsearch /usr/share/elasticsearch/

# Add your elasticsearch plugins setup here
# Example: RUN elasticsearch-plugin install analysis-icu
