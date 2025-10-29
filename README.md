# Mylinky
Voir et maitriser sa consommation électrique via son compteur Linky.
Voir les appareils énergivores et les plus sobres ou tout simplement pouvoir faire
des études comparatives post isolation ou autre.

Le système est entièrement programmé pour les abonnements Heures pleines / Heures creuses, si vous cherchez
un script adapté a l'abonnement BASE (tarif fixe) vous le trouverez sur ce dépôt https://github.com/Ailothaen/linky dont je me suis inspiré.

Le Matériel nécessaire pour réaliser votre Télémétrie est ici: https://www.tindie.com/products/hallard/micro-teleinfo-v30 et coute une vingtaine d'euros.

Pour le serveur vous pouvez utiliser un Raspberry 4 ou 5, je vous déconseille vivement le 3 qui n'est pas assez puissant, même si ca semble fonctionner
il est trop lent et pas assez puissant, lors de mes tests j'ai vu des trames corrompues.
Pour ma part je l'ai installé sous forme de VM sur un miniserveur acheté sur Aliexpress assez musclé ou j'ai un hyperviseur VmWare ESXI
et qui me sert a faire tourner également d'autres VMs.

Pour commencer on installe Ubuntu 22.04 server
Ensuite comme je ne suis pas fan des sudo et que je travaille toujours en root je fais:

    sudo passwd root
        
Ensuite je passe en root

    su root
        
S'il n'est pas déjà installé installer ssh server

    apt install openssh-server
        
J'édite le fichier de config de ssh pour pouvoir me connecter en Root

    nano /etc/ssh/sshd_config
        
Cherchez la ligne qui commence par #set PermitRootLogin, décommentez la et transformez la en
set PermitRootLogin yes
On redémarre SSH

    service ssh restart
  
ON plug la clef USB teleinfo et on controle qu'elle est reconnue.

    lsusb
    
Vous devez voir "QinHeng Electronics uTinfo-V3.0", la clef branchée sur I1 et I2 du compteur doit clignoter.
OK on met a jour la machine et on installe ce qui vas être nécessaire.

    apt update && apt upgrade
    apt install mysql-server
    systemctl enable --now mysql
    apt install python3 python3-yaml libyaml-0-2 python3-mysqldb python3-pymysql python3-mysqldb python3-serial.
    mkdir /usr/src/linky
    mkdir /usr/src/linky/logs/
    touch /usr/src/linky/logs/linky.log
    chmod -R 755 /usr/src/linky
    
Plus qu'a copier les 3 fichiers dans /usr/src/linky et le fichier linky.service dans /etc/systemd/system/
Créer l'utilisateur et la database:

    mysql
    mysql> CREATE DATABASE mylinky;
    mysql> CREATE USER 'linky'@'localhost' IDENTIFIED BY 'password';
    mysql> GRANT ALL PRIVILEGES ON linky.* TO 'linky'@'localhost';
    mysql> FLUSH PRIVILEGES;

Lancez ensuite le service linky.

    systemctl daemon-reload
    systemctl enable linky
    systemctl start linky
    systemctl status linky

Installez maintenant grafana-server:

    cd /usr/src
    wget https://dl.grafana.com/grafana/release/12.2.0/grafana_12.2.0_17949786146_linux_amd64.deb
    dpkg -i grafana_12.2.0_17949786146_linux_amd64.deb
    systemctl daemon-reload
    systemctl enable grafana-server
    systemctl start grafana-server
    systemctl status grafana-server

Loguez-vous ensuite sur http://votreip:3000
Créez la Data-source MYSQL indiquez +00 en time zone.
Importez ensuite le fichier json et vous devriez avoir un beau dashboard avec vos datas.
