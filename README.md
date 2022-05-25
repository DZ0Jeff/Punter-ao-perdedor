# Punter ao perdedor

Programa que verifica se existem odds baixas em partidas futuras de tênis de mesa, se existem:

- Verifica ate achar o placar de 2-0
- Sinaliza no telegram

------

Tenha certeza que tenha o python instalado, [Clique aqui para instalar]("https://www.python.org/")
Tenha certeza que tenha o git instalado, [Clique aqui para instalar]("https://git-scm.com/downloads")

``` cmd
git clone
cd punter-ao-perdedor	
```

### (Recomentado) instalando o ambiente


Se você não tiver virtualenv instalado, digite:

```python
    pip install virtualenv
```

## Instalação
------

Faça a criação do bot do telegram digitando @botmaster

com o token de acesso, crie um arquivo ".env" com o seguinte conteudo:

``` env
TELEGRAM_TOKEN="Telegram token"
TELEGRAM_CHAT_ID="seu telegram id"
```

#### telegram chat id

para conseguir o mesmo, acesse o telegram e clique em "Meu chat", depois clique em "Chat" e depois "ID do chat" ou digite @getidsbot para colocar o id do chat

(aqui no diretório possui um arquivo ".env.example" com o exemplo)

Então:

```python
    python -m venv venv && .\venv\scripts\activate 
```

Se for terminal:

```python
    python -m venv venv && source venv/bin/activate 
```

Instalando dependêncies:

```python
    pip install -r requirements.txt
```

Esta pronto para uso!

Digite:

```python
    python main.py
```


## Maiss informações

consulte ao diretório "docs" para mais informações
