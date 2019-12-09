import csv
import nltk
import spacy
from helpers import file_helper, validator_helper, data_process_helper, dictionary_creator_helper

class Parser:

    relation_id = 0
    word_id = 1
    entity_type_id = 0
    pos_tag_id = 1
    padding_size = 100

    def __init__(self, config):
        self.config = config
        self.dataset_types = ['train', 'test']

    
    def get_config(self, str_config_type=None):
        return self.config.get_configuration(str_config_type)


    def increment_relation_id(self, inc=1):
        '''
        Função para incrementar o relation_id
        '''
        self.relation_id += inc


    def increment_word_id(self, inc=1):
        '''
        Função para incrementar o word_id
        '''
        self.word_id += inc


    def increment_entity_type_id(self, inc=1):
        self.entity_type_id += inc
    

    def increment_pos_tag_id(self, inc=1):
        self.pos_tag_id +=1

    
    def run_initial_parse(self):
        '''
        Função chamada ao iniciar o programa,
        realiza o parse dos arquivos conforme as configurações
        '''
        # chamada para conversão de arquivos originais(txt, tsv) para json
        self.convert_src_to_json_files()

        # chamada para criação de dicionários: word_to_id e reverse_dict
        self.create_word_dicts()

        # chamada para formatação de inputs que serão utilizados pelo modelo
        self.parse_inputs_for_model()

        # chamada para criar o vetor de output que será utilizado no treino do modelo
        self.create_output_for_model()


    def create_pos_tag_input(self):
        '''
        Cria o input contendo as informações de part-of-speech dos dataset,
        além de ir criando juntamente o dicionario de tags 
        '''
        dataset_config = self.get_config('dataset')
        dataset_path = dataset_config.get('path')
        pos_config = self.get_config('part_of_speech')
        pos_path = pos_config.get('path')
        input_config = self.get_config('input')
        input_path = input_config.get('path')
        pos_tag_dict = { 'PAD' : 0 }
        nlp = spacy.load('pt')
        for dataset_type in self.dataset_types:
            input_list = []
            dataset_file_name = 'train_json' if dataset_type == 'train' else 'test_json'
            input_file_name = 'train_pos_tagged_input' if dataset_type == 'train' else 'test_pos_tagged_input'
            dataset = file_helper.get_json_file_data(dataset_path, dataset_config.get(dataset_file_name))
            for data in dataset:
                sentence = data.get('sentence')
                tagged_sentence = [token.pos_ for token in nlp(sentence)]
                for tag in tagged_sentence:
                    self.add_tag_in_pos_tag_dict(pos_tag_dict, tag)
                
                input_data = self.include_padding([pos_tag_dict[tag] for tag in tagged_sentence])
                input_list.append(input_data)
                file_helper.dict_to_json(input_path, input_config.get(input_file_name), input_list, 4)
        
        file_helper.dict_to_json(pos_path, pos_config.get('pos_tag_dict'), pos_tag_dict, 4)


    def add_tag_in_pos_tag_dict(self, pos_tag_dict, pos_tag):
        '''
        Adiciona tag no dicionario de tags
        '''
        if pos_tag_dict.get(pos_tag) is None:
            pos_tag_dict[pos_tag] = self.pos_tag_id
            self.increment_pos_tag_id()

    
    def create_word_embeddings_weight(self):
        '''
        Função para criar o arquivo com vetor de pesos do word embeddings que será utilizado no modelo
        '''
        word_embeddings_config = self.get_config('word_embeddings')
        word_embeddings = file_helper.get_json_file_data(word_embeddings_config.get('path'), word_embeddings_config.get('word_embeddings_json'))
        word_embeddings_dimension = word_embeddings_config.get('dimensions')
        word_to_id_config = self.get_config('word_to_id')
        word_to_id = file_helper.get_json_file_data(word_to_id_config.get('path'), word_to_id_config.get('dict'))
        word_embeddings_weight = self.create_empty_word_embeddings_weight_list(len(word_to_id) + 1, word_embeddings_dimension) 
        for word, index in word_to_id.items():
            weight_in_embeddings = word_embeddings.get(word)
            if weight_in_embeddings is not None:
                word_embeddings_weight[index] = weight_in_embeddings
        
        input_config = self.get_config('input')
        file_helper.dict_to_json(input_config.get('path'), input_config.get('word_embeddings_weight'), word_embeddings_weight, 4)


    def create_empty_word_embeddings_weight_list(self, vocab_size, embeddings_dimension):
        embeddings_weight = []
        for _ in range(vocab_size):
            embeddings_weight.append([0] * int(embeddings_dimension))
        
        return embeddings_weight


    def create_output_for_model(self):
        '''
        Cria o arquivo de output do modelo
        '''
        output_config = self.get_config('output')
        dataset_config = self.get_config('dataset')
        for dataset_type in self.dataset_types:
            dataset_filename = 'train_json' if dataset_type == 'train' else 'test_json'
            output_filename = 'train_sentence_output' if dataset_type == 'train' else 'test_sentence_output'
            dataset = file_helper.get_json_file_data(dataset_config.get('path'), dataset_config.get(dataset_filename))
            sentences_output = self.parse_output_sentence(dataset)
            file_helper.dict_to_json(output_config.get('path'), output_config.get(output_filename), sentences_output, 4)


    def parse_output_sentence(self, dataset):
        '''
        Faz o parse do output das sentenças, onde é utilizado um vetor binário com  a seguinte representação:
            0 -> palavra normal (não faz parte do relacionamento)
            1 -> palavra do relacionamento
        '''
        sentences_output = []
        for data in dataset:
            cur_sentence = [0] * self.padding_size
            sentence = data.get('sentence')
            head = data.get('head').get('word')
            tail = data.get('tail').get('word')
            relation = data.get('relation')
            begin, end = self.extract_relation_from_sentence(sentence, head, tail, relation)
            fn_lambda = lambda index: 0 if index < begin or index >= end else 1
            cur_sentence = [fn_lambda(index) for index, _ in enumerate(cur_sentence)]
            sentences_output.append(cur_sentence)
        
        return sentences_output
    

    def extract_relation_from_sentence(self, sentence, head, tail, relation):
        '''
        Extrai o trecho da sentença que contem o relacionamento, retornando os seguintes valores:
            * begin -> inicio do relacionamento
            * begin + relation_len -> onde acaba o relacionamento, visto que é o inicio mais o tamanho do relacionamento
        '''
        split_sentence = sentence.split(' ')
        split_relation = relation.split(' ')
        begin, end = self.get_relation_boundaries(split_sentence, head, tail)
        relation_len = len(split_relation)
        found = False
        while found is not True and begin < end:
            found = split_sentence[begin:begin+relation_len] == split_relation
            if found is not True:
                begin += 1
        
        return begin, begin+relation_len

            
        
    
    def get_relation_boundaries(self, split_sentence, head, tail):
        '''
        Pega os indexes de onde as entidades se encontram,
        criando o espaço onde o relacionamento deve ser procurado
        '''
        head_index_list = []
        tail_index_list = []
        for index, word in enumerate(split_sentence):
            if word == head:
                head_index_list.append(index)
            
            if word == tail:
                tail_index_list.append(index)
        # por simplicidade será utilizado:
        #   * index_min para begin
        #   * index_max para end
        # porque desta forma o relacionamento vai ser capturado
        return min(head_index_list), max(tail_index_list)


    def include_padding(self, sentence, padding=padding_size):
        '''
        Adiciona a representação de paddings na sentença -> word_to_id = 0
        '''
        while len(sentence) < padding:
            sentence.append(0)
        
        return sentence
    

    def parse_inputs_for_model(self):
        '''
        Função para parsear o input de palavras para numeros, tornando melhor para alimentar o modelo
        '''
        word_to_id_config = self.get_config('word_to_id')
        word_to_id_path = word_to_id_config.get('path')
        word_to_id_file_name = word_to_id_config.get('dict')
        word_to_id = file_helper.get_json_file_data(word_to_id_path, word_to_id_file_name)

        self.create_sentence_input(word_to_id)
        self.create_entity_input()
        self.create_pos_tag_input()
        self.create_word_embeddings_weight()
        
    
    def create_sentence_input(self, word_to_id):
        '''
        Cria o arquivo de sentence_input, que será utilizado como input no modelo
        '''
        dataset_config = self.get_config('dataset')
        input_config = self.get_config('input')
        dataset_path = dataset_config.get('path')
        input_path = input_config.get('path')
        for dataset_type in self.dataset_types:
            dataset_type_filename = 'train_json' if dataset_type == 'train' else 'test_json'
            input_type_filename = 'train_sentence_input' if dataset_type == 'train' else 'test_sentence_input'
            dataset = file_helper.get_json_file_data(dataset_path, dataset_config.get(dataset_type_filename))
            sentence_input = self.parse_sentence_input(dataset, word_to_id)
            file_helper.dict_to_json(input_path, input_config.get(input_type_filename), sentence_input, 4)

    
    def parse_sentence_input(self, dataset, word_id):
        '''
        Faz a tradução das palavras para id's que são usados no sentence_input
        '''
        sentences_input = []
        for data in dataset:
            sentence = data.get('sentence')
            sentence_input = [word_id.get(word) for word in sentence.split(' ')]
            self.include_padding(sentence_input)
            sentences_input.append(sentence_input)
        return sentences_input


    def create_entity_input(self):
        '''
        Cria o arquivo de entity_input, que será utilizado como input no modelo
        '''
        dataset_config = self.get_config('dataset')
        input_config = self.get_config('input')
        dataset_path = dataset_config.get('path')
        input_path = input_config.get('path')
        for dataset_type in self.dataset_types:
            dataset_type_filename = 'train_json' if dataset_type == 'train' else 'test_json'
            input_type_filename = 'train_entity_input' if dataset_type == 'train' else 'test_entity_input'
            dataset = file_helper.get_json_file_data(dataset_path, dataset_config.get(dataset_type_filename))
            entity_input = self.parse_entity_input(dataset)
            file_helper.dict_to_json(input_path, input_config.get(input_type_filename), entity_input, 4)
        

    def parse_entity_input(self, dataset):
        '''
        Faz a tradução das entidades e palavras normais para vetor binario, onde:
        0 -> palavra normal
        1 -> entidade marcada na sentença
        '''
        entities_input = []
        for data in dataset:
            sentence = data.get('sentence')
            head = data.get('head').get('word')
            tail = data.get('tail').get('word')
            fn_lambda = lambda head, tail, word: 1 if word == tail or word == head else 0
            entity_input = [fn_lambda(head, tail, word) for word in sentence.split(' ')]
            self.include_padding(entity_input)
            entities_input.append(entity_input)
        return entities_input


    def create_word_dicts(self):
        '''
        Função que cria os dicionários de palavras(word_to_id, reverse_dict) presentes nos dados de entrada
        '''
        word_to_id_config = self.get_config('word_to_id')
        path = word_to_id_config.get('path')
        word_to_id_file_name = word_to_id_config.get('dict')
        reverse_dict_file_name = word_to_id_config.get('reverse_dict')
        word_to_id_dict = {}
        reverse_dict = {}
        self.process_all_dataset_to_word_to_id(word_to_id_dict, reverse_dict)
        file_helper.dict_to_json(path, word_to_id_file_name, word_to_id_dict, 4)
        file_helper.dict_to_json(path, reverse_dict_file_name, reverse_dict, 4)
        
    
    def convert_src_to_json_files(self):
        '''
        Função que realiza a conversão dos arquivos de entrada para json
        '''
        # transforma o arquivo txt de word embeddings em um json
        self.word_embeddings_to_json()

        # transforma os arquivos de dataset json
        for dataset_type in self.dataset_types:
            self.dataset_to_json(dataset_type)

        # cria um arquivo json com os relacionamentos presentes no dataset de treino
        self.relation_to_id_json()

        # cria im arquivo json com todos os tipos de entidades presente
        self.entities_types_to_id()


    def entities_types_to_id(self):
        '''
        Cria os dicionários para os tipos de entidades presentes no dataset de treino
        '''
        entities_type_dict = {}
        reverse_entities_type_dict = {}
        dataset_config = self.get_config('dataset')
        entities_config = self.get_config('entities')
        path = entities_config.get('path')
        train_dataset = file_helper.get_json_file_data(dataset_config.get('path'), dataset_config.get('train_json'))

        for sentence in train_dataset:
            for str_type in ['head', 'tail']:
                self.add_data_to_entities_dict(str_type, sentence, entities_type_dict, reverse_entities_type_dict)
        
        file_helper.dict_to_json(path, entities_config.get('entities_to_id'), entities_type_dict, 4)
        file_helper.dict_to_json(path, entities_config.get('reverse_entities_to_id'), reverse_entities_type_dict, 4)


    def add_data_to_entities_dict(self, str_entity, sentence, entity_to_id_dict, reverse_dict):
        '''
        Adiciona os dados nos dicionarios de entidades
        '''
        entity = sentence.get(str_entity).get('category')
        if entity_to_id_dict.get(entity) is None:
            entity_to_id_dict[entity] = self.entity_type_id
            reverse_dict[self.entity_type_id] = entity
            self.increment_entity_type_id()
        

    def dataset_to_json(self, dataset_type):
        '''
        Função para transformar os inputs do dataset em json
        '''
        # vai guardar o index de cada uma das chaves presentes no cabeçalho do arquivo
        dataset_config = self.get_config('dataset')
        keys_dict = {}
        dataset_list = []
        path = dataset_config.get('path')
        str_file_name = 'train_tsv' if dataset_type == 'train' else 'test_tsv'
        str_json_file_name = 'train_json' if dataset_type == 'train' else 'test_json'
        file_name = dataset_config.get(str_file_name)
        json_file_name = dataset_config.get(str_json_file_name)
        
        with open(f"{path}{file_name}") as fp:
            # faz a leitura do arquivo, utilizando a tabulação como separeador
            reader = csv.reader(fp, delimiter="\t")
            # a primeira linha contém as chaves de cada um dos campos
            keys = reader.__next__()

            # preenche o dicionario de chaves com o indice
            for index, value in enumerate(keys, start=0):
                keys_dict[index] = value.lower()
            
            # para as outras linhas do arquivo vai adicionando cada campo em seu respectivo lugar
            for line in reader:
                cur_dict = dictionary_creator_helper.create_dataset_dict()
                for index, value in enumerate(line):
                    self.process_dataset_data(cur_dict, keys_dict.get(index), value)

                dataset_list.append(cur_dict)
                    
        file_helper.dict_to_json(path, json_file_name, dataset_list, 4)


    def process_dataset_data(self, cur_dict, key, value):
        '''
        Função para processar os dados do dataset de acordo com os campos
        '''
        if validator_helper.is_id_data(key):
            data_process_helper.process_id_data(cur_dict, key, value)
        elif validator_helper.is_entity(key):
            data_process_helper.process_entity_data(cur_dict, key, value)
        elif validator_helper.is_category(key):
            data_process_helper.process_category_data(cur_dict, key, value)
        elif validator_helper.is_sentence(key):
            data_process_helper.process_sentence_data(cur_dict, key, value)
        elif validator_helper.is_relation(key):
            data_process_helper.process_relation_data(cur_dict, key, value)


    def word_embeddings_to_json(self):
        '''
        Função para transformar o arquivo de word_embeddings em json
        '''
        word_embeddings_config = self.get_config('word_embeddings')
        # lista de dicionarios com dados processados de word embeddings
        word_embeddings_dict = {}
        path = word_embeddings_config.get('path')
        # seta o arquivo que vai ser utilizado de word embeddings
        src_word_embedings = 'real_src' if word_embeddings_config.get('real') else 'example_src'
        file_name = word_embeddings_config.get(src_word_embedings)
  
        with open(f"{path}{file_name}") as fp:
            # primeira linha do arquivo contém o número de linhas e a dimensionalidade do vetor
            lines, vector_size = fp.readline().strip().split(' ')
            word_embeddings_config['vocab_size'] = lines
            word_embeddings_config['dimensions'] = vector_size
            # itera por todas linhas que contém dados do word embeddings
            for _ in range(int(lines)):
                # separa os dados presentes em cada linha, e realiza o pop para separar a word do vetor
                data_list = fp.readline().strip().split(' ')
                word = data_list[0]
                # transforma os dados do vetor em float
                word_embeddings_dict[word] = [float(x) for x in data_list[1:]]
        
        json_file_name = word_embeddings_config.get('word_embeddings_json')
        file_helper.dict_to_json(path, json_file_name, word_embeddings_dict, 4)


    def relation_to_id_json(self):
        '''
        Função para atribuir um id para cada uma das relações encontradas no dataset de treino
        '''
        dataset_config = self.get_config('dataset')
        treino_json = file_helper.get_json_file_data(dataset_config.get('path'), dataset_config.get('train_json'))
        relation_config = self.get_config('relation')
        relation_dict = {}
        # primeira relação deve ser NA e o id 0
        relation_dict['NA'] = self.relation_id
        for line in treino_json:
            relation = line.get('relation')
            if relation_dict.get(relation) is None:
                self.increment_relation_id()
                relation_dict[relation] = self.relation_id
        
        file_helper.dict_to_json(relation_config.get('path'), relation_config.get('file_name'), relation_dict, 4)


    def add_word_to_id(self, word, word_to_id_dict, reverse_dict):
        '''
        Função para adicionar um id para uma palavra
        '''
        if word_to_id_dict.get(word) is None:
            word_to_id_dict[word] = self.word_id
            reverse_dict[self.word_id] = word
            self.increment_word_id()
    

    def process_all_dataset_to_word_to_id(self, word_to_id_dict, reverse_dict):
        '''
        Função para iniciar o processamento de todos os datasets (treino, teste)
        para word_to_id
        '''
        dataset_config = self.get_config('dataset')
        path = dataset_config.get('path')
        files_names = []
        files_names.append(dataset_config.get('train_json'))
        files_names.append(dataset_config.get('test_json'))

        for file_name in files_names:
            self.process_individual_dataset_to_word_to_id(path, file_name, word_to_id_dict, reverse_dict)

    
    def process_individual_dataset_to_word_to_id(self, path, file_name, word_to_id_dict, reverse_dict):
        '''
        Função para processar individualmente cada um dos datasets em word_to_id e reverse_dict
        '''
        dict_data = file_helper.get_json_file_data(path, file_name)
        self.add_dataset_to_word_to_id(dict_data, word_to_id_dict, reverse_dict)
        file_helper.dict_to_json(path, file_name, dict_data, 4)
    

    def add_dataset_to_word_to_id(self, dataset, word_to_id_dict, reverse_dict):
        '''
        Função para transformar todas palavras das frases presentes 
        no dataset em word_to_id
        '''
        for line in dataset:
            sentence = line.get('sentence')
            for word in sentence.split(' '):
                self.add_word_to_id(word, word_to_id_dict, reverse_dict)
            
            self.set_word_id_to_entity_in_dataset(line, word_to_id_dict)
    

    def set_word_id_to_entity_in_dataset(self, dataset_line, word_to_id_dict):
        head = dataset_line.get('head')
        tail = dataset_line.get('tail')
        head['id'] = word_to_id_dict.get(head.get('word'))
        tail['id'] = word_to_id_dict.get(tail.get('word'))


    def save_predicted_output(self, dataset, predicted):
        '''
        Função para salvar de forma legivel o predict do modelo,
        para evitar uma nova leitura do arquivo, os dados gravados são retornados pela função
        '''
        output_data = []
        output_files_config = self.get_config('output_files')
        output_path = output_files_config.get('path')
        for index, data in enumerate(dataset):
            pred = predicted[index]
            sentence = data.get('sentence')
            data['predicted_relation'] = self.parse_prediction_to_words(sentence, pred)
            output_data.append(data)

        file_helper.dict_to_json(output_path, output_files_config.get('predicted_output_json'), output_data, 4)
        return output_data


    def parse_prediction_to_words(self, sentence, prediction):
        cur_sentence = []
        split_sentence = sentence.split(' ')
        for index, word in enumerate(split_sentence):
            if prediction[index] == 1:
                cur_sentence.append(word)
        
        return " ".join(cur_sentence)


    def save_number_of_entities_in_dataset(self):
        dataset_config = self.get_config('dataset')
        path = dataset_config.get('path')
        for dataset_type in self.dataset_types:
            dataset_file = 'train_json' if dataset_type == 'train' else 'test_json'
            entities_number_file = 'train_entities_number' if dataset_type == 'train' else 'test_entities_number'
            dataset = file_helper.get_json_file_data(path, dataset_config.get(dataset_file))
            local_dict = {}
            for data in dataset:
                for position in ['head', 'tail']:
                    entity = data.get(position).get('category')
                    if local_dict.get(entity) is None:
                        local_dict[entity] = 1
                    else:
                        local_dict[entity] += 1

            local_str = self.sort_data_to_txt(local_dict)
            file_helper.save_txt_file(path, dataset_config.get(entities_number_file), local_str)


    def save_entities_relation(self):
        dataset_config = self.get_config('dataset')
        path = dataset_config.get('path')
        for dataset_type in self.dataset_types:
            dataset_file = 'train_json' if dataset_type == 'train' else 'test_json'
            entities_relation_file = 'train_entities_relation' if dataset_type == 'train' else 'test_entities_relation'
            dataset = file_helper.get_json_file_data(path, dataset_config.get(dataset_file))
            local_dict = {}
            for data in dataset:
                head = data.get('head').get('category')
                tail = data.get('tail').get('category')
                relation = f'{head}-{tail}'
                if local_dict.get(relation) is None:
                    local_dict[relation] = 1
                else:
                    local_dict[relation] += 1
            local_str = self.sort_data_to_txt(local_dict)  
            file_helper.save_txt_file(path, dataset_config.get(entities_relation_file), local_str)


    def save_full_relation_in_sentence(self):
        dataset_config = self.get_config('dataset')
        path = dataset_config.get('path')
        for dataset_type in self.dataset_types:
            dataset_file = 'train_json' if dataset_type == 'train' else 'test_json'
            full_relation_file = 'train_full_relation' if dataset_type == 'train' else 'test_full_relation'
            dataset = file_helper.get_json_file_data(path, dataset_config.get(dataset_file))
            local_dict = {}
            for data in dataset:
                relation = data.get('relation')
                if local_dict.get(relation) is None:
                    local_dict[relation] = 1
                else:
                    local_dict[relation] += 1
            local_str = self.sort_data_to_txt(local_dict)
            file_helper.save_txt_file(path, dataset_config.get(full_relation_file), local_str)


    def save_words_in_relation(self):
        dataset_config = self.get_config('dataset')
        path = dataset_config.get('path')
        for dataset_type in self.dataset_types:
            dataset_file = 'train_json' if dataset_type == 'train' else 'test_json'
            words_in_relation_file = 'train_words_in_relation' if dataset_type == 'train' else 'test_words_in_relation'
            dataset = file_helper.get_json_file_data(path, dataset_config.get(dataset_file))
            local_dict = {}
            for data in dataset:
                for word in data.get('relation').split(' '):
                    if local_dict.get(word) is None:
                        local_dict[word] = 1
                    else:
                        local_dict[word] += 1
            local_str = self.sort_data_to_txt(local_dict)
            file_helper.save_txt_file(path, dataset_config.get(words_in_relation_file), local_str)

        
    def sort_data_to_txt(self, dict_data):
        acc = 0
        local_str = ''
        sorted_data = sorted(dict_data, key=dict_data.__getitem__, reverse=True)
        for data in sorted_data:
            value = dict_data.get(data)
            local_str += f'{data} : {value} \n'
            acc += value

        local_str += f'Total: {acc}\n'
        return local_str

