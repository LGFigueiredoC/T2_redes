# Transmissão Contínua de Áudio
## Alunos
Artur Noack de Souza

Luiz Gabriel Figueiredo de Carvalho

## Descrição
Esse projeto implementou uma transmissão de áudio contínua por TCP, tanto ao vivo quanto carregando um arquivo já gravado. Quando um cliente se conecta a esse servidor, ele pode escolher qual opção de transmissão ele irá escolher, bem como pode controlar a reprodução desse áudio escolhido, de forma independente de outros clientes conectados.

Essa transmissão ocorre de forma sincronizada entre clientes, por meio de threads que atendem a cada um independentemente, e ocorre de forma criptografada, por meio da tecnologia TLS.

Após a reprodução do áudio, o cliente pode escolher se irá salvar o áudio ou não.

## Tecnologias Utilizadas
O programa foi todo escrito em Python, e foram utilizadas as bibliotecas Pygame, Pyaudio, Threading, SSL, Socket, Asyncio, Time e Wave.

## Como Executar
Primeiro, deve-se baixar os requerimentos descritos no arquivo "requirements.txt".

Para executar o programa, basta clonar o repositório em uma pasta. Abrindo o terminal nessa pasta, pode-se executar tanto o cliente quanto o servidor, e pode-se colocar quantos arquivos .wav quanto quiser na pasta "audio".

Para executar como servidor, basta, em um terminal aberto na pasta, executar:

openssl req -newkey rsa:2048 -nodes -keyout server.key -x509 -days 365 -out server.crt

para criar a chave de criptografia. Depois, execute:
 
python3 main_server.py
 
Executando como servidor, pode-se escolher as opções de listar as conexões ativas no momento ou fechar o servidor.

Para executar como cliente, basta, no código, alterar o ip do host na main do cliente e, em um terminal aberto na pasta, executar "python3 main.client.py". Executando como cliente, deverá ser feita sua autenticação, com login e senha.

Acesso padrão cadastrado:
    Login: user
    Senha: password

Mais acessos podem ser criados no campo users da classe tcp_server em server.py.

Então, pode-se escolher 4 opções:

A transmissão ao vivo, onde há a opção de salvar ou não essa transmissão, e a opção de escolher o nome do arquivo. 

Ler um arquivo .wav do servidor, dado que você saiba quais arquivos estão salvos nele.

Listar todos os arquivos de audio salvos no servidor.

Terminar a conexão.

Em todas as escutas, pode-se dar pause, play e stop nesse audio, de forma independente dos outros clientes.

## Como Testar
Para testar o programa, basta executar o servidor e os clientes na mesma rede.

## Funcionalidades Implementadas
Foram implementadas todas as funcionalidades padrão pedidas, bem como os incrementos. Além disso, foi implementada uma pequena interface no terminal para controle das funcionalidades já explicadas.

## Possíveis Melhorias Futuras