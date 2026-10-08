# Santander Dev Week 2023 — Pipeline ETL com Python

Projeto do desafio da **DIO** para praticar o fluxo **ETL (Extração, Transformação e Carregamento)** com Python e Pandas.

Como a API pública da Santander Dev Week pode ficar fora do ar, este projeto usa a **Alternativa 2** do desafio: os dados dos clientes (Nome, Conta e Cartão) ficam em um arquivo CSV.

## Como o pipeline funciona

```
data/usuarios.csv  ──►  EXTRAÇÃO  ──►  TRANSFORMAÇÃO  ──►  CARREGAMENTO  ──►  output/
                       (pandas)       (mensagem por IA       (CSV + JSON)
                                       ou gerador local)
```

| Etapa | O que faz |
|---|---|
| **Extração** | Lê `data/usuarios.csv` e valida se as colunas obrigatórias existem. |
| **Transformação** | Cria uma mensagem personalizada sobre investimentos para cada cliente. Com a variável `OPENAI_API_KEY` configurada, a mensagem é gerada por IA; sem ela, um gerador local cria a mensagem conforme o saldo do cliente. Se a IA falhar, o pipeline continua com o gerador local. |
| **Carregamento** | Salva o resultado em `output/usuarios_com_mensagens.csv` e `output/usuarios_com_mensagens.json` (no mesmo formato da API original, com o campo `news`). |

## Como executar

```bash
pip install -r requirements.txt
python etl.py
```

Ou abra o notebook `SantanderDevWeek2023_ETL.ipynb` e execute as células em ordem.

### Opcional: usar IA para gerar as mensagens

```bash
pip install openai
# Windows (PowerShell)
$env:OPENAI_API_KEY="sua-chave-aqui"
# Linux / macOS
export OPENAI_API_KEY="sua-chave-aqui"

python etl.py
```

> Nunca coloque sua chave de API dentro do código ou no GitHub.

## Exemplo de saída

```
[Extração] 6 usuários lidos de usuarios.csv
[Transformação] Gerando mensagens com gerador local...
  - Ana Souza: Ana, monte sua reserva de emergência antes de buscar investimentos mais arriscados.
  - Bruno Lima: Bruno, comece com pouco: guardar R$ 50 por mês já cria o hábito de investir.
  ...
[Carregamento] Arquivos salvos em: usuarios_com_mensagens.csv e usuarios_com_mensagens.json
Pipeline ETL concluído com sucesso!
```

## Estrutura

```
├── data/
│   └── usuarios.csv                    # dados de entrada (fictícios)
├── output/                             # gerado pelo pipeline
├── etl.py                              # pipeline ETL
├── SantanderDevWeek2023_ETL.ipynb      # versão notebook
├── requirements.txt
└── README.md
```

## Tecnologias

- Python 3
- Pandas
- OpenAI API (opcional)

## Aprendizados

- O ETL separa responsabilidades: cada etapa tem uma função e pode ser trocada sem afetar as outras (por exemplo, trocar o CSV por uma API na extração).
- Uma boa prática é prever falhas de fontes externas, por isso o pipeline tem um plano B quando a IA não está disponível.

## Referências

- [Notebook original — Santander Dev Week 2023](https://github.com/falvojr/santander-dev-week-2023)
- [API da Santander Dev Week 2023](https://github.com/digitalinnovationone/santander-dev-week-2023-api)

---
Desenvolvido por **Oscar do Carmo Junior** no bootcamp da [DIO](https://www.dio.me/).
