#!/bin/sh
if [ ! -d "wp-content/index.php" ]; then
    cp -r wp-content.bak/* wp-content/
    curl -L https://github.com/WordPress/sqlite-database-integration/archive/refs/heads/develop.zip -o /tmp/sqlite.zip
    mkdir -p wp-content/mu-plugins
    unzip /tmp/sqlite.zip -d wp-content/mu-plugins
    echo '<?php require_once __DIR__ . "/sqlite-database-integration-develop/load.php";' > wp-content/mu-plugins/0-sqlite.php
    cat << EOF > wp-content/mu-plugins/0-wp-pwa.php
<?php
    add_filter( 'comments_open', function(){
        return false;
    });
    update_option("permalink_structure","/%postname%/");

EOF
    cp wp-content/mu-plugins/sqlite-database-integration-develop/db.copy wp-content/db.php
    sed -i "s/\/plugins\/sqlite-database-integration/\/mu-plugins\/sqlite-database-integration-develop/" wp-content/db.php
fi
php -S 0.0.0.0:8000