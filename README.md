# IA-G1-2022.1 - Thomas Botelho, Emanuel Umbellino

Trabalho de IA 1

O projeto consiste de duas partes,

- Uma interface que carrega um mapa de um arquivo externo, mostra um caminho calculado com A\* em tempo real e mostra os personagens escolhidos para cada etapa a partir de um arquivo com resultados pré-calculado.
- Um solver que usa o processo de Simulated Annealing para solucionar o problema da escolha de personagens para cada etapa.

---

A interface depende da biblioteca Pygame para desenhar o mapa na tela. Para executá-la use o comando

```
python main.py
```

A partir disto use a barra de espaço para avançar a etapa e a tecla 'i' para mostrar os tempos de deslocamento de realização de cada caminho.

---

Para executar o procedimento de simulated annealing use o comando

```
python annealing.py
```

É preciso ter a biblioteca NumPy instalada para tal.

O programa executa o procedimento 20 vezes e extrai o melhor resultado.
O melhor resultado obtido até o momento foi

```
Tempo total apos annealing: 1822.1074358062847
[[0 0 0 0 0 0 1]
 [0 0 0 0 0 1 0]
 [0 0 0 0 0 1 0]
 [0 0 0 0 1 0 0]
 [0 0 0 0 1 0 0]
 [0 0 0 1 0 0 0]
 [0 0 0 1 0 0 0]
 [1 0 0 0 0 0 0]
 [1 0 0 0 0 0 0]
 [0 0 0 0 1 0 1]
 [0 0 0 0 1 0 1]
 [0 0 0 1 0 0 1]
 [0 1 0 0 0 0 1]
 [0 0 1 0 0 1 0]
 [0 0 1 0 0 1 0]
 [0 1 0 0 0 1 0]
 [1 0 0 0 0 1 0]
 [1 0 0 0 0 1 0]
 [1 0 0 0 0 1 0]
 [0 1 0 0 1 0 0]
 [0 0 1 0 1 0 0]
 [0 1 1 0 0 0 0]
 [0 1 0 1 0 0 0]
 [0 1 1 0 0 0 0]
 [0 1 1 0 0 0 0]
 [0 1 1 0 0 0 0]
 [1 0 0 1 0 0 0]
 [1 0 0 1 0 0 0]
 [1 0 1 0 0 0 0]
 [0 0 0 1 1 0 1]
 [0 0 0 1 1 0 1]]
```

Note que cada posição no vetor corresponde a um personagem.

```
1: Aang
2: Zukko
3: Toph
4: Katara
5: Sokka
6: Appa
7: Momo
```
