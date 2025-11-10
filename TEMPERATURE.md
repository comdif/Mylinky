Pour avoir un outil complet et contextuel de mesure j'ai ajouté deux sondes de température de chez https://ipthermometer.eu

Assez facile a intégrer dans le script avec la librairie urllib2 a appeler avec: import urllib.request as urllib2 sur ma version de python

Rajouter des champs decimaux (3,1) dans la db mysql, les déclarer dans linky.py et ensuite ajouter dans le while de main.py:

    resptemp = urllib2.urlopen('http://ip_thermometre1/t')
    tempout = resptemp.read()
    resptempin = urllib2.urlopen('http://ip_thermometre2/t')
    tempin = resptempin.read()

et les faire remonter dans la dB

Voir image dashboar-temp.jpg https://raw.githubusercontent.com/comdif/Mylinky/refs/heads/main/dashboar-temp.jpg
