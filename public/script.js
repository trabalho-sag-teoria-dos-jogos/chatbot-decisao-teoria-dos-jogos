// Injeta, dentro do grupo esquerdo do cabeçalho do Chainlit: a torre (♜)
// clicável (recarrega e volta ao início) e o título compacto do site.
// São elementos reais do DOM (não efeitos de CSS), necessários para o
// clique e para o cabeçalho ter um propósito visível (nome do site).
(function () {
  function insertHeaderBranding() {
    var header = document.getElementById("header");
    if (!header || header.querySelector(".sag-rook-icon")) {
      return;
    }

    var rook = document.createElement("button");
    rook.type = "button";
    rook.className = "sag-rook-icon";
    rook.setAttribute("aria-label", "Recarregar e voltar ao início");
    rook.title = "Recarregar e voltar ao início";
    rook.textContent = "♜";
    rook.addEventListener("click", function () {
      window.location.reload();
    });

    var title = document.createElement("span");
    title.className = "sag-header-title";
    title.textContent = "Consultor de Estratégia Competitiva";

    // O cabeçalho do Chainlit tem dois grupos internos (esquerda/direita)
    // distribuídos com "space-between". Inserimos torre + título DENTRO do
    // grupo da esquerda (não como irmãos soltos do header), para não
    // quebrar esse layout em 3 partes e descentralizar o botão de nova
    // conversa.
    var leftGroup = header.firstElementChild;
    var target = leftGroup || header;
    target.insertBefore(title, target.firstChild);
    target.insertBefore(rook, title);
  }

  // Cria uma faixa PRÓPRIA para o cavalo, como elemento IRMÃO do
  // #header (não filho dele, não filho da área de mensagens) — inserida
  // logo depois do cabeçalho no DOM. Por ocupar espaço real no fluxo
  // normal do documento, o restante do conteúdo (a área de mensagens) é
  // empurrado para baixo dela automaticamente. Resultado: três áreas
  // sequenciais e exclusivas — cabeçalho, faixa do cavalo, texto — sem
  // nenhuma se sobrepor às outras.
  function insertKnightBand() {
    var header = document.getElementById("header");
    if (!header || document.querySelector(".sag-knight-band")) {
      return;
    }
    var band = document.createElement("div");
    band.className = "sag-knight-band";
    var knight = document.createElement("span");
    knight.className = "sag-horizon-knight";
    knight.setAttribute("aria-hidden", "true");
    knight.textContent = "♞";
    band.appendChild(knight);
    header.insertAdjacentElement("afterend", band);
  }

  var observer = new MutationObserver(function () {
    insertHeaderBranding();
    insertKnightBand();
  });
  observer.observe(document.body, { childList: true, subtree: true });
  insertHeaderBranding();
  insertKnightBand();
})();
