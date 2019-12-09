import csv
import os 

class RelpFormat:

    def __init__(self, sentence, enty_1, id_1, tolkien_1, enty_2, id_2, tolkien_2):
        
        self.sentence = sentence
        self.enty_1 = enty_1
        self.id_1 = id_1
        self.tolkien_1 = tolkien_1
        self.enty_2 = enty_2
        self.id_2 = id_2
        self.tolkien_2 = tolkien_2
        
class manageFile:

    def __init__(self, name, mode, saida):
        self.name = name
        self.mode = mode
        self.relpformat = []
        self.saida = saida

    def print_content(self):
        f = open(self.name, self.mode)
        content = f.read()
        print(content)
        f.close()   

    def to_array(self):
        f = open(self.name, self.mode)
        content = f.read().split("\n")
        f.close()

        return content

    def analisys(self):

        array = self.to_array()
        #self.print_array(array)
        #self.count_sentences(array)
        word = []
        tolkien = []
        aux = []
        aux_index = 0
        index = 0
        
        while index <= len(array):
            
            try:
                aux_array = array.__getitem__(index).split()
                word.insert(index, aux_array[0]) 
                tolkien.insert(index, aux_array[1])

                if tolkien.__getitem__(index).__contains__("I-"):
                    
                    aux.insert(aux_index, word.__getitem__(index-1)+"_"+word.__getitem__(index)+" "+tolkien.__getitem__(index-1))

                    array.insert(index-1, aux.__getitem__(aux_index))
                    word.insert(index-1, aux.__getitem__(aux_index).split().__getitem__(0))
                    tolkien.insert(index-1, aux.__getitem__(aux_index).split().__getitem__(1))
                    
                    cont = 0
                    while cont < 2:
                        array.pop(index)
                        word.pop(index)
                        tolkien.pop(index)
                        cont += 1

                    index = index-1 
      
            except IndexError:
                break    
            index += 1
        
        return array

    def count_sentences(self, array):

        count = 0

        for i in array:

            if i == "":
                count += 1
                print(count)

            else:
                print(i)    

        #print(str(count))

        return array    

    def relp_format_builder(self, version, sub_version):
        
        #print("Relp Format Builder")

        class CheckComparison:

            def __init__(self, check_entity_1, check_entity_2):
                self.check_entity_1 = check_entity_1
                self.check_entity_2 = check_entity_2

        class Entities:
        
            def __init__(self, entity, tolkien, position):
                self.entity = entity
                self.tolkien = tolkien
                self.position = position

        array = self.analisys() #For entity manipulation
        
        sentence = self.get_sentence(array) 
        enty_1 = ""
        id_1 = 0
        tolkien_1 = ""
        enty_2 = ""
        id_2 = 0
        tolkien_2 = ""
        entities = []
        check_org = []
        already = False
        final = []
        #final.append(RelpFormat("SENTENCE", "ENTIDADE_1", "ID_1", "TOLKIEN_1", "ENTIDADE_2 ", "ID_2", "TOLKIEN_2"))

        #Get entities
        for index, enty in enumerate(array):
            if enty.__contains__("B-"):
                entities.append(Entities(enty.split().__getitem__(0),enty.split().__getitem__(1),index))
        
        index = 0
        sub_index = 0
        while index < len(entities):
            
            if entities[index].tolkien.__contains__("B-ORG"):
                sub_index = 0
                entities[index].relation_number = len(entities)-1

                while sub_index <= entities[index].relation_number:
                    
                    #Skipping TIME and VALUE stamps
                    if entities[sub_index].tolkien.__contains__("TMP") or entities[sub_index].tolkien.__contains__("VAL"):
                        pass

                    else:
                        if index != sub_index:
                            
                            #ORG Tolkien
                            enty_1 = str(entities[index].entity)
                            id_1 = entities[index].position
                            tolkien_1 = str(entities[index].tolkien).replace("B-", "")
                            if tolkien_1.__contains__("LOC"):
                                tolkien_1 = tolkien_1.replace("LOC", "PLC")

                            #Any Tolkien
                            enty_2 = str(entities[sub_index].entity)
                            id_2 = entities[sub_index].position
                            tolkien_2 = str(entities[sub_index].tolkien).replace("B-", "")   
                            if tolkien_2.__contains__("LOC"):
                                tolkien_2 = tolkien_2.replace("LOC", "PLC")
                            
                            if tolkien_1.__contains__("ORG") and tolkien_2.__contains__("ORG"):
                                #print("\nENTROU\n")
                                try:
                                    for i in check_org:
                                        if (i.check_entity_1 == enty_1 and i.check_entity_2 == enty_2) or (i.check_entity_1 == enty_2 and i.check_entity_2 == enty_1):    
                                            already = True
                                except:
                                    pass             
                                
                                if already:
                                    pass
                                
                                else:
                                    final.append(RelpFormat(sentence, enty_1, id_1, tolkien_1, enty_2, id_2, tolkien_2))        

                                check_org.append(CheckComparison(enty_1, enty_2))
                                already = False
                            
                            else:
                                final.append(RelpFormat(sentence, enty_1, id_1, tolkien_1, enty_2, id_2, tolkien_2))
                            
                    sub_index += 1    

            index += 1

        #index = 0
        #while index < len(entities):
        
        """
        for i in final:
            print("============== RELP FORMAT =============="+
                "\n\nSentence: "+str(i.sentence)+
                "\n\nId 1: "+str(i.id_1)+
                "\nEntidade 1: "+str(i.enty_1)+
                "\nTolkien 1: "+str(i.tolkien_1)+
                "\n\nId 2: "+str(i.id_2)+
                "\nEntidade 2: "+str(i.enty_2)+
                "\nTolkien 2: "+str(i.tolkien_2)+
                  "\n\n============ RELP FORMAT EXIT ============\n")          
        """

        self.to_tsv(final, version, sub_version)

    def to_tsv(self, final, version, sub_version):
        #print("To tsv")
        #PLN Adress:
        #Home Adress: "C:/Users/gui99/Desktop/Pucrs/PLN/2019_2/Script/Script/teste_csv.csv" 
        #10_news_training_test/case_"+str(number)+".txt
        with open(self.saida+str(version)+"_"+str(sub_version)+".txt", mode="wt") as myfile:
            
            wr = csv.writer(myfile, delimiter="\t", lineterminator="\n")
            for i in final:
                wr.writerow([i.sentence, i.id_1, i.enty_1, i.tolkien_1, i.id_2, i.enty_2, i.tolkien_2])
            
    #Utility functions
    def print_array(self, array):
        
        for i in array:
            
            if i == "":
                print("1")
            
            elif i == " ":
                print("2")
            
            elif i == "\n":
                print("3")        
            
            else:
                print(i)

        print("Size: "+str(len(array))+"\n")        

    def get_sentence(self, array):

        sentence = ""

        for i in array:
            try:
                if sentence == "":
                    sentence += i.split().__getitem__(0)
                else:
                    sentence += " "+i.split().__getitem__(0)    
            except:
                pass

        return sentence
    

if __name__ == "__main__":

    """
    number = 1
    tam = 1

    while number <= tam:
        #teste = manageFile("sentences_patricia/output_ner_"+str(number)+".txt", "r")
        teste = manageFile("output_test.txt","r")
        teste.relp_format_builder(number, number)
        print("Finishing test number: "+str(number))
        number += 1
    """

    version = 1
    sub_version = 1
    
    version_tam = True
    sub_version_tam = True
    memory = 0

    cat_command = "cat "
 
    while version_tam:
        try:
            while sub_version_tam:        
                try:
                    adress = "2_ner/output_ner/sentence_"
                    saida = "3_ne_matcher/output_ne_matcher/sentence_" 

                    test = manageFile(adress+str(version)+"_"+str(sub_version)+".txt","r", saida)
                    test.relp_format_builder(version, sub_version)
                    
                    #print(adress+str(version)+"_"+str(sub_version)+".txt")
                    
                    cat_command += "3_ne_matcher/output_ne_matcher/sentence_"+str(version)+"_"+str(sub_version)+".txt " 
                    
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

    cat_command += "> 4_RelP/Exemplos/Teste/all_sentences.txt"

    #with open("all_sentences.txt", "w") as cat:
    #    cat.write(cat_command)
    
    #print(cat_command)
    os.system(cat_command)


                