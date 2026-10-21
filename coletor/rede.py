"""
Como o coletor baixa feeds e páginas: direto, das máquinas do GitHub, ou
pelo Worker do Cloudflare (worker/leitor.js), pros sites abertos que
barram as máquinas de nuvem (coletar_pelo_hub, sql/040). O Worker baixa
com o User-Agent do DailyPaperBot e só se o robots.txt do site deixar:
pro coletor, é só outro caminho até o site.

Com WORKER_URL e WORKER_SECRET no ambiente (.env, ou Secrets do GitHub),
os sites marcados passam a ser lidos pelo Worker, e a rota do hub na
Vercel (/api/coletar-bloqueados) fica de reserva: o passo dela no
coleta.yml só roda sem o Worker.

Endereço interno, nunca (auditoria de 20/10): os endereços vêm dos
usuários (fontes que eles seguem e os links das notícias desses feeds), e
o coletor grava o texto do que abre. Sem esta checagem, alguém poderia
seguir "http://localhost:..." ou um IP da rede da máquina do GitHub e ler
a resposta como notícia. Vale pra cada redirecionamento também.
"""
import ipaddress
import os
import socket
from urllib.parse import urljoin, urlparse

import requests

TEMPO_EXTRA_DO_WORKER = 20  # o Worker ainda lê o robots.txt antes
MAX_REDIRECIONAMENTOS = 5
# IPs "públicos" que são da rede interna da nuvem: o 168.63.129.16 é o
# servidor da Azure que toda máquina dela enxerga (as do GitHub rodam lá)
IPS_DA_NUVEM = {ipaddress.ip_address("168.63.129.16")}


class RobotsNaoDeixa(Exception):
    """O Worker conferiu: o robots.txt do site não deixa abrir esse endereço."""


class ErroDoWorker(requests.RequestException):
    """O próprio Worker recusou ou caiu (senha errada, site fora da lista)."""


class EnderecoInterno(requests.RequestException):
    """O endereço não é http(s) ou aponta pra uma rede interna (localhost,
    IP privado, rede da própria máquina)."""


def tem_worker():
    return bool(os.environ.get("WORKER_URL") and os.environ.get("WORKER_SECRET"))


def _ip_publico(texto):
    ip = ipaddress.ip_address(texto.split("%")[0])  # "fe80::1%eth0" -> sem a interface
    if ip.version == 6 and ip.ipv4_mapped:
        ip = ip.ipv4_mapped  # "::ffff:127.0.0.1" é o 127.0.0.1
    return ip.is_global and not ip.is_multicast and ip not in IPS_DA_NUVEM


def checar_endereco(url):
    """Levanta EnderecoInterno se o endereço não puder ser aberto. Confere
    os IPs pra onde o nome aponta de verdade: "127.0.0.1.nip.io" e
    "2130706433" também são o 127.0.0.1. Nome que não existe passa: o GET
    falha sozinho, como antes."""
    partes = urlparse(url)
    if partes.scheme not in ("http", "https") or not partes.hostname:
        raise EnderecoInterno(f"endereço não permitido: {url[:80]}")
    try:
        porta = partes.port or (443 if partes.scheme == "https" else 80)
        enderecos = {info[4][0] for info in socket.getaddrinfo(partes.hostname, porta, proto=socket.IPPROTO_TCP)}
    except (socket.gaierror, UnicodeError, ValueError):
        return
    if not all(_ip_publico(e) for e in enderecos):
        raise EnderecoInterno(f"endereço interno: {partes.hostname}")


def _direto(url, user_agent, timeout):
    """GET seguindo os redirecionamentos à mão, conferindo cada destino."""
    for _ in range(MAX_REDIRECIONAMENTOS + 1):
        checar_endereco(url)
        resposta = requests.get(url, headers={"User-Agent": user_agent}, timeout=timeout, allow_redirects=False)
        if not resposta.is_redirect:
            return resposta
        url = urljoin(url, resposta.headers["location"])
    raise requests.TooManyRedirects(f"redirecionamentos demais: {url[:80]}")


def baixar(url, user_agent, pelo_worker=False, timeout=15):
    """GET no endereço, direto ou pelo Worker. Devolve a resposta do site,
    com o status de lá: o raise_for_status fica com quem chama."""
    if not pelo_worker:
        return _direto(url, user_agent, timeout)
    resposta = requests.get(
        os.environ["WORKER_URL"].rstrip("/") + "/",
        params={"url": url},
        headers={"Authorization": f"Bearer {os.environ['WORKER_SECRET']}"},
        timeout=timeout + TEMPO_EXTRA_DO_WORKER,
    )
    # O que vem do site traz o x-url-final; sem ele, quem respondeu foi o
    # próprio Worker
    if "x-url-final" not in resposta.headers:
        if resposta.status_code == 451:
            raise RobotsNaoDeixa(url)
        raise ErroDoWorker(f"o Worker recusou ({resposta.status_code}: {resposta.text[:80]})")
    return resposta
