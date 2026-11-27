# Resumo dos slides: referência para a apresentação

**Trabalho:** Avaliação Experimental de Heurísticas e Meta-Heurísticas para o Problema Fracionário de Seleção de Pedidos Ótima
**Autor:** Vinicius Alves Pereira, PFC II, CEFET-MG Divinópolis (2026)

---

## Slide 1: Capa

Título, autor, orientador (Prof. Ms. Eduardo Gabriel Reis Miranda) e coorientador (Prof. Dr. André Luiz Maravilha Silva).

---

## Seção 1: Introdução

### Slide 2: Contexto

**Mensagem:** o *picking* é a operação mais cara do armazém, e boa parte desse custo é deslocamento. Reduzir o número de corredores visitados reduz o custo.

- O e-commerce brasileiro movimentou R$ 160,3 bilhões no 1º semestre de 2024, 18,7% a mais que no ano anterior. Mais pedidos significam mais pressão sobre os centros de distribuição.
- O *picking* responde por até 55% do custo operacional de um armazém.
- Cerca de metade do tempo do operador é gasta andando entre estantes.

**Conceitos**

- ***Picking* (separação de pedidos):** retirar das estantes os produtos que compõem os pedidos dos clientes.
- **Corredor:** região do armazém com estantes que guardam um estoque de vários itens. Cada corredor visitado custa deslocamento.

### Slide 3: Desafio SBPO 2025

**Mensagem:** o problema vem do Primeiro Desafio Mercado Livre de Otimização, realizado no 57º SBPO (Simpósio Brasileiro de Pesquisa Operacional), em 2025.

- O desafio propôs o **PSP**, um problema fracionário de seleção de pedidos.
- O Mercado Livre disponibilizou instâncias reais, que servem de *benchmark* padronizado para comparar métodos.

---

## Seção 2: Problema

### Slide 4: O PSP e sua formulação

**Mensagem:** escolher um subconjunto de pedidos (a *wave*) e um subconjunto de corredores que maximize as **unidades coletadas por corredor visitado**.

**Conjuntos e parâmetros**

| Símbolo      | Significado                                     |
| ------------ | ----------------------------------------------- |
| 𝒪            | Pedidos do *backlog*                            |
| ℐ            | Itens (produtos)                                |
| ℐ_o          | Itens do pedido *o*                             |
| 𝒜            | Corredores                                      |
| q_oi         | Unidades do item *i* pedidas pelo pedido *o*    |
| e_ai         | Unidades do item *i* em estoque no corredor *a* |
| LB, UB       | Limites inferior e superior de unidades da wave |

**Variáveis de decisão (binárias)**

- x_o = 1 se o pedido *o* entra na *wave*.
- y_a = 1 se o corredor *a* é visitado.

**Modelo**

- **Objetivo:** maximizar (total de unidades dos pedidos escolhidos) ÷ (número de corredores visitados).
- **Tamanho da *wave*:** o total de unidades fica entre LB e UB.
- **Disponibilidade:** para cada item, a demanda dos pedidos escolhidos não passa do estoque somado dos corredores visitados.
- **Integralidade:** x e y são binárias. Um pedido entra inteiro ou não entra.

**Conceitos**

- ***Wave*:** lote de pedidos separado de uma vez.
- ***Backlog*:** fila de pedidos pendentes, de onde a *wave* é escolhida.
- **Problema fracionário:** a função objetivo é uma razão entre duas expressões das variáveis. Isso impede o uso direto de um *solver* linear inteiro e torna o problema mais difícil.
- **Compromisso central:** colocar mais pedidos aumenta o numerador, mas pode exigir mais corredores, o que aumenta o denominador.

### Slide 5: Exemplo

**Mensagem:** uma instância pequena (5 pedidos, 5 itens, 5 corredores, LB = 5, UB = 12) mostra que coletar mais unidades não garante o melhor objetivo.

| *Wave* | Pedidos       | Corredores | Unidades | Objetivo         |
| ------ | ------------- | ---------- | -------- | ---------------- |
| A      | 0, 4          | {0, 1}     | 5        | 5 / 2 = 2,5      |
| B      | 0, 2, 3       | {1, 3, 4}  | 12       | 12 / 3 = 4,0     |
| C      | 0, 1, 2, 4    | {1, 3}     | 10       | 10 / 2 = **5,0** |

- A *wave* B atinge o UB (12 unidades), mas precisa de 3 corredores.
- A *wave* C coleta menos (10 unidades) e usa só 2 corredores. Ela é a solução ótima.
- Todas são viáveis: respeitam LB ≤ unidades ≤ UB e o estoque dos corredores escolhidos cobre a demanda.

---

## Seção 3: Métodos

### Slide 6: Objetivos

**Objetivo geral:** implementar e avaliar experimentalmente heurísticas e meta-heurísticas para o PSP, usando as instâncias reais do Desafio SBPO 2025 como *benchmark*.

**Objetivos específicos**

1. Formalizar o PSP e situá-lo na literatura do *Order Batching Problem*.
2. Desenvolver a heurística construtiva *OrderBased*, com composição definida pela fronteira de Pareto.
3. Desenvolver a heurística construtiva *AisleBased* e compará-la ao *OrderBased*.
4. Propor a meta-heurística ILS-VND, partindo da solução do *AisleBased*.
5. Avaliar os métodos nas instâncias A, B e X frente às MSC e ao método de referência.

**Conceitos**

- ***Order Batching Problem* (OBP):** família clássica de problemas que agrupa pedidos em lotes para reduzir o esforço de coleta. O PSP é uma variante: escolhe um único lote e mede eficiência por unidades/corredor.
- **Heurística construtiva:** monta uma solução do zero, passo a passo, com regras gulosas. É rápida e não garante o ótimo.
- **Meta-heurística:** estratégia geral que guia buscas locais para escapar de ótimos locais. Troca tempo por qualidade.
- **Fronteira de Pareto:** conjunto de opções em que nenhuma é melhor que outra em todos os critérios ao mesmo tempo (aqui, qualidade × tempo). Uma opção fora da fronteira é dominada.
- **MSC (Melhor Solução Conhecida):** maior objetivo já registrado para a instância. Serve de referência para medir o desvio.

### Slide 7: *OrderBased*

**Ideia:** escolher **primeiro os pedidos**, depois os corredores que cobrem a demanda.

**Etapas**

1. **Ordenar os pedidos** em ordem decrescente de unidades.
2. **Selecionar pedidos:** percorrer a lista e aceitar o pedido se o total continuar ≤ UB e houver estoque no armazém. A demanda aceita se acumula.
3. **Verificar LB:** se o total final ficar abaixo do LB, não há solução.
4. **Cobrir a demanda com corredores** por três variantes, e ficar com a melhor:
   - ***simple*:** guloso estático. Ordena os corredores uma vez e abre na ordem até cobrir a demanda.
   - ***multi*:** guloso dinâmico. Reavalia os corredores a cada passo, considerando a demanda que ainda falta.
   - ***exact*:** cobertura mínima resolvida por *Branch and Bound*, com limite de 30 s.

**Conceitos**

- **Guloso:** a cada passo, toma a decisão que parece melhor no momento, sem voltar atrás.
- **Problema de cobertura de conjuntos (*set cover*):** escolher o menor número de corredores cujo estoque cubra toda a demanda. É NP-difícil.
- ***Branch and Bound* (B&B):** método exato que divide o problema em subproblemas e descarta os que não podem superar a melhor solução encontrada.

**Ponto fraco:** a *wave* é fixada antes de olhar os corredores. Pedidos grandes espalhados pelo armazém forçam a abertura de muitos corredores.

### Slide 8: *AisleBased*

**Ideia:** inverter a ordem. Escolher **primeiro os corredores**, depois empacotar os pedidos que o estoque acumulado consegue atender.

**Etapas**

1. **Escolher a estratégia de ordenação dos corredores:**
   - **Estáticas** (*ranking* fixo, 4 variantes): *units*, *variety*, *mixed* e *useful*. Cada uma pontua o corredor por um critério diferente (quantidade de unidades, variedade de itens, combinação dos dois, unidades úteis para a demanda do *backlog*).
   - **Dinâmica:** *useful* recalculado sobre a demanda residual a cada corredor aberto.
2. **Ordenar os pedidos** em ordem decrescente de unidades (calculado uma vez).
3. **Loop de verificação:**
   - Abrir o próximo corredor (k ← k + 1).
   - Empacotar os pedidos que o estoque dos k corredores atende, sem passar do UB.
   - Avaliar unidades/k e guardar a melhor solução.
   - **Critério de parada:** continuar enquanto UB/k > melhor objetivo. UB/k é o máximo que se pode alcançar com k corredores. Quando esse limite não supera a melhor solução, abrir mais corredores não adianta.
4. **Refinamento:** podar corredores desnecessários, trocar pedidos por outros maiores e podar de novo.
5. **Resultado:** a melhor solução em unidades/|corredores|.

**Por que funciona melhor:** o denominador (corredores) é controlado diretamente, e a poda pelo limite UB/k evita explorar soluções que não podem vencer.

### Slide 9: ILS-VND

**Ideia:** meta-heurística que parte da solução do *AisleBased* e a melhora alternando perturbação guiada e busca local. Não usa *solver*.

**Resumo: ILS (*Iterated Local Search*)**

O ILS é uma meta-heurística que encadeia buscas locais. Uma busca local sozinha para no primeiro ótimo local que encontra. O ILS resolve isso aplicando uma **perturbação** à solução, uma modificação maior que um movimento comum, e rodando a busca local de novo a partir do ponto perturbado. Assim a busca salta para outra região do espaço de soluções sem recomeçar do zero.

Componentes do ILS:

- **Solução inicial:** ponto de partida, normalmente gerado por uma heurística construtiva.
- **Busca local:** leva a solução até um ótimo local.
- **Perturbação:** altera parte da solução para escapar do ótimo local. Se for fraca demais, a busca local volta ao mesmo ótimo. Se for forte demais, o método vira um reinício aleatório.
- **Critério de aceitação:** decide se a nova solução substitui a corrente. Aceitar só melhorias intensifica a busca. Aceitar pioras pequenas diversifica.
- **Critério de parada:** tempo, número de iterações ou iterações sem melhora (estagnação).

Esquema genérico:

```
s ← BuscaLocal(SoluçãoInicial())
s* ← s
enquanto não atingir o critério de parada:
    s' ← Perturbar(s)
    s'' ← BuscaLocal(s')
    s ← Aceitar(s, s'')
    se s'' é melhor que s*: s* ← s''
retorna s*
```

No ILS-VND deste trabalho, a solução inicial é a do *AisleBased*, a busca local é o VND, a perturbação troca corredores e a aceitação tolera piora de até 1%.

**Resumo: VND (*Variable Neighborhood Descent*)**

O VND é uma busca local que usa **várias vizinhanças** em vez de uma só. A ideia vem do fato de que um ótimo local para uma vizinhança pode não ser ótimo local para outra. Ao combinar vizinhanças, a solução final é um ótimo local em relação a todas elas ao mesmo tempo, o que costuma ser melhor que o resultado de qualquer vizinhança isolada.

Funcionamento:

- As vizinhanças N₁, N₂, …, N_k são ordenadas, em geral da mais barata para a mais cara de explorar.
- A busca começa em N₁ e procura uma solução melhor.
- Se encontra, aceita a melhora e **volta para N₁**.
- Se não encontra, passa para a próxima vizinhança.
- Termina quando nenhuma das k vizinhanças melhora a solução.

Esquema genérico:

```
k ← 1
enquanto k ≤ k_max:
    s' ← melhor vizinho de s em N_k
    se s' é melhor que s:
        s ← s'
        k ← 1
    senão:
        k ← k + 1
retorna s
```

O VND é determinístico: não sorteia nada. Ele é a versão de descida do VNS (*Variable Neighborhood Search*). No ILS-VND, a aleatoriedade fica só na perturbação do ILS, e o VND cuida de refinar a solução com as vizinhanças T1 a T4.

**Etapas**

1. **Solução inicial:** s₀ ← *AisleBased*. Aplica VND em s₀ e define a solução corrente (s_cur) e a melhor (s*).
2. **Ciclo ILS:**
   - **Perturbar** s_cur: remove corredores pouco eficientes e adiciona corredores promissores, sorteados de uma lista restrita de candidatos (RCL) controlada por α.
   - **VND** sobre a solução perturbada, gerando s''.
   - **Aceitação:** aceita s'' se ela não piorar mais que τ = 1% em relação a s_cur. Atualiza s* se melhorar.
   - Repete até atingir o limite de tempo ou de estagnação.
3. **VND (busca local em vizinhanças ordenadas):**
   - **T1:** reduzir corredores.
   - **T2:** trocar ou adicionar pedidos.
   - **T3:** adicionar corredor.
   - **T4:** trocar corredor.
   - Se uma vizinhança melhora a solução, volta para T1. Se nenhuma melhora, a solução é um ótimo local de todas.

**Conceitos**

- **Vizinhança:** conjunto de soluções alcançáveis a partir da atual por um movimento pequeno (tirar um corredor, trocar um pedido etc.).
- **Ótimo local:** solução que nenhum movimento da vizinhança consegue melhorar, mesmo sem ser o ótimo global.
- **RCL e α:** lista dos melhores candidatos de onde se sorteia um. α regula o tamanho da lista: perto de 0 é guloso, perto de 1 é aleatório. A mesma ideia é usada no GRASP.
- **Tolerância τ:** aceitar soluções levemente piores (até 1%) ajuda a diversificar a busca.

---

## Seção 4: Experimentos e Resultados

### Slide 10: Datasets e instâncias

**Mensagem:** 50 instâncias reais do Mercado Livre em três datasets de tamanho crescente.

| Dataset | Instâncias | Pedidos (média) | Itens (média) | Corredores (média) |
| ------- | ---------- | --------------- | ------------- | ------------------ |
| A       | 20         | 3.054           | 3.179         | 204                |
| B       | 15         | 14.824          | 13.527        | 321                |
| X       | 15         | 23.836          | 20.622        | 333                |

- O boxplot mostra que A tem instâncias pequenas e muito variadas (de poucos a ~400 corredores).
- B e X são maiores e chegam a ~68 mil pedidos e ~54 mil itens no dataset X.

### Slide 11: Configuração experimental

- 50 instâncias, 30 execuções (sementes) por instância, limite de 600 s por execução.
- Implementação em Java 21, em um Intel i5-13420H com 16 GB de RAM.
- **Por que 30 execuções:** o ILS-VND é estocástico. Repetir com sementes diferentes permite avaliar a média e a variação.

### Slide 12: Protocolo experimental

**RPD (*Relative Percentage Deviation*)**

RPD = (f* − f) / f* × 100%

- f*: MSC da instância. f: objetivo obtido pelo algoritmo.
- RPD = 0% significa que o algoritmo atingiu a MSC. Quanto menor, melhor.
- Normaliza o desvio, o que permite comparar instâncias com objetivos de escalas diferentes.

**Teste de Friedman (teste global)**

- Teste não paramétrico que ranqueia os k = 3 algoritmos em cada uma das N = 50 instâncias e compara os *rankings* médios R_j.
- H₀: todos os algoritmos são equivalentes. Se p for pequeno, existe pelo menos uma diferença, e é preciso descobrir onde.
- É não paramétrico porque não supõe distribuição normal dos dados.

**Teste de Wilcoxon pareado (par a par)**

- Compara dois algoritmos pelas diferenças de RPD d_i em cada instância.
- Ordena |d_i| em postos e soma os postos das diferenças positivas e negativas separadamente. W é a menor das duas somas.
- Considera o sinal (quem venceu) e a magnitude (por quanto).
- **Ajuste de Holm:** corrige os p-valores porque são feitas várias comparações. Sem ajuste, a chance de um falso positivo cresce com o número de testes. Nível de significância α = 0,05.

### Slide 13: Visão geral

**Mensagem:** a tabela resume qualidade e tempo de cada algoritmo por dataset.

**Colunas**

- **RPD médio ± DP:** desvio médio em relação à MSC e o desvio padrão entre instâncias.
- **RPD mediano:** menos sensível a instâncias extremas.
- **RPD ≤ 1%:** em quantas instâncias o algoritmo ficou a até 1% da MSC.
- **#MSC:** em quantas instâncias atingiu a MSC.
- **Tempo médio ± DP.**

**Consolidado (50 instâncias)**

| Algoritmo                | RPD médio | RPD ≤ 1% | #MSC  | Tempo médio |
| ------------------------ | --------- | -------- | ----- | ----------- |
| *OrderBased*             | 81,47%    | 1/50     | 1/50  | 15,9 s      |
| *AisleBased*             | 3,70%     | 28/50    | 16/50 | 2,0 s       |
| ILS-VND                  | 0,18%     | 47/50    | 36/50 | 475,3 s     |
| Santos e Baldotto (2025) | 0,02%     | 50/50    | 43/50 | 190,8 s     |

**Pontos para falar**

- O *OrderBased* fica longe da MSC em todos os datasets (69% a 90%).
- O *AisleBased* é o mais rápido (cerca de 2 s) e já chega perto da MSC, principalmente em B e X.
- O ILS-VND chega a 0,18% de RPD médio e mediana 0%, mas usa quase todo o limite de 600 s em B e X.
- Santos e Baldotto (2025) é o método de referência da literatura e tem o menor RPD.

### Slide 14: Distribuição do RPD

- **(a) Visão global:** o *OrderBased* concentra a maioria das instâncias entre 80% e 95% de RPD. Os outros três ficam próximos de zero.
- **(b) Ampliação:** o *AisleBased* varia de 0% a ~13%, com mediana ~0,7%. O ILS-VND e a referência ficam praticamente em 0%, com poucos pontos acima (máximo de ~3% no ILS-VND).
- Losango branco = média. Linha laranja = mediana.

### Slide 15: Tempo × qualidade

- Gráfico bi-logarítmico: eixo x é o tempo médio e eixo y é o RPD médio. Quanto mais perto do canto inferior esquerdo, melhor.
- A **fronteira de Pareto** do consolidado liga *AisleBased* (rápido, RPD ~3,7%) e Santos e Baldotto (mais lento, RPD ~0,02%).
- O *OrderBased* é dominado: é mais lento e pior que o *AisleBased*.
- O ILS-VND fica fora da fronteira: é mais lento e tem RPD maior que a referência.
- A linha tracejada só liga os dois pontos. Ela não representa configurações intermediárias.

### Slide 16: Análise das heurísticas construtivas

**Mensagem:** explica por que o *AisleBased* vence o *OrderBased*.

- **(a) Unidades coletadas:** o *OrderBased* coleta mais unidades por instância.
- **(b) Corredores visitados:** o *OrderBased* abre cerca de uma ordem de grandeza a mais de corredores (média de ~100 a ~300 contra ~10 a ~20 do *AisleBased*).
- Como o objetivo é unidades/corredor, o denominador grande derruba o *OrderBased*. Escolher corredores primeiro mantém o denominador pequeno.

### Slide 17: Refinamento do *AisleBased* pelo ILS-VND

- Mostra as 22 instâncias em que o *AisleBased* tinha RPD inicial acima de 1%.
- Triângulo azul = solução inicial s₀. Círculo vermelho = média das soluções finais s* (30 sementes).
- O ILS-VND reduz o RPD em todas. Exemplos: A/0009 cai de ~31% para quase 0%; A/0003 e A/0011 caem de ~25-29% para 0%.
- Os maiores desvios restantes estão em X/0004 (~3%), A/0010 (~2%) e X/0001 (~1,5%).

### Slide 18: ILS-VND × Santos e Baldotto (2025)

- Boxplot do RPD por dataset para as duas meta-heurísticas.
- As duas medianas ficam em 0% nos três datasets.
- O ILS-VND tem alguns *outliers* (até ~2,1% em A e ~3% em X), o que puxa a média para cima.
- A referência é mais estável: todos os pontos ficam abaixo de ~0,25%.

### Slide 19: Comparação com a referência

**Friedman:** χ²_F(2) = 57,32, p < 0,001. Os algoritmos não são equivalentes, e os testes par a par mostram onde estão as diferenças.

| Comparação (A × B)                  | Com diferença | Empates | Vitórias A / B | r_rb | p (Holm) |
| ----------------------------------- | ------------- | ------- | -------------- | ---- | -------- |
| Santos e Baldotto × ILS-VND         | 18            | 32      | 13 / 5         | 0,58 | 0,031    |
| Santos e Baldotto × *AisleBased*    | 34            | 16      | 34 / 0         | 1,00 | < 0,001  |
| ILS-VND × *AisleBased*              | 33            | 17      | 33 / 0         | 1,00 | < 0,001  |

**Leitura**

- O ILS-VND é estatisticamente melhor que o *AisleBased*: vence em todas as 33 instâncias com diferença.
- A referência é estatisticamente melhor que o ILS-VND (p = 0,031), mas as duas empatam em 32 das 50 instâncias, e o ILS-VND vence em 5.
- Diferenças relativas de até 0,01% no objetivo contam como empate e não entram no teste.

**Conceitos**

- **r_rb (correlação rank-bisserial):** tamanho de efeito do Wilcoxon, de −1 a 1. r_rb = 1 significa que A vence em todas as instâncias com diferença. r_rb = 0,58 é um efeito moderado a forte a favor de A.
- **Significância × tamanho de efeito:** o p-valor diz se a diferença é real. O r_rb diz o quanto ela pesa.

### Slide 20: Novas MSC: B/0012 e B/0013

**Mensagem:** o ILS-VND encontrou soluções melhores que as melhores conhecidas em duas instâncias.

| Instância | Algoritmo         | Corredores | Unid. méd. | Unid. máx. | f méd.     | f máx.     | MSC anterior       |
| --------- | ----------------- | ---------- | ---------- | ---------- | ---------- | ---------- | ------------------ |
| B/0012    | *AisleBased*      | 11         | 6.244,0    | 6.244      | 567,64     | 567,64     | 567,64 (6.244/11)  |
| B/0012    | **ILS-VND**       | 11         | 6.245,9    | 6.252      | **567,81** | **568,36** |                    |
| B/0012    | Santos e Baldotto | 11         | 6.244,0    | 6.244      | 567,64     | 567,64     |                    |
| B/0013    | *AisleBased*      | 9          | 6.761,0    | 6.761      | 751,22     | 751,22     | 757,00 (6.813/9)   |
| B/0013    | **ILS-VND**       | 9          | 6.814,0    | 6.814      | **757,11** | **757,11** |                    |
| B/0013    | Santos e Baldotto | 9          | 6.811,0    | 6.811      | 756,78     | 756,78     |                    |

- Com o mesmo número de corredores, o ILS-VND coleta mais unidades, o que aumenta o objetivo.
- Em B/0013, o ILS-VND supera a MSC anterior (757,00) em todas as 30 sementes.

---

## Seção 5: Conclusões

### Slide 21: Conclusões e trabalhos futuros

**Conclusões**

- **Escolher corredores primeiro** reduz o RPD médio de 81,47% (*OrderBased*) para 3,70% (*AisleBased*), em cerca de 2 s.
- **O ILS-VND, sem *solver*,** chega a RPD médio de 0,18% e atinge a MSC em 36 das 50 instâncias.
- O ILS-VND fica próximo do método de referência e encontrou **novas MSC** em B/0012 e B/0013.

**Limitações e trabalhos futuros**

- Comparar os métodos sob o mesmo paralelismo e com outras abordagens, para que os tempos sejam diretamente comparáveis.
- Hibridizar o ILS-VND com métodos exatos (por exemplo, usar um *solver* dentro de uma vizinhança).

### Slide 22: Agradecimentos

Encerramento com título, autor, orientadores e instituição.
