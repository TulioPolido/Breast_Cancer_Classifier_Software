import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder
import numpy as np
import cv2
import os
import time

np.set_printoptions(precision=2)

def lerDir ():
    folder = './imagens'
    imagens = []
    labels = []
    for i in range(1,5):
        subFolder = folder + '/' + str(i)
        files = os.listdir(subFolder)
        for arquivo in files:
            img = cv2.imread(subFolder + '/' + arquivo)
            imagens.append(img)
            labels.append(i)
    return imagens, labels


inicio = time.time()

#train_feat = []
#train_labels = []

#seta o vetor de labels
#for i in range(0,400):
#    train_labels.append(int(i/100) + 1)

# Particionamento da base
X, y = lerDir()
print (X)
le = LabelEncoder()
y = le.fit_transform(y)

class_names = le.classes_

print (class_names)   # Remover linha

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=0)


mlp = MLPClassifier(solver='lbfgs', random_state=0)

mlp.fit(X_train, y_train)
y_pred = mlp.predict(X_test)


print("Camadas da rede: {}".format(mlp.n_layers_))
print("Neurônios na camada oculta: {}".format(mlp.hidden_layer_sizes))
print("Neurônios na camada de saída: {}".format(mlp.n_outputs_))
print("Pesos na camada de entrada: {}".format(mlp.coefs_[0].shape))
print("Pesos na camada oculta: {}".format(mlp.coefs_[1].shape))

print("Acurácia da base de treinamento: {:.2f}".format(mlp.score(X_train, y_train)))
print("Acurácia da base de teste: {:.2f}".format(mlp.score(X_test, y_test)))

print(classification_report(y_test, y_pred, target_names=class_names))

# Calcula a matriz de confusão
cnf_matrix = confusion_matrix(y_test, y_pred)
print(cnf_matrix)


# Calcula tempo de execução
tempo = time.time() - inicio

print("Tempo de execução: " + tempo)
