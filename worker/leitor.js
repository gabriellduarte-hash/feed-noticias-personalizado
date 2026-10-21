// Daily Paper — leitor dos sites que barram as máquinas de nuvem
// (Cloudflare Worker).
//
// Alguns sites abertos (Adrenaline e outros) ficam atrás de um filtro do
// Cloudflare que barra os servidores do GitHub e da Vercel, mesmo com o
// robots.txt liberando robôs. Este Worker roda na rede do Cloudflare e
// baixa o feed ou a página por nós, do mesmo jeito honesto de sempre:
//   - com o nosso User-Agent (DailyPaperBot), sem fingir ser navegador;
//   - só se o robots.txt do site permitir;
//   - só pra quem tem a senha (SEGREDO): não é um proxy aberto.
// Devolve o conteúdo como veio (status, tipo e corpo); quem lê é o coletor.
//
// Configuração (painel do Cloudflare › Workers › este Worker › Settings):
//   SEGREDO   (Secret): a senha; a mesma em WORKER_SECRET no coletor
//   DOMINIOS  (Text, opcional): sites aceitos, separados por vírgula
//             ("adrenaline.com.br,placar.com.br"). Vazio = qualquer um.
// O resto (nome e região: perto de São Paulo) fica no wrangler.jsonc,
// publicado com "npx wrangler deploy" de dentro desta pasta.
//
// Uso: GET https://<worker>.workers.dev/?url=<endereço>
//      Authorization: Bearer <SEGREDO>

const USER_AGENT = "DailyPaperBot/1.0 (+https://dailypaper.news)";
const NOSSO_ROBO = "dailypaperbot";
const ROBOTS_EM_CACHE_SEGUNDOS = 3600;

export default {
  async fetch(request, env) {
    if (!env.SEGREDO || request.headers.get("authorization") !== `Bearer ${env.SEGREDO}`) {
      return resposta("não autorizado", 401);
    }
    const pedido = new URL(request.url).searchParams.get("url");
    let destino;
    try {
      destino = new URL(pedido);
    } catch {
      return resposta("url inválida", 400);
    }
    if (destino.protocol !== "https:" && destino.protocol !== "http:") return resposta("só http e https", 400);

    const dominios = (env.DOMINIOS || "")
      .split(",")
      .map((d) => d.trim().toLowerCase())
      .filter(Boolean);
    const host = destino.hostname.toLowerCase().replace(/^www\./, "");
    if (dominios.length && !dominios.some((d) => host === d || host.endsWith(`.${d}`))) {
      return resposta("site fora da lista", 403);
    }
    if (!(await robotsPermite(destino))) return resposta("o robots.txt do site não permite", 451);

    const original = await fetch(destino.toString(), {
      headers: { "User-Agent": USER_AGENT, Accept: "*/*" },
      redirect: "follow",
    });
    return new Response(original.body, {
      status: original.status,
      headers: {
        "content-type": original.headers.get("content-type") || "application/octet-stream",
        "x-url-final": original.url,
      },
    });
  },
};

function resposta(texto, status) {
  return new Response(texto, { status, headers: { "content-type": "text/plain; charset=utf-8" } });
}

/** O robots.txt do site deixa o DailyPaperBot (ou "*") abrir esse caminho?
 * Sem robots.txt (ou com erro), está liberado. Guardado por 1h. */
async function robotsPermite(destino) {
  const enderecoRobots = `${destino.origin}/robots.txt`;
  const cache = caches.default;
  let robots = await cache.match(enderecoRobots);
  if (!robots) {
    const baixado = await fetch(enderecoRobots, { headers: { "User-Agent": USER_AGENT } }).catch(() => null);
    const texto = baixado && baixado.ok ? await baixado.text() : "";
    robots = new Response(texto, { headers: { "cache-control": `max-age=${ROBOTS_EM_CACHE_SEGUNDOS}` } });
    await cache.put(enderecoRobots, robots.clone());
  }
  return caminhoPermitido(await robots.text(), destino.pathname + destino.search);
}

/** As regras do grupo do nosso robô (ou do "*"); a regra mais longa que
 * casa decide, e Allow ganha no empate (como o Google faz). */
function caminhoPermitido(texto, caminho) {
  const grupos = [];
  let atual = null;
  for (const linhaBruta of texto.split(/\r?\n/)) {
    const linha = linhaBruta.replace(/#.*/, "").trim();
    const [campo, ...resto] = linha.split(":");
    if (!campo || !resto.length) continue;
    const chave = campo.trim().toLowerCase();
    const valor = resto.join(":").trim();
    if (chave === "user-agent") {
      if (!atual || atual.regras.length) grupos.push((atual = { agentes: [], regras: [] }));
      atual.agentes.push(valor.toLowerCase());
    } else if ((chave === "allow" || chave === "disallow") && atual) {
      atual.regras.push({ permite: chave === "allow", padrao: valor });
    }
  }
  const nosso = grupos.find((g) => g.agentes.includes(NOSSO_ROBO));
  const grupo = nosso || grupos.find((g) => g.agentes.includes("*"));
  if (!grupo) return true;
  let melhor = null;
  for (const regra of grupo.regras) {
    if (!regra.padrao) continue; // "Disallow:" vazio libera tudo
    if (casa(regra.padrao, caminho)) {
      const maisLonga = !melhor || regra.padrao.length > melhor.padrao.length;
      const empateQueLibera = melhor && regra.padrao.length === melhor.padrao.length && regra.permite;
      if (maisLonga || empateQueLibera) melhor = regra;
    }
  }
  return melhor ? melhor.permite : true;
}

/** Padrão do robots.txt (com * e $) contra o caminho. */
function casa(padrao, caminho) {
  const ateOFim = padrao.endsWith("$");
  const corpo = (ateOFim ? padrao.slice(0, -1) : padrao).replace(/[.+?^${}()|[\]\\]/g, "\\$&").replace(/\*/g, ".*");
  return new RegExp(`^${corpo}${ateOFim ? "$" : ""}`).test(caminho);
}
