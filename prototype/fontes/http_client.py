"""Cliente HTTP com cache em disco e fallback para fixtures.

Modos:
- "live":    consulta a API real; erro se indisponível.
- "fixture": usa somente os JSONs de dados/fixtures (demonstração/offline).
- "auto":    tenta a API real; se falhar, cai para a fixture correspondente.

Toda resposta carrega proveniência: {"origem": "live"|"fixture", "url", "consultado_em"}.
O relatório final usa a proveniência para exibir o selo de fonte de cada número
e o aviso de dados de demonstração quando qualquer fixture for usada.
"""

import gzip
import hashlib
import json
import time
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DIR_FIXTURES = RAIZ / "dados" / "fixtures"
DIR_CACHE = RAIZ / ".cache"

TIMEOUT_S = 30
CACHE_TTL_S = 7 * 24 * 3600  # dados públicos mudam devagar


class FonteIndisponivel(RuntimeError):
    pass


class ClienteHTTP:
    def __init__(self, modo: str = "auto"):
        assert modo in ("live", "fixture", "auto"), modo
        self.modo = modo
        self.usou_fixture = False
        DIR_CACHE.mkdir(exist_ok=True)

    def buscar_json(self, url: str, fixture: str):
        """Retorna (dados, proveniencia). `fixture` é o nome do arquivo em dados/fixtures."""
        if self.modo != "fixture":
            try:
                dados = self._live(url)
                return dados, {
                    "origem": "live",
                    "url": url,
                    "consultado_em": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()),
                }
            except Exception as exc:
                if self.modo == "live":
                    raise FonteIndisponivel(f"{url}: {exc}") from exc
                print(f"[aviso] fonte ao vivo indisponível, usando fixture {fixture}: {exc}")
                motivo = f"{type(exc).__name__}: {exc}"
        else:
            motivo = "modo fixture selecionado"
        dados = self._fixture(fixture)
        self.usou_fixture = True
        return dados, {
            "origem": "fixture",
            "url": url,
            "consultado_em": "dados de demonstração (fixture)",
            "motivo": motivo,
        }

    def _live(self, url: str):
        chave = DIR_CACHE / (hashlib.md5(url.encode()).hexdigest() + ".json")
        if chave.exists() and time.time() - chave.stat().st_mtime < CACHE_TTL_S:
            return json.loads(chave.read_text())
        req = urllib.request.Request(url, headers={
            "User-Agent": "prototipo-pesquisa-mercado/0.1",
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            bruto = resp.read()
        if bruto[:2] == b"\x1f\x8b":  # algumas respostas do IBGE chegam gzipadas
            bruto = gzip.decompress(bruto)
        dados = json.loads(bruto.decode("utf-8"))
        try:
            chave.write_text(json.dumps(dados, ensure_ascii=False))
        except OSError:
            pass  # cache é otimização; nunca derruba uma consulta que funcionou
        return dados

    def _fixture(self, nome: str):
        caminho = DIR_FIXTURES / nome
        if not caminho.exists():
            raise FonteIndisponivel(f"fixture ausente: {caminho}")
        return json.loads(caminho.read_text())
