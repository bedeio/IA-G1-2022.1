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
def valida_sol(sol):
    v = sol.view()
    v.shape = (ETAPAS, PERSONAGENS)
    for i in range(PERSONAGENS):
        vidas = v[:, i].sum()
        p_ind = [*personagens][i]
        personagem = personagens[p_ind][0]
        # print(f"{personagem}: {vidas}")
        if vidas > 8 or vidas < 0:
            # print(f"SOLUCAO INVALIDA, {personagem} TEM {vidas}!!")
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
            agilidade_etapa = 1

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
    bit_sol = np.copy(curr_sol)
    swap_bit_op(bit_sol)
    two_bit_sol = np.copy(curr_sol)
    swap_bit_op(two_bit_sol)
    swap_bit_op(two_bit_sol)
    three_bit_sol = np.copy(curr_sol)
    swap_bit_op(three_bit_sol)
    swap_bit_op(three_bit_sol)
    swap_bit_op(three_bit_sol)
    four_bit_sol = np.copy(curr_sol)
    swap_bit_op(four_bit_sol)
    swap_bit_op(four_bit_sol)
    swap_bit_op(four_bit_sol)
    swap_bit_op(four_bit_sol)
    five_bit_sol = np.copy(curr_sol)
    swap_bit_op(five_bit_sol)
    swap_bit_op(five_bit_sol)
    swap_bit_op(five_bit_sol)
    swap_bit_op(five_bit_sol)
    swap_bit_op(five_bit_sol)
    six_bit_sol = np.copy(curr_sol)
    swap_bit_op(six_bit_sol)
    swap_bit_op(six_bit_sol)
    swap_bit_op(six_bit_sol)
    swap_bit_op(six_bit_sol)
    swap_bit_op(six_bit_sol)
    swap_bit_op(six_bit_sol)
    seven_bit_sol = np.copy(curr_sol)
    swap_bit_op(seven_bit_sol)
    swap_bit_op(seven_bit_sol)
    swap_bit_op(seven_bit_sol)
    swap_bit_op(seven_bit_sol)
    swap_bit_op(seven_bit_sol)
    swap_bit_op(seven_bit_sol)

    stage_cost = total_cost(stage_sol)
    bit_cost = total_cost(bit_sol)
    two_bit_cost = total_cost(two_bit_sol)
    three_bit_cost = total_cost(three_bit_sol)
    four_bit_cost = total_cost(four_bit_sol)
    five_bit_cost = total_cost(five_bit_sol)
    six_bit_cost = total_cost(six_bit_sol)
    seven_bit_cost = total_cost(seven_bit_sol)
    sols = [
        (stage_cost, stage_sol),
        (bit_cost, bit_sol),
        (two_bit_cost, two_bit_sol),
        (three_bit_cost, three_bit_sol),
        (four_bit_cost, four_bit_sol),
        (five_bit_cost, five_bit_sol),
        (six_bit_cost, six_bit_sol),
        (seven_bit_cost, seven_bit_sol),
    ]
    chosen = min(sols, key=lambda t: t[0])
    # if stage_cost < bit_cost:
    #     return stage_sol, stage_cost
    return chosen[1], chosen[0]


def acceptance_prob(cost, n_cost, temp):
    if n_cost < cost:
        return 1
    else:
        # metropolis criterion
        p = np.exp(-(n_cost - cost) / temp)
        return p


# logarithmic cooling
def temperature(start_temp, curr_temp, alpha, iter):
    if curr_temp < 0.00001:
        return 0.00001
    # return start_temp / (1 + alpha * np.log(1 + iter))
    return curr_temp * alpha
    # return curr_temp - alpha


def solve(start_state, start_temp, alpha, maxiter=10000):
    curr_state = start_state
    curr_cost = total_cost(curr_state)
    curr_temp = start_temp

    for iter in range(maxiter):
        curr_temp = temperature(start_temp, curr_temp, alpha, float(iter))
        neighbor_state, neighbor_cost = rand_neighbor(curr_state)
        if acceptance_prob(curr_cost, neighbor_cost, curr_temp) > np.random.rand():
            curr_state = neighbor_state
            curr_cost = neighbor_cost
        # curr_temp = temperature(start_temp, curr_temp, alpha, iter)

    return curr_state, total_cost(curr_state)


# largura do vetor de solucoes
# 7 bits para cada etapa
width = PERSONAGENS * len(dificuldades)
sol = np.zeros(width, dtype=int)

# montar solucao inicial
# saturar as primeiras 7 etapas
fill_width = PERSONAGENS * VIDAS
for i in range(fill_width):
    sol[i] = 1

unique, counts = np.unique(sol, return_counts=True)
unique_count = dict(zip(unique, counts))
print("Resumo:", unique_count)
valida_sol(sol)
tempo = total_cost(sol)

while True:
    np.random.shuffle(sol)
    if valida_sol(sol):
        break

print("Tempo total:", tempo)
# print_sol(sol)


new_sol, new_cost = solve(start_state=sol, start_temp=7500.0, alpha=0.98, maxiter=10000)

if valida_sol(new_sol):
    print("Tempo total apos annealing:", new_cost)
    print(new_sol)
else:
    print("Solucao invalida!")
