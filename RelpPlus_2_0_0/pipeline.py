# -*- coding: utf-8 -*-

import os
import sys

def pre_processamento(file_name):

    print("\n(1/4) - Pré-Processamento\n\nPrimeira fase: Sentence Breaker\nSegunda  fase: Tolkienizer\n")

    #Sentence Breaker               python3 1_pre_processamento/sentence_breaker.py file
    print("(1/2) - Sentence Breaker")
    os.system("python3 1_pre_processamento/sentence_breaker.py "+str(file_name))

    #Tolkienizer                    python3 1_pre_processamento/tolkienizer.py file
    print("(2/2) - Tolkienizer")
    os.system("python3 1_pre_processamento/tolkienizer.py")

    print("\n--- Done! ---")

def ner(file):

    print("\n(2/4) - NER\n")

    #Calling Ner                    python3 calling_ner.py
    os.system("python3 2_ner/calling_ner.py")

    print("--- Done! ---")

def ne_matcher(file):

    print("\n(3/4) - NE Matcher\n")

    #NE Matcher                     python3 ne_matcher.py
    os.system("python3 3_ne_matcher/ne_matcher.py")

    print("--- Done! ---")

def relp(file):

    print("\n(4/4) - RelP")

    #Cogroo                         java -jar cogroo4py.jar
    #print("\nExecute paralelamente a ferramenta Cogroo em uma nova janela do terminal\nA ferramenta Cogroo se encontra na pasta 4_RelP\n\nPara executar esta ferramenta, utilize o comando abaixo:\njava -jar cogroo4py.jar")
    #os.system("java -jar 4_RelP/cogroo4py.jar")

    #choice = input("\n(1) - Continuar\t(2) - Sair\n\nApós executar a ferramenta, selecione uma das opções acima: ")
    choice = 1 #int(choice)

    if choice == 1:

        #Gerando features para treino   python3 features_treino.py Exemplos/texto_treino.txt
        #print("\nGerando features para treino")
        #Modelos alternativos para treino:  4_RelP/Exemplos/Treino/IberLEAF_treino.txt
        #os.system("python3 4_RelP/features_treino.py 4_RelP/Exemplos/Treino/IberLEAF_treino.txt")

        #Gerando modelo de treino       python3 crf_treino.py features_treino.txt.gz
        #print("\nGerando modelo de treino")
        #os.system("python3 4_RelP/crf_treino.py 4_RelP/features_treino.txt.gz")

        #Gerando features para teste    python3 features_teste.py Exemplos/texto_teste.txt
        print("\nGerando features para teste")
        os.system("python3 4_RelP/features_teste.py 4_RelP/Exemplos/Teste/all_sentences.txt")

        #Teste do modelo                python3 crf_teste.py features_teste.txt.gz modelo_padrao.txt.gz
        print("\nTestando modelo")
        os.system("python3 4_RelP/crf_teste.py 4_RelP/features_teste.txt.gz 4_RelP/modelo_treinado_sicredi.txt.gz")

    else:
        pass

    print("\n--- Done! ---")
    pass

def main(file_name):

    #STAGE 1
    pre_processamento(file_name)

    #STAGE 2
    ner(file_name)

    #STAGE 3
    ne_matcher(file_name)

    #STAGE 4
    relp(file_name)

if __name__ == '__main__':

    try:
        #file_adress = sys.argv[1]
        file_name = sys.argv[1]
        #print(file_adress)
        main(file_name)

    except IndexError:
        print("\nO arquivo anexado está errado\n")

    except Exception as name:
        print("\nPipeline Exception: "+str(name))    

    