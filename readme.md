
# Análise de Desempenho e Dimensionamento de Recursos de uma API REST

Este projeto contém uma aplicação de exemplo — uma API RESTful com FastAPI em Python — juntamente com uma infraestrutura dockerizada para testes de desempenho e dimensionamento de recursos (CPU e RAM) sob diferentes cargas de trabalho.

## Funcionalidades

- API REST com operações CRUD para gerenciamento de Itens
- Contêineres Docker para API e banco PostgreSQL
- Testes de carga com Apache JMeter
- Avaliação de impacto da CPU e RAM no desempenho
- Relatórios com métricas: tempo de resposta, throughput e taxa de erros

## Tecnologias Utilizadas

- Python 3.9  
- FastAPI  
- PostgreSQL  
- Docker + Docker Compose  
- Apache JMeter

## Instalação e Execução

### Pré-requisitos

- Docker Desktop (ou Docker Engine + Docker Compose)
- Java (JDK ou OpenJDK)
- [Apache JMeter](https://jmeter.apache.org/) instalado e descompactado

### 1. Clone o Repositório

```bash
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO
```

### 2. Estrutura do Projeto

```
.
├── main.py               # Código da API FastAPI
├── Dockerfile            # Imagem da API
├── requirements.txt      # Dependências Python
└── docker-compose.yml    # Orquestração API + DB
```

### 3. Subindo os Contêineres

```bash
docker-compose up --build -d
```

Verifique se os serviços estão ativos:

```bash
docker-compose ps
```

Acesse a documentação da API:  
[http://localhost:8000/docs](http://localhost:8000/docs)

## Configuração de Recursos

No arquivo `docker-compose.yml`, edite os limites de CPU/RAM no serviço da API:

```yaml
api:
  deploy:
    resources:
      limits:
        cpus: '1.0'
        memory: 512M
```

Esses valores devem ser ajustados para cada cenário de teste.

## Testes de Desempenho com JMeter

### 1. Criando o Plano de Teste

Abra o JMeter e configure os seguintes elementos:

**Thread Group**  
Adicione: `Test Plan > Add > Threads (Users) > Thread Group`

**HTTP Request - Criar Item (POST /items/)**

- Method: POST  
- Path: `/items/`  
- Body Data:

```json
{
  "nome": "Item JMeter ${__Random(1,10000,)}",
  "descricao": "Teste de Carga",
  "preco": 10.00
}
```

**HTTP Request - Listar Itens (GET /items/)**

- Method: GET  
- Path: `/items/`

**HTTP Header Manager**

Adicione o cabeçalho:

```
Content-Type: application/json
```

**Listeners Recomendados**

- View Results Tree  
- Summary Report  
- Aggregate Report

### 2. Cenários de Carga

| Cenário        | Threads | Ramp-up | Duração | CPU   | RAM   |
|----------------|---------|---------|---------|-------|--------|
| Baixa Carga    | 5       | 10s     | 60s     | 0.5   | 128M   |
| Média Carga    | 20      | 20s     | 120s    | 1.0   | 256M   |
| Alta Carga     | 50      | 30s     | 180s    | 1.0   | 512M   |

### 3. Execução dos Testes

Para cada cenário:

1. Pare os contêineres existentes:

```bash
docker-compose down
```

2. Ajuste CPU/RAM no `docker-compose.yml`

3. Suba os contêineres:

```bash
docker-compose up --build -d
```

4. Monitore recursos em tempo real:

```bash
docker stats
```

5. Execute o teste no JMeter e salve os resultados dos relatórios em `.csv`.

## Resultados e Análise

Os arquivos de saída (CSV) dos relatórios devem ser analisados com base em:

- Tempo médio de resposta
- Throughput (requisições por segundo)
- Taxa de erros
- Gargalos detectados (CPU, RAM ou lógica da aplicação)
- Recomendação de alocação ideal de recursos

## Contribuições

Contribuições são bem-vindas!  
Abra uma issue ou envie um pull request com melhorias, sugestões ou correções.

## Licença

Este projeto está licenciado sob a Licença MIT.  
Veja o arquivo `LICENSE` para mais informações.
