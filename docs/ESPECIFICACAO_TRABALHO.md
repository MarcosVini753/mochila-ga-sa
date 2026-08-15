# Especificação do Trabalho — GA × Simulated Annealing na Mochila 0/1

Este documento é a fonte canônica dos requisitos acadêmicos do projeto. Ele traduz as mensagens recebidas sobre o trabalho em um procedimento experimental claro, reproduzível e diretamente implementável.

## 1. Estrutura obrigatória do trabalho

O trabalho possui três partes.

### Parte 1 — Estudar o primeiro algoritmo

1. Implementar o algoritmo normalmente, com uma configuração de referência.
2. Executá-lo sobre o problema e registrar desempenho e número de iterações.
3. Fazer pequenas modificações nos parâmetros do algoritmo.
4. Para cada modificação, executar novamente e guardar os resultados.
5. Construir gráficos comparando a configuração original com as modificadas.
6. Explicar o comportamento observado, relacionando cada mudança de parâmetro aos efeitos em qualidade, tempo, iterações e taxa de sucesso.
7. Identificar a melhor configuração do primeiro algoritmo.

### Parte 2 — Estudar o segundo algoritmo

Repetir o mesmo processo da Parte 1 para o segundo algoritmo: configuração original, variações controladas, execuções repetidas, resultados, gráficos, interpretação e escolha da melhor configuração.

### Parte 3 — Comparação final

1. Selecionar a melhor configuração encontrada na Parte 1.
2. Selecionar a melhor configuração encontrada na Parte 2.
3. Comparar diretamente as duas.
4. Explicar por que uma apresentou resultado melhor que a outra, considerando qualidade da solução, estabilidade, tempo e esforço computacional.

## 2. Escolhas deste projeto

- Problema: Problema da Mochila 0/1.
- Parte 1: Algoritmo Genético (GA).
- Parte 2: Simulated Annealing (SA).
- Parte 3: melhor GA × melhor SA.

A Mochila 0/1 é formulada como:

```text
maximizar sum(v_i * x_i)
sujeito a sum(w_i * x_i) <= C
x_i ∈ {0,1}
```

## 3. Princípio experimental central

As modificações devem ser controladas. Ao estudar o efeito de um parâmetro, alterar apenas esse parâmetro e manter os demais iguais à configuração de referência.

Exemplo correto:

```text
GA_BASE:    population_size=100, crossover=0.80, mutation=1/n
GA_POP_50:  population_size=50,  crossover=0.80, mutation=1/n
GA_POP_200: population_size=200, crossover=0.80, mutation=1/n
```

Não se deve alterar vários parâmetros simultaneamente numa configuração usada para atribuir efeito a uma variável, pois isso impede explicar qual mudança causou o comportamento observado.

## 4. Instâncias e ótimo de referência

Manter as instâncias Pisinger já adotadas:

```text
n = 20, 50, 100
correlation = uncorrelated, weakly, strongly
10 instâncias por combinação
90 instâncias no total
```

O dataset Kaggle de apenas 5 itens permanece descartado, pois `2^5 = 32` soluções tornam a comparação pouco informativa.

O ótimo de cada instância deve ser calculado por programação dinâmica e armazenado em `data/processed/instances_with_optimum.csv`. O ótimo serve somente para avaliação posterior e nunca pode ser consultado pelo GA ou SA durante a busca.

Gap percentual:

```text
gap_percent = ((optimum_value - best_value_found) / optimum_value) * 100
```

Quanto menor o gap, melhor.

## 5. Repetições e reprodutibilidade

Cada configuração deve ser executada 10 vezes por instância, com sementes determinísticas e registradas. Metaheurísticas são estocásticas; uma única execução não é suficiente.

As configurações concorrentes devem usar as mesmas instâncias e, sempre que possível, as mesmas sementes correspondentes.

## 6. Métricas obrigatórias

Cada execução deve registrar:

```text
instance_id
n
correlation
algorithm
configuration
run
seed
best_value_found
best_weight_found
optimum_value
gap_percent
execution_time_ms
evaluations
iterations_executed
hit_optimum
```

Hierarquia para interpretar desempenho:

1. menor gap médio;
2. maior taxa de obtenção do ótimo;
3. menor tempo médio;
4. menor número médio de avaliações;
5. menor número médio de iterações quando a comparação fizer sentido.

“Melhor” não deve significar apenas “mais rápido” ou apenas “maior valor”. A conclusão deve discutir o trade-off entre qualidade e custo computacional.

## 7. Parte 1 — Algoritmo Genético

Configuração de referência:

```text
GA_BASE
population_size = 100
generations = 100
tournament_size = 3
crossover_rate = 0.80
mutation_rate = 1/n
elitism = True
```

Variações iniciais recomendadas, sempre mudando um parâmetro por vez:

```text
GA_POP_50:    population_size = 50
GA_POP_200:   population_size = 200
GA_CROSS_060: crossover_rate = 0.60
GA_CROSS_095: crossover_rate = 0.95
GA_MUT_LOW:   mutation_rate = 0.5/n
GA_MUT_HIGH:  mutation_rate = 2/n
```

Hipóteses a investigar:

- população maior pode aumentar diversidade e qualidade, mas eleva avaliações e tempo;
- população menor pode ser mais rápida, mas mais sujeita a convergência prematura;
- crossover maior aumenta recombinação;
- mutação maior aumenta exploração, mas pode destruir boas estruturas;
- mutação muito baixa pode reduzir diversidade.

A Parte 1 deve gerar comparações de gap, taxa de ótimo, tempo, avaliações e gerações. Ao final, deve ser escolhida a melhor configuração efetivamente testada de GA.

Não combinar automaticamente os melhores valores de parâmetros encontrados. O vencedor da Parte 1 deve ser uma configuração realmente executada, salvo autorização explícita para uma etapa adicional de combinação.

## 8. Parte 2 — Simulated Annealing

Configuração de referência:

```text
SA_BASE
iterations = 10000
initial_temperature = 1000.0
minimum_temperature = 0.001
cooling_rate = 0.995
neighborhood = flip de 1 bit
```

As mensagens do trabalho citam explicitamente alterar a velocidade de resfriamento e a temperatura inicial. Essas devem ser as variações principais:

```text
SA_COOL_FAST: cooling_rate = 0.98
SA_COOL_SLOW: cooling_rate = 0.999
SA_T0_LOW:    initial_temperature = 100.0
SA_T0_HIGH:   initial_temperature = 5000.0
```

Hipóteses a investigar:

- resfriamento mais rápido reduz mais cedo a aceitação de soluções piores e pode diminuir tempo/iterações, mas aumentar convergência prematura;
- resfriamento mais lento prolonga exploração e pode melhorar qualidade ao custo de mais iterações/tempo;
- temperatura inicial menor torna a busca mais gulosa desde cedo;
- temperatura inicial maior aumenta exploração inicial e a possibilidade de escapar de ótimos locais.

O SA deve registrar o número real de iterações executadas. Como há parada por `temperature < minimum_temperature`, mudanças em `cooling_rate` podem alterar diretamente esse número. Isso precisa aparecer na análise porque as mensagens do trabalho pedem explicitamente observar quantas iterações o algoritmo realizou.

A Parte 2 deve comparar gap, taxa de ótimo, tempo, avaliações e iterações, terminando com a escolha da melhor configuração efetivamente testada de SA.

## 9. Parte 3 — Melhor GA × melhor SA

Depois das duas análises:

```text
best_GA = melhor configuração observada na Parte 1
best_SA = melhor configuração observada na Parte 2
```

Comparar os dois sobre as mesmas instâncias e repetições.

A comparação final deve responder:

1. qual alcança menor gap médio;
2. qual encontra o ótimo com maior frequência;
3. qual é mais rápido;
4. qual usa menos avaliações;
5. qual é mais estável entre execuções;
6. como o comportamento muda com `n` e tipo de correlação;
7. qual apresenta o melhor compromisso entre qualidade e custo.

A discussão deve relacionar os resultados à natureza dos métodos: GA trabalha com população, seleção, crossover e mutação; SA trabalha com uma solução por vez e controla exploração/explotação pela temperatura.

## 10. Estrutura dos resultados

Separar resultados por etapa:

```text
results/
  ga/
    raw_runs.csv
    summary.csv
    figures/
  sa/
    raw_runs.csv
    summary.csv
    figures/
  final/
    summary.csv
    figures/
```

Resumo agregado sugerido:

```text
algorithm,configuration,n,correlation
mean_gap,std_gap
optimal_rate
mean_time_ms,std_time_ms
mean_evaluations,std_evaluations
mean_iterations,std_iterations
```

## 11. Gráficos mínimos

Parte 1 — GA:

- gap médio por configuração;
- tempo médio por configuração;
- taxa de ótimo por configuração;
- avaliações médias por configuração.

Parte 2 — SA:

- gap médio por configuração;
- tempo médio por configuração;
- taxa de ótimo por configuração;
- iterações médias por configuração.

Parte 3 — Final:

- melhor GA × melhor SA em gap;
- melhor GA × melhor SA em tempo;
- melhor GA × melhor SA em taxa de ótimo.

Todos os gráficos devem ser gerados a partir dos CSVs, nunca preenchidos manualmente.

## 12. Como explicar o comportamento dos gráficos

A discussão deve seguir esta lógica:

```text
modificação do parâmetro
→ mudança no mecanismo de busca
→ mudança no comportamento observado
→ efeito nas métricas
```

Exemplo SA:

```text
cooling_rate menor
→ resfriamento mais rápido
→ menos tempo aceitando soluções piores
→ intensificação mais cedo
→ possível redução de tempo/iterações
→ possível aumento do gap por convergência prematura
```

Exemplo GA:

```text
population_size maior
→ mais indivíduos por geração
→ maior diversidade potencial
→ mais avaliações e maior tempo
→ possível redução do gap se a diversidade evitar convergência prematura
```

As hipóteses servem para orientar a análise; a conclusão deve ser baseada nos resultados reais.

## 13. Comparação justa

Tempo isolado não é suficiente para declarar vencedor. Uma configuração pode parecer melhor apenas porque consumiu muito mais avaliações.

Por isso, `evaluations` deve ser sempre registrado. Quando duas configurações tiverem qualidade semelhante, a de menor tempo/avaliações é preferível. Quando uma configuração gastar muito mais computação para obter pequena melhora, esse trade-off deve ser explicitamente discutido.

## 14. Estrutura recomendada do artigo

```text
1. Introdução
2. Problema da Mochila 0/1
3. Algoritmos Avaliados
   3.1 Algoritmo Genético
   3.2 Simulated Annealing
4. Metodologia Experimental
   4.1 Instâncias e ótimo de referência
   4.2 Métricas
   4.3 Configurações do GA
   4.4 Configurações do SA
5. Resultados e Discussão
   5.1 Parte 1 — Configurações do GA
   5.2 Parte 2 — Configurações do SA
   5.3 Parte 3 — Melhor GA × melhor SA
6. Conclusão
```

## 15. Regras obrigatórias

1. Não inventar resultados.
2. Não usar o ótimo durante a busca das metaheurísticas.
3. Não voltar ao dataset Kaggle de 5 itens sem solicitação explícita.
4. Manter sementes e reprodutibilidade.
5. Guardar resultados brutos antes de agregar.
6. Gerar gráficos a partir dos dados salvos.
7. Alterar um parâmetro por vez nas análises de sensibilidade.
8. Comparar configurações sobre as mesmas instâncias.
9. Registrar iterações/gerações e avaliações.
10. Não chamar uma configuração de “melhor” sem aplicar critérios explícitos.
11. Na comparação final, usar a melhor configuração efetivamente observada de cada algoritmo.
12. Não apresentar hipóteses teóricas como se fossem resultados experimentais.

## 16. Ordem correta de execução

```text
1. Verificar as 90 instâncias
2. Verificar os ótimos por programação dinâmica
3. Validar GA_BASE
4. Implementar executor das configurações de GA
5. Rodar Parte 1
6. Agregar e gerar gráficos da Parte 1
7. Selecionar best_GA
8. Validar SA_BASE
9. Implementar executor das configurações de SA
10. Rodar Parte 2
11. Agregar e gerar gráficos da Parte 2
12. Selecionar best_SA
13. Produzir comparação best_GA × best_SA
14. Gerar gráficos finais
15. Atualizar o artigo apenas com resultados reais
16. Revisar discussão e conclusão
```

Esta especificação substitui qualquer plano anterior que tratasse apenas de comparar GA padrão contra SA padrão.