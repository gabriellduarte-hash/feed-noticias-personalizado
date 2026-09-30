-- ============================================================
-- 008_add_category_and_summary.sql
-- Persiste, por artigo, a categoria e o resumo que o resumo/resumir.py
-- já calcula via IA (hoje isso só existe dentro do HTML do e-mail).
-- Vira dado estruturado, reaproveitável pelo hub de leitura (Next.js)
-- sem precisar reprocessar nada.
-- ============================================================

alter table articles add column category text;
alter table articles add column ai_summary text;

-- Mesma lista fixa de categorias usada em resumo/resumir.py — trava no
-- banco pra não entrar valor fora do padrão por engano.
alter table articles add constraint articles_category_check
  check (category is null or category in (
    'Tecnologia', 'Finanças', 'Humor', 'Política', 'Ciência',
    'Saúde', 'Esportes', 'Entretenimento', 'Mundo', 'Outros'
  ));
