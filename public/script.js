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
    header.insertBefore(rook, header.firstChild);
  }

  var observer = new MutationObserver(insertRookIcon);
  observer.observe(document.body, { childList: true, subtree: true });
  insertRookIcon();
})();
