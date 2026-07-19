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

  // Cavalo decorativo e persistente. É inserido DENTRO do #header (não
  // mais em document.body) e posicionado via CSS "position: absolute"
  // relativo ao próprio cabeçalho — assim ele fica numa faixa reservada,
  // sempre abaixo dos ícones e sempre acima de qualquer texto de
  // mensagem, sem nunca se sobrepor ao conteúdo (área fisicamente
  // separada, não uma questão de camada/z-index).
  function insertHorizonKnight() {
    var header = document.getElementById("header");
    if (!header || header.querySelector(".sag-horizon-knight")) {
      return;
    }
    var knight = document.createElement("div");
    knight.className = "sag-horizon-knight";
    knight.setAttribute("aria-hidden", "true");
    knight.textContent = "♞";
    header.appendChild(knight);
  }

  var observer = new MutationObserver(function () {
    insertHeaderBranding();
    insertHorizonKnight();
  });
  observer.observe(document.body, { childList: true, subtree: true });
  insertHeaderBranding();
  insertHorizonKnight();
})();
