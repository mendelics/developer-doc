# Entrega de resultado de testes de COVID

## Objetivo

Este documento tem o objetivo de apresentar à empresa parceira uma forma de integrar seu sistema ao sistema de resultados da Mendelics, viabilizando o recebimento de resultados dos testes de COVID de forma automatizada.

Nas seções a seguir apresentamos todos os elementos necessários para que se possa efetuar a integração corretamente, além de apresentar as configurações para o ambiente de homologação onde é possível efetuar testes de integração.

Esta forma de recebimento de resultado não substitui a notificação de resultados por e-mail ou o acompanhamento através de nossos sistemas web.

Oferecemos um script em **Python** contendo as etapas necessárias para apoiar a integração com o sistema. Outros exemplos, usando outras linguagens de programação, estão disponíveis na documentação do Pub/Sub.

## Premissas Básicas

Utilizamos como plataforma de envio de resultados o sistema de mensageria da **Google Cloud Platform (GCP)**, chamado de **Cloud Pub/Sub**, neste documento referenciado somente como Pub/Sub. Para mais detalhes sobre o uso e funcionamento do Pub/Sub, recomendamos a leitura da [documentação oficial](https://cloud.google.com/pubsub/docs/overview).

Os resultados são enviados através de mensagens que ficam disponíveis para o recebimento no **Pub/Sub** por nossos parceiros.

### Formato dos resultados

As mensagens contêm o seguinte dado estruturado em formato JSON.

```json
{
  "sample_code": "CODIGO",
  "type": "TIPO_DE_TESTE",
  "result": "RESULTADO_TESTE"
}
```

A seguir apresentamos o valor de cada campo.

- `sample_code`: O código do teste realizado (ex: COV00248202490).
- `type`: O tipo do teste realizado (ex: “covid”).
- `result`: O resultado do teste, podendo assumir os valores:
  - `positive` (caso positivo)
  - `negative` (caso negativo)
  - `non_compliance` (recusa do exame pela triagem por problema com a amostra).

### Garantia de envio de mensagem

Todo teste terá seu resultado notificado através do envio de pelo menos uma mensagem para o Pub/Sub.

> Devido a limitações da ferramenta, não garantimos a unicidade da mensagem de resultado. Isto significa que para um único teste podemos enviar mais de uma vez o mesmo resultado.

### Expiração da mensagem

Cada mensagem permanece ativa no Pub/Sub durante sete dias, sendo removida automaticamente após este período.

Caso seja necessário ver algum outro resultado de teste em período pregresso, recomendamos utilizar a ferramenta [Corporativo da Mendelics](https://corporativo.mendelics.com.br/).

## Detalhamento Técnico

Dentro do Pub/Sub existem três entidades que serão mencionadas com frequência neste manual e, portanto, vamos fazer uma rápida apresentação delas. Em caso de dúvidas ou necessidade de uma leitura mais completa, recomendamos a [documentação oficial](https://cloud.google.com/pubsub/docs/overview).

Uma mensagem é enviada para um **_tópico_**, que é um assunto de interesse para o qual um **_publisher_** manda mensagens para serem consumidas por **_subscribers_**.

Um **_publisher_** é um usuário autenticado para enviar mensagens para um determinado tópico. Em nosso caso, a Mendelics é o **_publisher_** das mensagens de resultado.

Um **_subscriber_** é um usuário autenticado para receber mensagens de um determinado tópico. Em nosso caso, os sistemas construídos pelo cliente são o **_subscriber_**.

Para autenticar um **_subscriber_** a um tópico, são necessárias algumas informações.

- Um arquivo com a chave de acesso para a GCP, que chamaremos de `key.json`;
- O identificador do projeto que hospeda o tópico
- O identificador do subscriber acessando o tópico

A seguir, detalhamos cada uma dessas informações.

### Chave de acesso

O arquivo `key.json` possui a chave de acesso necessária para realizar a autenticação na GCP e liberar o acesso ao **Pub/Sub**. Portanto, este arquivo deve ser armazenado em um local seguro, cujo acesso é restrito à aplicações e pessoas autorizadas a receberem os resultados de covid.

Durante o processo de integração, a Mendelics irá gerar uma chave de acesso e enviar para a empresa consumidora.

### Identificador do projeto

O identificador da aplicação interna da Mendelics.

### Identificador do subscriber

O identificador do subscriber, gerado pela Mendelics para a empresa parceira. Este identificador será fornecido juntamente com o documento durante o processo de integração.

### Confirmando o recebimento da mensagem

Com suas credenciais, o sistema construído pela empresa parceira se conectará ao seu tópico do **Pub/Sub** e, então, poderá requisitar mensagens.

Quando uma mensagem é recebida, é necessário enviar ao Pub/Sub uma confirmação de recebimento, chamada de **_ack_**. Ao receber este **_ack_** o Pub/Sub entende que o **_subscriber_** recebeu e interpretou corretamente a mensagem do tópico e irá remover a mensagem daquele tópico. Caso não receba o **_ack_** no tempo determinado, a mensagem ficará disponível no Pub/Sub para que o sistema construído pela empresa parceira possa tentar receber a mensagem e enviar o ack novamente para o Pub/Sub.

Por padrão o Pub/Sub aguarda dez segundos pelo recebimento do **_ack_**.

### Ambiente de homologação

Oferecemos um Pub/Sub de homologação, com um tópico contendo testes falsos e resultados, para que nossos parceiros possam testar a integração e o recebimento de mensagens.

Como a mensagem possui um tempo para expirar, caso seja necessário uma maior quantidade de resultados disponibilizados no tópico, entre em contato conosco.

Configurações:

- identificador do projeto: `api-mendelics-dev`
- identificador do subscriber: o mesmo que para produção
- tópico: `homolog-result`

### Ambiente de produção

Utilize estes dados para o ambiente de produção.

Configurações:

- identificador do projeto: `api-mendelics`
- identificador do subscriber: será recebido com este documento
- tópico: será recebido com este documento
