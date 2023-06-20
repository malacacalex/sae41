docker run --rm --network=host -h=127.0.0.1 deb-cli-1
mysql -u sqlflask -p’sqlflask’ -h 127.0.0.1 -P 3306