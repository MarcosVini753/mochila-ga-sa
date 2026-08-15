import math

LINHAS = 6
COLUNAS = 7

VAZIO = 0
JOGADOR = 1
IA = 2


def criar_tabuleiro():
    return [[VAZIO for _ in range(COLUNAS)] for _ in range(LINHAS)]


def imprimir_tabuleiro(tabuleiro):
    print()

    for linha in tabuleiro:
        print("|", end=" ")

        for elemento in linha:
            if elemento == VAZIO:
                simbolo = "."
            elif elemento == JOGADOR:
                simbolo = "X"
            else:
                simbolo = "O"

            print(simbolo, end=" ")

        print("|")

    print("  1 2 3 4 5 6 7")
    print()


def coluna_valida(tabuleiro, coluna):
    return tabuleiro[0][coluna] == VAZIO


def obter_colunas_validas(tabuleiro):
    colunas = []

    for coluna in range(COLUNAS):
        if coluna_valida(tabuleiro, coluna):
            colunas.append(coluna)

    return colunas


def jogar_peca(tabuleiro, coluna, jogador):
    for linha in range(LINHAS - 1, -1, -1):
        if tabuleiro[linha][coluna] == VAZIO:
            tabuleiro[linha][coluna] = jogador
            return


def verificar_vitoria(tabuleiro, jogador):

    # Horizontal
    for linha in range(LINHAS):
        for coluna in range(COLUNAS - 3):
            if (
                tabuleiro[linha][coluna] == jogador
                and tabuleiro[linha][coluna + 1] == jogador
                and tabuleiro[linha][coluna + 2] == jogador
                and tabuleiro[linha][coluna + 3] == jogador
            ):
                return True

    # Vertical
    for linha in range(LINHAS - 3):
        for coluna in range(COLUNAS):
            if (
                tabuleiro[linha][coluna] == jogador
                and tabuleiro[linha + 1][coluna] == jogador
                and tabuleiro[linha + 2][coluna] == jogador
                and tabuleiro[linha + 3][coluna] == jogador
            ):
                return True

    # Diagonal \
    for linha in range(LINHAS - 3):
        for coluna in range(COLUNAS - 3):
            if (
                tabuleiro[linha][coluna] == jogador
                and tabuleiro[linha + 1][coluna + 1] == jogador
                and tabuleiro[linha + 2][coluna + 2] == jogador
                and tabuleiro[linha + 3][coluna + 3] == jogador
            ):
                return True

    # Diagonal /
    for linha in range(3, LINHAS):
        for coluna in range(COLUNAS - 3):
            if (
                tabuleiro[linha][coluna] == jogador
                and tabuleiro[linha - 1][coluna + 1] == jogador
                and tabuleiro[linha - 2][coluna + 2] == jogador
                and tabuleiro[linha - 3][coluna + 3] == jogador
            ):
                return True

    return False


def avaliar_janela(janela):
    pontuacao = 0

    quantidade_ia = janela.count(IA)
    quantidade_jogador = janela.count(JOGADOR)
    quantidade_vazios = janela.count(VAZIO)

    if quantidade_ia == 4:
        pontuacao += 1000

    elif quantidade_ia == 3 and quantidade_vazios == 1:
        pontuacao += 50

    elif quantidade_ia == 2 and quantidade_vazios == 2:
        pontuacao += 10

    if quantidade_jogador == 4:
        pontuacao -= 1000

    elif quantidade_jogador == 3 and quantidade_vazios == 1:
        pontuacao -= 50

    elif quantidade_jogador == 2 and quantidade_vazios == 2:
        pontuacao -= 10

    return pontuacao


def avaliar_tabuleiro(tabuleiro):
    pontuacao = 0

    # Horizontal
    for linha in range(LINHAS):
        for coluna in range(COLUNAS - 3):
            janela = [
                tabuleiro[linha][coluna],
                tabuleiro[linha][coluna + 1],
                tabuleiro[linha][coluna + 2],
                tabuleiro[linha][coluna + 3]
            ]

            pontuacao += avaliar_janela(janela)

    # Vertical
    for linha in range(LINHAS - 3):
        for coluna in range(COLUNAS):
            janela = [
                tabuleiro[linha][coluna],
                tabuleiro[linha + 1][coluna],
                tabuleiro[linha + 2][coluna],
                tabuleiro[linha + 3][coluna]
            ]

            pontuacao += avaliar_janela(janela)

    # Diagonal \
    for linha in range(LINHAS - 3):
        for coluna in range(COLUNAS - 3):
            janela = [
                tabuleiro[linha][coluna],
                tabuleiro[linha + 1][coluna + 1],
                tabuleiro[linha + 2][coluna + 2],
                tabuleiro[linha + 3][coluna + 3]
            ]

            pontuacao += avaliar_janela(janela)

    # Diagonal /
    for linha in range(3, LINHAS):
        for coluna in range(COLUNAS - 3):
            janela = [
                tabuleiro[linha][coluna],
                tabuleiro[linha - 1][coluna + 1],
                tabuleiro[linha - 2][coluna + 2],
                tabuleiro[linha - 3][coluna + 3]
            ]

            pontuacao += avaliar_janela(janela)

    return pontuacao


def estado_terminal(tabuleiro):

    if verificar_vitoria(tabuleiro, JOGADOR):
        return True

    if verificar_vitoria(tabuleiro, IA):
        return True

    if len(obter_colunas_validas(tabuleiro)) == 0:
        return True

    return False


def minimax(tabuleiro, profundidade, maximizando):

    colunas_validas = obter_colunas_validas(tabuleiro)

    if estado_terminal(tabuleiro):

        if verificar_vitoria(tabuleiro, IA):
            return None, 100000

        elif verificar_vitoria(tabuleiro, JOGADOR):
            return None, -100000

        else:
            return None, 0

    if profundidade == 0:
        return None, avaliar_tabuleiro(tabuleiro)

    if maximizando:

        melhor_valor = -math.inf
        melhor_coluna = colunas_validas[0]

        for coluna in colunas_validas:

            novo_tabuleiro = [
                linha[:] for linha in tabuleiro
            ]

            jogar_peca(novo_tabuleiro, coluna, IA)

            _, valor = minimax(
                novo_tabuleiro,
                profundidade - 1,
                False
            )

            if valor > melhor_valor:
                melhor_valor = valor
                melhor_coluna = coluna

        return melhor_coluna, melhor_valor

    else:

        melhor_valor = math.inf
        melhor_coluna = colunas_validas[0]

        for coluna in colunas_validas:

            novo_tabuleiro = [
                linha[:] for linha in tabuleiro
            ]

            jogar_peca(
                novo_tabuleiro,
                coluna,
                JOGADOR
            )

            _, valor = minimax(
                novo_tabuleiro,
                profundidade - 1,
                True
            )

            if valor < melhor_valor:
                melhor_valor = valor
                melhor_coluna = coluna

        return melhor_coluna, melhor_valor


def jogar():

    tabuleiro = criar_tabuleiro()

    print("============================")
    print("       CONNECT FOUR")
    print("============================")
    print("Você é X")
    print("Computador é O")

    imprimir_tabuleiro(tabuleiro)

    turno = JOGADOR

    while True:

        if turno == JOGADOR:

            try:
                coluna = int(
                    input("Escolha uma coluna (1-7): ")
                ) - 1

            except ValueError:
                print("Digite um número válido.")
                continue

            if coluna < 0 or coluna >= COLUNAS:
                print("Coluna inválida.")
                continue

            if not coluna_valida(tabuleiro, coluna):
                print("Essa coluna está cheia.")
                continue

            jogar_peca(
                tabuleiro,
                coluna,
                JOGADOR
            )

            imprimir_tabuleiro(tabuleiro)

            if verificar_vitoria(tabuleiro, JOGADOR):
                print("Você venceu!")
                break

            turno = IA

        else:

            print("Computador pensando...")

            coluna, valor = minimax(
                tabuleiro,
                profundidade=4,
                maximizando=True
            )

            jogar_peca(
                tabuleiro,
                coluna,
                IA
            )

            print(
                "Computador jogou na coluna:",
                coluna + 1
            )

            imprimir_tabuleiro(tabuleiro)

            if verificar_vitoria(tabuleiro, IA):
                print("O computador venceu!")
                break

            turno = JOGADOR

        if len(obter_colunas_validas(tabuleiro)) == 0:
            print("Empate!")
            break


if __name__ == "__main__":
    jogar()
