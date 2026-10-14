"""
O "sentido" de cada notícia como um vetor de números (embedding), com um
modelo pequeno que roda aqui mesmo, sem IA paga e sem internet além do
download do modelo. Duas notícias sobre o mesmo assunto têm vetores
parecidos mesmo com palavras diferentes, e mesmo em línguas diferentes:
"GTA 6 será lançado no PC no 1º trimestre de 2027" e "GTA 6's PC release
date is set for Q1 2027" ficam a 0,92 de semelhança (de 0 a 1).

É o que deixa o agrupamento (agrupar.py) juntar português e inglês, e
achar a mesma história contada com outras palavras.

Modelo: paraphrase-multilingual-MiniLM-L12-v2 (50+ línguas, 384 números
por notícia, ~220 MB), pela biblioteca fastembed (ONNX, sem PyTorch).
Na máquina do GitHub, ~25 notícias por segundo: por isso cada vetor é
calculado uma vez só e guardado em vetores_noticias (sql/045), pela URL.
Só servem pra janela do agrupamento: os de mais de 4 dias são apagados.
"""
import os
from pathlib import Path

import numpy as np
from psycopg2.extras import execute_values

MODELO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DIMENSOES = 384
CARACTERES_DO_TEXTO = 300
DIAS_GUARDADOS = 4
# O workflow guarda essa pasta entre as execuções (actions/cache): sem
# ela, seriam 220 MB baixados toda hora
PASTA_DOS_MODELOS = os.environ.get("MODELOS_DIR") or str(Path.home() / ".cache" / "daily-paper-modelos")

_modelo = None


def texto_da_noticia(titulo, texto):
    return f"{titulo}. {(texto or '')[:CARACTERES_DO_TEXTO]}"


def vetorizar(textos):
    """Matriz (len(textos) x 384), cada linha com tamanho 1 (aí a semelhança
    entre duas notícias é só o produto escalar)."""
    global _modelo
    if not textos:
        return np.zeros((0, DIMENSOES), dtype=np.float32)
    if _modelo is None:
        from fastembed import TextEmbedding  # só carrega se tiver o que calcular

        _modelo = TextEmbedding(MODELO, cache_dir=PASTA_DOS_MODELOS)
    matriz = np.array(list(_modelo.embed(textos, batch_size=64)), dtype=np.float32)
    return matriz / np.maximum(np.linalg.norm(matriz, axis=1, keepdims=True), 1e-9)


def carregar(conn, urls):
    """{url: vetor} dos que já foram calculados."""
    with conn.cursor() as cur:
        cur.execute("select url, vetor::real[] from vetores_noticias where url = any(%s)", (list(urls),))
        linhas = cur.fetchall()
    conn.commit()
    return {url: np.array(v, dtype=np.float32) for url, v in linhas}


def gravar(conn, novos):
    """novos: {url: vetor}. Apaga os velhos na mesma transação."""
    with conn.cursor() as cur:
        if novos:
            execute_values(
                cur,
                "insert into vetores_noticias (url, vetor) values %s on conflict (url) do nothing",
                [(url, "[" + ",".join(f"{x:.5f}" for x in v) + "]") for url, v in novos.items()],
                template="(%s, %s::extensions.vector)",
                page_size=200,
            )
        cur.execute(
            "delete from vetores_noticias where criado_em < now() - make_interval(days => %s)", (DIAS_GUARDADOS,)
        )
    conn.commit()
