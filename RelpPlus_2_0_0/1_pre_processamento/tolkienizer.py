# -*- coding: utf-8 -*-

import re as regex
import os
import sys 
import subprocess

class Script:

    def __init__(self, fileName, mode):
        
        self.f = open(fileName, mode, encoding='utf-8')

    def separate(self,saida):

        f = self.f.readlines()

        #print(f)
        
        array = []
        #print(len(f))
        for line in f:
            #print(line)
            #line = self.removeNonAscii(line)
            array.append(line.split())
        
        resultArray = []
        
        for sentence in array:
            for index, line in enumerate(sentence):
                word = str(line)
                #print(word)
                resultArray.append(word)
            #resultArray.append("barran")    
        
        
        #for i in resultArray:
        #    print(i)
        
        for index, word in enumerate(resultArray):
            
            #print(word)
                
            if (len(word) > 1) and (word.__contains__('"') or word.__contains__(",") or word.__contains__(".") or word.__contains__("!") or word.__contains__("?") or word.__contains__(":") or word.__contains__("(") or word.__contains__(")")):
                
                #print("Entrou")
                pos = int(len(word))
                #print("Word: "+resultArray[index]+"\nPosition: "+str(pos)+"\nWord + Position: "+word[pos-1])
                #print("Index: "+str(index)+"\n")
                aux = str(word[pos-1])
                #print("***\nAnswer: "+resultArray[index].replace(aux, "")+"\n***\n")
                resultArray.insert(index, resultArray[index].replace(aux, ""))
                resultArray.remove(str(word))
                resultArray.insert(index+1, aux)
        
        #for i in resultArray:
        #    print(i)
        
        n = open(saida, "w")

        for index, line in enumerate(resultArray):
            #print(line)
            n.writelines(line+"\n")
        
        n.write("\n")    

if __name__ == "__main__":
    
    version = 1
    sub_version = 1
    
    version_tam = True
    sub_version_tam = True
    memory = 0

    """

    #Para arquivos com somente uma sentença

    while version_tam:

        try:
            test = Script("Exemplos/v3_200_news/#0_news/Startup_"+str(sub_version)+".txt", "r")
            test.separate("Exemplos/v3_200_news/#1_pos_tolkienizer/Startup_"+str(sub_version)+".txt")

            sub_version += 1

        except Exception as name:
            print(name)
            version_tam = False

    """
    
    # Para arquivos com mais de uma sentença 

    while version_tam:
        #print("First While")
        try:
            while sub_version_tam:        
                #print("Second While")
                try:
                    
                    test = Script("1_pre_processamento/outputs/sentence_breaker_output/sentence_"+str(version)+"_"+str(sub_version)+".txt", "r")
                    test.separate("1_pre_processamento/outputs/tolkienizer_output/sentence_"+str(version)+"_"+str(sub_version)+".txt")

                    #print("Exemplos/408_news/amostra_50/pos_tolkienizer/parceria_"+str(version)+"_"+str(sub_version)+".txt")
                    
                    #file += '2_script/200_news/200_news_pos_script/startup_'+str(version)+'_'+str(sub_version)+'.txt '
                    sub_version += 1
                    memory = 0
                         
                except:
                    memory += 1
                    break
    
            sub_version = 1            
            version += 1

            if memory > 1:
                #print("\nDone!\n")
                version_tam = False
            
            elif memory == 1:
                pass
            
            else:    
                memory = 0

        except:
            break        
    
    """
    choice = int(input("(1) - Passar pelo NER\n(2) - Sair\n\nEscolha: "))
    
    version_tam = True
    sub_version_tam = True
    version = 1
    sub_version = 1
    memory = 0

    

    # Para arquivos com somente uma sentença

    if choice == 1:
        while version_tam:
            catch = terminal.system("python3.6 tagging_ner.py Exemplos/v3_200_news/#1_pos_tolkienizer/Startup_"+str(version)+".txt Exemplos/v3_200_news/#2_pos_ner/Startup_"+str(version)+".txt conll")

            if catch == 0:
                version += 1

            else:
                break
    else:
        pass
    

    

    # Para arquivos com mais de uma sentença

    if choice == 1:
        while version_tam:
            #print("First While")
            try:
                while sub_version_tam:
                    
                    #print("Pos Script File Adress: Exemplos/Extra_news/2_pos_tolkienizer/news_"+str(version)+"_"+str(sub_version)+".txt\n"+ 
                    #      "Pos NER File Adress:    Exemplos/Extra_news/3_pos_ner/news_"+str(version)+"_"+str(sub_version)+".txt")
                    catch = terminal.system("python3.6 tagging_ner.py Exemplos/408_news/amostra_50/pos_tolkienizer/parceria_"+str(version)+"_"+str(sub_version)+".txt Exemplos/408_news/amostra_50/pos_ner/parceria_"+str(version)+"_"+str(sub_version)+".txt conll")
                    
                    if catch == 0:  
                        sub_version += 1
                        memory = 0
                        #print(str(catch))
                    
                    else:    
                        memory += 1
                        break        
                
                sub_version = 1
                version += 1

                if memory > 1:
                    print("\nDone!\n")
                    version_tam = False
            
                elif memory == 1:
                    pass
            
                else:    
                    memory = 0   
            
            except:
                print("\nFinishing NER...\n")
                break
    else:
        print("\nFinishing...\n")

    #print(file)    
    """