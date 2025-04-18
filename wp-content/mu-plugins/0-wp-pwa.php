<?php
    add_filter( 'comments_open', function(){
        return false;
    });
    update_option("permalink_structure","/%postname%/");

