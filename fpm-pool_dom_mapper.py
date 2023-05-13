#!/usr/bin/env python3
import subprocess
import re
import os
def get_domain_pool_mapping():
    print('\033[38;5;22m=\033[38;5;28m=\033[38;5;34m=\033[38;5;40m=\033[38;5;46m= List of PHP-FPM pools and their domain mappings \033[38;5;46m=\033[38;5;40m=\033[38;5;34m=\033[38;5;28m=\033[38;5;22m=\033[0m')
    # Get list of Apache configuration files
    php_fpm_file = ''
    cmd = "apachectl -S 2>/dev/null | grep -oP '\((.*?.)\)' | grep -oP '.*(?=:)' | tr -d '('| sort|uniq"
    config_files = subprocess.check_output(cmd, shell=True, universal_newlines=True).splitlines()

    # Get the list of running PHP-FPM Pools
    cmd = "ps -ef | awk '/php-fpm[:] pool/ {print $NF}' | sort|uniq"
    pools = subprocess.check_output(cmd, shell=True, universal_newlines=True).splitlines()

    distro = subprocess.getoutput("cat /etc/*-release| grep '^ID='|cut -d'=' -f2")
    if 'ubuntu' in distro:
        cmd = "ls /etc/apache2/conf-available/php*-fpm.conf"
        php_fpm_file = subprocess.getoutput(cmd)
        cmd = "apachectl -S 2>/dev/null | awk '/namevhost/ {print $5}' | tr -d '()' | grep -oP '.*(?=:)' | sort | uniq"
        config_files = subprocess.check_output(cmd, shell=True, universal_newlines=True).splitlines()

    else:

        file_path = '/etc/httpd/conf.d/php.conf'
        try:
            with open(file_path) as f:
                file_content = f.read()
                cmd = f"grep -o -P '^\s*SetHandler\s+\"proxy:.*\"' {file_path}"
                try:
                    output = subprocess.check_output(cmd, shell=True, universal_newlines=True)
                    php_fpm_file = '/etc/httpd/conf.d/php.conf'
                except subprocess.CalledProcessError:
                    pass
        except:
            pass



    # Find PHP-FPM pool name for each domain in config files
    domain_pool_map = {}
    for pool in pools:
        domain_pool_map[pool] = []
        for config_file in config_files:
            with open(config_file) as f:
                config_content = f.read()
            cmd = f"grep -o -P '^\s*SetHandler\s+\"proxy:.*\"' {config_file}"
            try:
                output = subprocess.check_output(cmd, shell=True, universal_newlines=True)
            except subprocess.CalledProcessError:
                #print(f"An error occurred while running command: {cmd}")
                continue

            if f"{pool}.sock" in output:
                domain_match = re.search(r'ServerName\s+(?P<domain>[^\s]+)', config_content)
                domain = domain_match.group('domain')
                domain_pool_map[pool].append(domain)

        if domain_pool_map[pool]:
            print(f"\033[1;36m--- {pool} ---\033[0m")
            for domain in domain_pool_map[pool]:
                print(f" - {domain}")
            print()

        else:
            if pool == "www" and os.path.isfile(php_fpm_file) and os.path.getsize(php_fpm_file) > 0:

                print(f"\033[36m\033[1m--- {pool} ---\033[0m")
                print(f" - www is the default pool")
                print()
                print(f"\033[31m\033[1m The file {php_fpm_file} exists, it means that the default pool for all domains will be 'www', unless any domains define their own pool in their respective virtual host configuration files.\033[0m")

            else:
                print(f"\033[1;36m--- {pool} ---\033[0m")
                print(f" - Not in use")

get_domain_pool_mapping()
