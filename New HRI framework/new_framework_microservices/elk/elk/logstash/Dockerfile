# https://github.com/elastic/logstash-docker
FROM docker.elastic.co/logstash/logstash-oss:6.1.0

ADD ./config/logstash.yml /usr/share/logstash/config/logstash.yml
ADD ./pipeline /usr/share/logstash/pipeline
USER root
#RUN chmod -R 755 /usr/share/logstash/
RUN chown -R logstash: /usr/share/logstash/config/logstash.yml /usr/share/logstash/pipeline

# Add your logstash plugins setup here
# Example: RUN logstash-plugin install logstash-filter-json
