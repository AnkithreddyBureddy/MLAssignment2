# Pull in dependencies with composer
FROM composer:2.5 as build
COPY composer.json ./
RUN composer install --ignore-platform-reqs

FROM php:8.3.6-cli-alpine3.19

RUN apk update \
    && apk add curl \
# install the PHP extensions we need
    && apk add wget mysql mysql-client php82-mysqli autoconf build-base
RUN docker-php-ext-install mysqli
RUN pecl install opentelemetry protobuf
COPY otel.php.ini $PHP_INI_DIR/conf.d/.
# Copy in the composer vendor files and autoload.php
COPY --from=build /app/vendor /var/www/otel

RUN curl https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar -o /usr/bin/wp-cli && chmod +x /usr/bin/wp-cli

USER www-data:www-data
WORKDIR /var/local/wordpress

RUN php -d memory_limit=512M -f /usr/bin/wp-cli core download

RUN mv wp-content wp-content.bak
RUN mkdir /var/local/wordpress/wp-content
RUN chown www-data:www-data /var/local/wordpress/wp-content
VOLUME /var/local/wordpress/wp-content
COPY ./wp-config.php wp-config.php
COPY ./phpinfo.php phpinfo.php
COPY ./start_wordpress.sh start_wordpress.sh

CMD sh start_wordpress.sh