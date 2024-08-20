# Chat TCP

Este projeto implementa um servidor de chat que gerencia a comunicação entre clientes, permitindo o envio de mensagens individuais e em grupo. O servidor gerencia o registro de novos clientes, o armazenamento de mensagens não entregues e a confirmação de leitura.

## Funcionalidades

- **Registrar Cliente:** Registra um novo cliente no sistema e gera um ID único.
- **Conectar Cliente:** Conecta um cliente ao servidor e envia quaisquer mensagens não lidas para o cliente.
- **Enviar Mensagem:** Envia mensagens entre clientes conectados. Se o destinatário não estiver conectado, a mensagem é armazenada até que ele se conecte.
- **Confirmar Leitura:** Envia uma confirmação de leitura de uma mensagem recebida.
- **Criar Grupo:** Cria grupos de chat com múltiplos membros, permitindo a comunicação em grupo.

## Estrutura do Código

### Classe `Server`

- **Atributos:**
  - `host` e `port`: Configurações de host e porta para o servidor.
  - `created_clients`: Contador para IDs de clientes.
  - `connected_clients`: Dicionário de clientes conectados.
  - `unreceived_messages`: Dicionário de mensagens não lidas, armazenadas por ID de cliente.
  - `groups`: Dicionário de grupos de chat.
  - `codes`: Dicionário que mapeia códigos de requisição para métodos de processamento.

- **Métodos Principais:**
  - `register_client`: Registra um novo cliente e envia o ID gerado.
  - `connect_client`: Conecta um cliente e envia mensagens não lidas.
  - `send_message`: Envia uma mensagem de um cliente para outro.
  - `confirm_read`: Envia uma confirmação de leitura de mensagem.
  - `create_group`: Cria um novo grupo de chat.
  - `receive_unreceived_messages`: Envia mensagens não lidas para um cliente que acabou de se conectar.
  - `run`: Inicia o servidor e aceita conexões de clientes.
  - `handle_client`: Lida com a comunicação de um cliente específico.
  - `handle_request`: Processa requisições dos clientes.
  - `disconnect_client`: Desconecta um cliente e atualiza a lista de clientes conectados.

## Como Executar

1. **Instalação de Dependências:**
   Certifique-se de ter as dependências necessárias instaladas. Por exemplo, a biblioteca `socket` e `threading` são padrão em Python, mas você deve garantir que o Python 3.x esteja instalado.

2. **Configuração:**
   No arquivo `config/settings.py`, configure as variáveis `HOST` e `PORT` conforme necessário.

3. **Execução:**
   Execute o servidor utilizando o comando:
   ```bash
   python server.py
