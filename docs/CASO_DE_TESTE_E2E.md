# Caso de Teste — Cenário Real para Testar o Site

**URL:** https://chatbot-decisao-teoria-dos-jogos.onrender.com/

> O serviço gratuito do Render hiberna após ~15 min sem uso. Abram o link
> uns minutos antes de testar para o primeiro carregamento não ficar lento.

## O cenário

Você é uma empreendedora lançando uma **clínica de telemedicina** e quer
saber como se posicionar frente a um concorrente já estabelecido —
a **Doctoralia**, plataforma de agendamento médico online.

## O que digitar, em ordem

**1. Link do concorrente** (cole exatamente):
```
https://www.doctoralia.com.br
```
→ O sistema vai coletar o conteúdo da página e devolver de 2 a 4
estratégias da Doctoralia, cada uma com um trecho do site como evidência
(ex.: algo sobre grande volume de especialistas cadastrados, agendamento
online, teleconsulta).

**2. Suas próprias estratégias** (cole exatamente):
```
Quero focar em preço baixo e em um atendimento mais rápido e personalizado, com consultas em até 10 minutos após o agendamento.
```
→ O sistema deve devolver de 2 a 4 estratégias limpas (algo como "Preço
baixo", "Atendimento rápido", "Atendimento personalizado", "Consultas em
até 10 minutos") — o número exato de itens pode variar a cada execução
(o LLM não é determinístico), mas **nunca** deve aparecer um fragmento
sem sentido tipo "e em" ou "após o agendamento" virando estratégia
sozinha.

**3. Modo de payoff:** clique em **"Heurística automática"**.
→ Aparece a matriz de payoff (tabela), com um aviso de que os valores são
estimativas, não dados reais.

**4. Aguarde o resultado final.**
→ O sistema calcula sozinho (sem vocês fazerem nada) e devolve uma
recomendação em texto, dizendo qual estratégia adotar e citando o
conceito usado (estratégia dominante e/ou equilíbrio de Nash), com
explicação em linguagem simples.

## O que observar

- O tempo total do passo 1 até a matriz aparecer (esperado: até uns 30
  segundos).
- Se as estratégias da Doctoralia fazem sentido com o que está no site
  de verdade dela.
- Se a recomendação final é compreensível para alguém que nunca ouviu
  falar de Teoria dos Jogos.

## Se quiserem testar o fallback de imagem também

Depois desse fluxo terminar, enviem um novo link qualquer e, em vez de
esperar ele falhar, já mandem direto um print de alguma página de
concorrente (ícone de clipe) — o sistema deve interpretar a imagem do
mesmo jeito que interpretaria o texto do site.
