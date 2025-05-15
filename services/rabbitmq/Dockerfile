FROM rabbitmq:4.0.7-management

# Expose the RabbitMQ port
EXPOSE 5672

# Expose the RabbitMQ management plugin port
EXPOSE 15672
# This is disabled for security reasons for now

# Copy the logging conf file
RUN mkdir -p /etc/rabbitmq/conf.d
RUN chown -R rabbitmq:rabbitmq /etc/rabbitmq/conf.d
COPY 20-logging.conf /etc/rabbitmq/conf.d