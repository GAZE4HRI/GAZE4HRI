# https://github.com/elastic/kibana-docker
FROM docker.elastic.co/kibana/kibana-oss:6.1.0

ADD ./config/ /usr/share/kibana/config
USER root
RUN chown -R kibana /usr/share/kibana/config

# Add your kibana plugins setup here
# Example: RUN kibana-plugin install <name|url>
