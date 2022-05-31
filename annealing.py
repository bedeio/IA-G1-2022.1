import numpy as np
import random

# constantes
VIDAS = 8
ETAPAS = 31
PERSONAGENS = 7

# associacao entre etapas e suas dificuldades
# o indice na lista corresponde ao numero da etapa
dificuldades = []
for i in range(1, ETAPAS + 1):
    dificuldades.append(10 * i)

personagens = {
    0: ("aang", 1.8),
    1: ("zukko", 1.6),
    2: ("toph", 1.6),
    3: ("katara", 1.6),
    4: ("sokka", 1.4),
    5: ("appa", 0.9),
    6: ("momo", 0.7),
}
# print(dificuldades)
print("Len:", len(dificuldades))


def print_sol(sol):
    v = sol.view()
    v.shape = (ETAPAS, PERSONAGENS)
    print(v)


# garante que na solucao cada personagem tem ate 8 vidas
def valida_sol(sol, debug=False):
    v = sol.view()
    v.shape = (ETAPAS, PERSONAGENS)
    idx = 0
    for row in v:
        soma = np.sum(row)
        if soma < 1:
            if debug:
                print(f"Solucao invalida, etapa {idx} esta sem personagem!")
            return False
        idx += 1

    for i in range(PERSONAGENS):
        vidas = v[:, i].sum()
        p_ind = [*personagens][i]
        personagem = personagens[p_ind][0]
        # print(f"{personagem}: {vidas}")
        if vidas > VIDAS or vidas < 0:
            if debug:
                print(f"SOLUCAO INVALIDA, {personagem} TEM {vidas}!!")
            return False

    return True


#
# annealing funcs
#

# avalia o tempo levado de acordo com uma solucao
def total_cost(sol):
    tempo = 0
    v = sol.view()
    v.shape = (ETAPAS, PERSONAGENS)
    idx = 0
    for row in v:
        agilidade_etapa = 0
        for i in range(PERSONAGENS):
            # print(idx)
            if row[i] == 1:
                p_ind = [*personagens][i]
                agilidade_etapa += personagens[p_ind][1]

        if agilidade_etapa == 0:
            agilidade_etapa = 1e-12

        tempo += dificuldades[idx] / agilidade_etapa
        idx += 1

    return tempo


# troca a posicao de dois bits correspondentes em diferentes etapas
def swap_bit_op(sol):
    personagem = random.randrange(0, PERSONAGENS)
    rands = random.sample(range(0, ETAPAS), 2)
    e1, e2 = rands[0], rands[1]
    n_idx1 = PERSONAGENS * e1 + personagem
    n_idx2 = PERSONAGENS * e2 + personagem
    sol[[n_idx1, n_idx2]] = sol[[n_idx2, n_idx1]]


def swap_bit_op_n(sol, n):
    personagens = random.sample(range(0, PERSONAGENS), n)
    rands = random.sample(range(0, ETAPAS), 2)
    e1, e2 = rands[0], rands[1]

    for p in personagens:
        n_idx1 = PERSONAGENS * e1 + p
        n_idx2 = PERSONAGENS * e2 + p
        sol[[n_idx1, n_idx2]] = sol[[n_idx2, n_idx1]]


# troca as solucoes de duas etapas
def swap_stage_op(sol):
    rands = random.sample(range(0, ETAPAS), 2)
    i = rands[0]
    j = rands[1]
    v = sol.view()
    v.shape = (ETAPAS, PERSONAGENS)
    v[[i, j]] = v[[j, i]]


# gets best neighbor state
def rand_neighbor(curr_sol):
    stage_sol = np.copy(curr_sol)
    swap_stage_op(stage_sol)
    stage_2_sol = np.copy(curr_sol)
    swap_stage_op(stage_2_sol)
    swap_stage_op(stage_2_sol)
    stage_3_sol = np.copy(curr_sol)
    swap_stage_op(stage_3_sol)
    swap_stage_op(stage_3_sol)
    swap_stage_op(stage_3_sol)
    # stage_4_sol = np.copy(curr_sol)
    # swap_stage_op(stage_4_sol)
    # swap_stage_op(stage_4_sol)
    # swap_stage_op(stage_4_sol)
    # swap_stage_op(stage_4_sol)

    bit_sol = np.copy(curr_sol)
    swap_bit_op(bit_sol)
    bit_2_sol = np.copy(curr_sol)
    swap_bit_op_n(bit_2_sol, 2)
    bit_3_sol = np.copy(curr_sol)
    swap_bit_op_n(bit_3_sol, 3)
    bit_4_sol = np.copy(curr_sol)
    swap_bit_op_n(bit_4_sol, 4)
    bit_5_sol = np.copy(curr_sol)
    swap_bit_op_n(bit_5_sol, 5)
    bit_6_sol = np.copy(curr_sol)
    swap_bit_op_n(bit_6_sol, 6)

    stage_cost = total_cost(stage_sol)
    stage_2_cost = total_cost(stage_2_sol)
    stage_3_cost = total_cost(stage_3_sol)
    # stage_4_cost = total_cost(stage_4_sol)
    bit_cost = total_cost(bit_sol)
    bit_2_cost = total_cost(bit_2_sol)
    bit_3_cost = total_cost(bit_3_sol)
    bit_4_cost = total_cost(bit_4_sol)
    bit_5_cost = total_cost(bit_5_sol)
    bit_6_cost = total_cost(bit_6_sol)

    sols = [
        (stage_cost, stage_sol),
        (stage_2_cost, stage_2_sol),
        (stage_3_cost, stage_3_sol),
        # (stage_4_cost, stage_4_sol),
        (bit_cost, bit_sol),
        (bit_2_cost, bit_2_sol),
        (bit_3_cost, bit_3_sol),
        (bit_4_cost, bit_4_sol),
        (bit_5_cost, bit_5_sol),
        (bit_6_cost, bit_6_sol),
    ]

    for idx, s in enumerate(sols):
        if not valida_sol(s[1]):
            sols.pop(idx)

    chosen = min(sols, key=lambda t: t[0])
    return chosen[1], chosen[0]


def acceptance_prob(cost, n_cost, temp):
    if n_cost <= cost:
        return 1
    else:
        # metropolis criterion
        p = np.exp(-(n_cost - cost) / temp)
        return p


# logarithmic cooling
def temperature(start_temp, curr_temp, alpha, iter):
    if curr_temp < 0.000025:
        return 0.000025
    return start_temp / (1 + alpha * iter * iter)
    # return curr_temp * alpha


def solve(start_state, start_temp, alpha, maxiter=10000):
    curr_state = start_state
    curr_cost = total_cost(curr_state)
    curr_temp = start_temp

    for iter in range(maxiter):
        # curr_temp = temperature(start_temp, curr_temp, alpha, float(iter))
        curr_temp = temperature(start_temp, curr_temp, alpha, iter)
        neighbor_state, neighbor_cost = rand_neighbor(curr_state)
        if acceptance_prob(curr_cost, neighbor_cost, curr_temp) > np.random.rand():
            curr_state = neighbor_state
            curr_cost = neighbor_cost

    return curr_state, total_cost(curr_state)


# largura do vetor de solucoes
# 7 bits para cada etapa
width = PERSONAGENS * len(dificuldades)
sol = np.zeros(width, dtype=int)

# montar solucao inicial
v = sol.view()
v.shape = (ETAPAS, PERSONAGENS)
fill = [0, 1, 2, 3, 4, 5, 6] * VIDAS
# random.shuffle(fill)
row = 0
while len(fill) > 0:
    fill_idx = fill[-1]
    if v[row, fill_idx] == 0:
        v[row, fill_idx] = 1
        fill.pop()

    row += 1
    if row >= ETAPAS:
        row = 0

valida_sol(sol, debug=True)
tempo = total_cost(sol)
print("Tempo total inicial:", tempo)

new_sol, new_cost = solve(start_state=sol, start_temp=5000.0, alpha=0.98, maxiter=3000)
if valida_sol(new_sol):
    print("Tempo total apos annealing:", new_cost)
    # print(new_sol)
else:
    print("Solucao invalida!")
