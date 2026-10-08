"""
Santander Dev Week 2023 - Pipeline ETL com Python
=================================================

Extração      -> lê os usuários de um arquivo CSV (Alternativa 2 do desafio).
Transformação -> gera uma mensagem personalizada sobre investimentos para cada usuário.
                 Se houver uma chave OPENAI_API_KEY configurada, a mensagem é criada
                 por IA (OpenAI). Caso contrário, usa um gerador local baseado em regras,
                 para que o projeto funcione sem custo e sem depender de nenhuma API.
Carregamento  -> salva os usuários com suas mensagens em um novo CSV e em JSON.

Uso:
    python etl.py
"""

import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).parent
ARQUIVO_ENTRADA = BASE_DIR / "data" / "usuarios.csv"
PASTA_SAIDA = BASE_DIR / "output"


# ---------------------------------------------------------------------------
# 1. EXTRAÇÃO
# ---------------------------------------------------------------------------
def extrair(caminho: Path) -> pd.DataFrame:
    """Lê o CSV de usuários e valida as colunas obrigatórias."""
    df = pd.read_csv(caminho, dtype={"Conta": str, "Agencia": str})
    colunas_obrigatorias = {"UserID", "Nome", "Conta", "Cartao"}
    faltando = colunas_obrigatorias - set(df.columns)
    if faltando:
        raise ValueError(f"Colunas ausentes no CSV: {', '.join(sorted(faltando))}")
    print(f"[Extração] {len(df)} usuários lidos de {caminho.name}")
    return df


# ---------------------------------------------------------------------------
# 2. TRANSFORMAÇÃO
# ---------------------------------------------------------------------------
def mensagem_local(usuario: dict) -> str:
    """Gera uma mensagem personalizada sem IA, com base no saldo do cliente."""
    primeiro_nome = usuario["Nome"].split()[0]
    saldo = float(usuario.get("Saldo", 0) or 0)

    if saldo < 500:
        dica = "comece com pouco: guardar R$ 50 por mês já cria o hábito de investir."
    elif saldo < 5000:
        dica = "monte sua reserva de emergência antes de buscar investimentos mais arriscados."
    else:
        dica = "diversifique: espalhar o dinheiro em vários investimentos reduz o risco."

    return f"{primeiro_nome}, {dica}"


def mensagem_ia(usuario: dict, cliente) -> str:
    """Gera a mensagem com a API da OpenAI (usada apenas se houver chave)."""
    resposta = cliente.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": "Você é um especialista em marketing bancário."},
            {
                "role": "user",
                "content": (
                    f"Crie uma mensagem para {usuario['Nome']} sobre a importância "
                    "dos investimentos (máximo de 100 caracteres)."
                ),
            },
        ],
    )
    return resposta.choices[0].message.content.strip().strip('"')


def criar_cliente_ia():
    """Retorna um cliente OpenAI se a chave existir; senão, None."""
    if not os.getenv("OPENAI_API_KEY"):
        return None
    try:
        from openai import OpenAI

        return OpenAI()
    except ImportError:
        print("[Aviso] Pacote 'openai' não instalado. Usando gerador local.")
        return None


def transformar(df: pd.DataFrame) -> pd.DataFrame:
    """Adiciona a coluna 'Mensagem' com uma notícia personalizada para cada usuário."""
    cliente = criar_cliente_ia()
    origem = "IA (OpenAI)" if cliente else "gerador local"
    print(f"[Transformação] Gerando mensagens com {origem}...")

    mensagens = []
    for usuario in df.to_dict(orient="records"):
        try:
            texto = mensagem_ia(usuario, cliente) if cliente else mensagem_local(usuario)
        except Exception as erro:  # se a API falhar, o pipeline não para
            print(f"  [Aviso] Falha na IA para {usuario['Nome']}: {erro}")
            texto = mensagem_local(usuario)
        mensagens.append(texto)
        print(f"  - {usuario['Nome']}: {texto}")

    resultado = df.copy()
    resultado["Mensagem"] = mensagens
    resultado["GeradoEm"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return resultado


# ---------------------------------------------------------------------------
# 3. CARREGAMENTO
# ---------------------------------------------------------------------------
def carregar(df: pd.DataFrame, pasta: Path) -> None:
    """Salva o resultado em CSV e JSON (formato parecido com o da API original)."""
    pasta.mkdir(exist_ok=True)

    caminho_csv = pasta / "usuarios_com_mensagens.csv"
    df.to_csv(caminho_csv, index=False, encoding="utf-8-sig")

    usuarios_json = [
        {
            "id": int(linha["UserID"]),
            "name": linha["Nome"],
            "account": {"number": linha["Conta"], "agency": linha.get("Agencia")},
            "card": {"number": linha["Cartao"], "limit": linha.get("LimiteCartao")},
            "news": [{"description": linha["Mensagem"]}],
        }
        for linha in df.to_dict(orient="records")
    ]
    caminho_json = pasta / "usuarios_com_mensagens.json"
    caminho_json.write_text(
        json.dumps(usuarios_json, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"[Carregamento] Arquivos salvos em: {caminho_csv.name} e {caminho_json.name}")


# ---------------------------------------------------------------------------
# Execução do pipeline
# ---------------------------------------------------------------------------
def main() -> None:
    dados = extrair(ARQUIVO_ENTRADA)
    dados_transformados = transformar(dados)
    carregar(dados_transformados, PASTA_SAIDA)
    print("Pipeline ETL concluído com sucesso!")


if __name__ == "__main__":
    main()
