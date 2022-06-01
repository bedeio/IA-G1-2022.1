import numpy as np
import random

# constantes
VIDAS = 8
ETAPAS = 31
PERSONAGENS = 7

# associacao entre etapas e suas dificuldades
# o indice no dict corresponde ao numero da etapa
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

# imprimir solucao formatada
def print_sol(sol):
    v = sol.view()
    v.shape = (ETAPAS, PERSONAGENS)
    print(v)


# numa solucao valida:
# - cada personagem tem ate 8 vidas
# - toda etapa tem pelo menos 1 personagem
# - pelo menos um personagem sobrevive no final (tem mais de 0 vidas)
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

    total_vidas = 0
    for i in range(PERSONAGENS):
        vidas = v[:, i].sum()
        personagem = personagens[i][0]
        total_vidas += vidas

        if vidas > VIDAS or vidas < 0:
            if debug:
                print(f"SOLUCAO INVALIDA, {personagem} TEM {vidas}!!")
            return False

    return total_vidas < (PERSONAGENS * VIDAS)


class SimAnnealing:
    def total_cost(self, sol):
        # avalia o tempo levado de acordo com uma solucao
        tempo = 0
        v = sol.view()
        v.shape = (ETAPAS, PERSONAGENS)
        idx = 0
        for row in v:
            agilidade_etapa = 0
            for i in range(PERSONAGENS):
                if row[i] == 1:
                    agilidade_etapa += personagens[i][1]

            if agilidade_etapa == 0:
                agilidade_etapa = 1e-12

            tempo += dificuldades[idx] / agilidade_etapa
            idx += 1

        return tempo

    def swap_bit_op(self, sol):
        # troca a posicao de dois bits correspondentes em diferentes etapas
        personagem = random.randrange(0, PERSONAGENS)
        rands = random.sample(range(0, ETAPAS), 2)
        e1, e2 = rands[0], rands[1]
        n_idx1 = PERSONAGENS * e1 + personagem
        n_idx2 = PERSONAGENS * e2 + personagem
        sol[[n_idx1, n_idx2]] = sol[[n_idx2, n_idx1]]

    def swap_bit_op_n(self, sol, n):
        # troca a posicao de n bits correspondentes em diferentes etapas
        # n deve ser menor que $PERSONAGENS
        personagens = random.sample(range(0, PERSONAGENS), n)
        rands = random.sample(range(0, ETAPAS), 2)
        e1, e2 = rands[0], rands[1]

        for p in personagens:
            n_idx1 = PERSONAGENS * e1 + p
            n_idx2 = PERSONAGENS * e2 + p
            sol[[n_idx1, n_idx2]] = sol[[n_idx2, n_idx1]]

    def swap_stage_op(self, sol):
        # troca as solucoes de duas etapas
        rands = random.sample(range(0, ETAPAS), 2)
        i = rands[0]
        j = rands[1]
        v = sol.view()
        v.shape = (ETAPAS, PERSONAGENS)
        v[[i, j]] = v[[j, i]]

    def rand_neighbor(self, curr_sol):
        # aplica os operadores para solucoes "vizinhas"
        # e usa o que corresponde ao melhor resultado
        # OBS: os operadores utilizados geram solucoes validas
        stage_sol = np.copy(curr_sol)
        self.swap_stage_op(stage_sol)

        bit_sol = np.copy(curr_sol)
        self.swap_bit_op(bit_sol)
        bit_2_sol = np.copy(curr_sol)
        self.swap_bit_op_n(bit_2_sol, 2)
        bit_3_sol = np.copy(curr_sol)
        self.swap_bit_op_n(bit_3_sol, 3)
        bit_4_sol = np.copy(curr_sol)
        self.swap_bit_op_n(bit_4_sol, 4)
        bit_5_sol = np.copy(curr_sol)
        self.swap_bit_op_n(bit_5_sol, 5)
        bit_6_sol = np.copy(curr_sol)
        self.swap_bit_op_n(bit_6_sol, 6)

        stage_cost = self.total_cost(stage_sol)
        bit_cost = self.total_cost(bit_sol)
        bit_2_cost = self.total_cost(bit_2_sol)
        bit_3_cost = self.total_cost(bit_3_sol)
        bit_4_cost = self.total_cost(bit_4_sol)
        bit_5_cost = self.total_cost(bit_5_sol)
        bit_6_cost = self.total_cost(bit_6_sol)

        sols = [
            (stage_cost, stage_sol),
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

    def acceptance_prob(self, cost, n_cost, temp):
        if n_cost < cost:
            return 1
        else:
            # metropolis criterion
            p = np.exp(-(n_cost - cost) / temp)
            return p

    def temperature(self, start_temp, curr_temp, alpha, iter):
        # linear multiplicative cooling
        return start_temp / (1 + alpha * iter)

    def solve(self, start_state, start_temp, alpha, maxiter=10000):
        curr_state = start_state
        curr_cost = self.total_cost(curr_state)
        curr_temp = start_temp

        for iter in range(maxiter):

            curr_temp = self.temperature(start_temp, curr_temp, alpha, iter)
            neighbor_state, neighbor_cost = self.rand_neighbor(curr_state)

            if (
                self.acceptance_prob(curr_cost, neighbor_cost, curr_temp)
                > np.random.rand()
            ):
                curr_state = neighbor_state
                curr_cost = neighbor_cost

        # print("Ended at temp:", curr_temp)
        return curr_state, self.total_cost(curr_state)


def initial_solution():
    # Gera uma solucao inicial válida
    # para tal iteramos sobre as etapas aleatoriamente
    # acrescentando personagens até que acabem suas vidas.
    # Estamos assumindo que todos os personagens serão usados 8 vezes,
    # com excessão do Momo, que tem a menor agilidade

    # inicializacao
    width = PERSONAGENS * len(dificuldades)
    sol = np.zeros(width, dtype=int)

    # montar solucao inicial
    v = sol.view()
    v.shape = (ETAPAS, PERSONAGENS)
    fill = [0, 1, 2, 3, 4, 5, 6] * VIDAS
    fill.remove(6)
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
    return sol


def init():
    # Funcao de conveniencia para inicializar o processo de annealing
    sol = initial_solution()
    solver = SimAnnealing()
    tempo_inicial = solver.total_cost(sol)
    print("Tempo total inicial:", tempo_inicial)

    best_sol = []
    best_cost = np.inf
    for i in range(10):
        new_sol, new_cost = solver.solve(
            start_state=sol, start_temp=18.0, alpha=8, maxiter=10000
        )
        if new_cost < best_cost:
            best_cost = new_cost
            best_sol = new_sol

    if valida_sol(best_sol, debug=True):
        print("Tempo total apos annealing:", best_cost)
        print_sol(best_sol)
    else:
        print("Solucao encontrada é inválida!")


if __name__ == "__main__":
    init()
