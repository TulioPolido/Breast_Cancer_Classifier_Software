# trabPI

-> Caracterizar uma imagem ou região selecionada através de descritores de textura de Haralick, incluindo pelo menos os de homogeneidade, entropia, energia e contraste, aplicados às matrizes de co-ocorrência circulares C1, C2, C4, C8 e C16 e os 7 momentos invariantes de Hu. Reamostre o número de tons de cinza para um valor menor ou igual a 32 (ideal que seja um parâmetro ajustável do sistema). Os valores calculados para a região selecionada devem ser exibidos em uma janela auxiliar. O tempo de execução deve ser medido e exibido na interface.

-> Treinar uma rede neural rasa completamente conectada com os descritores selecionados, utilizando 75% das imagens escolhidas de forma aleatória, mas balanceadas entre as classes. O tempo de execução deve ser medido e exibido na interface.

-> Classificar os 25% das imagens restantes. O tempo de execução deve ser medido e exibido na interface, juntamente com a matriz de confusão e as métricas de sensibilidade média e especificidade média. Para 4 classes com 25 imagens por classe teremos a matriz de confusão 4x4, M, onde a linha é a classe correta e a coluna a classe estimada. A sensibilidade média = acurácia = Σi=1..4 Mi,i /100 e a especificidade = 1- Σi=1..4 Σj≠i Mj,i / 300.
 
-> Classificar a região selecionada com o mouse ou a imagem carregada.
