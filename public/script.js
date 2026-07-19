// Injeta a peça de torre (♜) como ícone clicável no cabeçalho, que recarrega
// a página (volta ao início da conversa). É um elemento real do DOM (não um
// efeito de CSS) para poder receber o clique.
(function () {
  function insertRookIcon() {
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

    // O cabeçalho do Chainlit tem dois grupos internos (esquerda/direita)
    // distribuídos com "space-between". Inserir a torre como um terceiro
    // item solto no topo do header quebra esse layout em 3 partes e joga o
    // botão "nova conversa" para o meio. Por isso, colocamos a torre DENTRO
    // do primeiro grupo (esquerda), junto com o botão de nova conversa, em
    // vez de como irmã dos dois grupos.
    var leftGroup = header.firstElementChild;
    if (leftGroup) {
      leftGroup.insertBefore(rook, leftGroup.firstChild);
    } else {
      header.insertBefore(rook, header.firstChild);
    }
  }

  // Cavalo grande, decorativo e persistente, perto do "horizonte" do
  // tabuleiro de fundo — não depende da tela de carregamento do Chainlit
  // (que é, por natureza, temporária e não pode ser mantida na tela).
  function insertHorizonKnight() {
    if (document.querySelector(".sag-horizon-knight")) {
      return;
    }
    var knight = document.createElement("div");
    knight.className = "sag-horizon-knight";
    knight.setAttribute("aria-hidden", "true");
    knight.textContent = "♞";
    document.body.appendChild(knight);
  }

  var observer = new MutationObserver(function () {
    insertRookIcon();
    insertHorizonKnight();
  });
  observer.observe(document.body, { childList: true, subtree: true });
  insertRookIcon();
  insertHorizonKnight();
})();
