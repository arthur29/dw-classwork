#Trabalho de DW

Você vai precisar de instalar a biblioteca names,sqlalchemy e MySQL-connector-python
Abaixo explica como instalar o virtualenv para nao poluir seu computador

https://www.linode.com/docs/development/python/create-a-python-virtualenv-on-ubuntu-1610/

Logo após instale as libs:
* names `pip3 install names`
* sqlalchemy `pip3 install sqlalchemy`
* MySQL-connector-python `pip3 install MySQL-connector-python`

ALEM DISSO:

Caso seu MySQL tenha sido configurado com algum usuario, senha ou esteja em outra maquina e você quira acessar pela rede, basta passar as variaveis de sistema com os valores correspondentes que ele acessará. Exemplo contendo os três aspectos:

`MYSQL_HOST=some_host MYSQL_USER=some_user MYSQL_PASSWORD=some_passoword python3 create.py`

Para auxiliar caso queira subir de forma rápida o banco de dados e também um cliente web, seguem abaixo os comandos com o docker para fazer isso:

`docker run -d -p 3306:3306 --name mysql -e MYSQL_DATABASE=dw -e MYSQL_ALLOW_EMPTY_PASSWORD=yes mysql:5.6`
`docker run --name myadmin -d --link mysql:db -e MYSQL_ROOT_PASSWORD=`` -p 8080:80 phpmyadmin/phpmyadmin`

Então os passos para ter as tabelas com o conteúdo requerido pelo professor são:

* Se certificar que o banco existe: `python3 create.py`
* Criar as tabelas: `python3 migrate.py`
* Popular as tabelas utilizando o CSV que veio a partir do XLSX: `python3 populate.py`
