# -*- coding: utf-8 -*-

import nltk
from nltk.tokenize import sent_tokenize
import sys

def main(file_name):
    
    #print("\nComeçando pré-processamento\n")
    
    count_new_files = 0
    input_count = 1
    #input_limit = 50

    condition = True
    
    #try:
    while condition:
        try:
            #print("First while")    
            #v2_200_news/#0_news/Startup_'+str(input_count)+'.txt'
            #print(file)
            #documents = open(str(file)+'/sentence_'+str(input_count)+'.txt', encoding='utf-8').read()
            documents = open('0_exemplos/'+str(file_name)+str(input_count)+'.txt', encoding='utf-8').read()
            sentencas = sent_tokenize(documents, language='portuguese')

            qtd_sentencas = 0

            for sentenca in sentencas:
                qtd_sentencas = qtd_sentencas +1

            #print(str(qtd_sentencas))
            output_limit = qtd_sentencas
            output_count = 1

            while output_count <= output_limit:
                #print("Second while")
                output_file = open('1_pre_processamento/outputs/sentence_breaker_output/sentence_'+str(input_count)+'_'+str(output_count)+'.txt', 'w', encoding='utf-8')
                output_file.write(sentencas[output_count-1])
                
                output_count += 1
                count_new_files += 1

            input_count += 1
        
        except Exception as name:
            #print("\nMain SB Exception: "+str(name)+"\n")
            condition = False

if __name__ == "__main__":

    try:
        file_adress = sys.argv[1]
        #print(file_adress)
        main(file_adress)

    except IndexError:
        print("\nO arquivo anexado está errado\n")

    except Exception as name:
        print("\nSB Exception: "+str(name))
