from nltk import tokenize

def process_entity_data(cur_dict, key, value):
    '''
    Função para processar entidades presentes no dataset
    '''
    # Necessário verificar a qual argumento a entidade pertence
    entity = cur_dict.get('head') if key == 'argument_1' else cur_dict.get('tail')
    entity['word'] = value.lower().replace("'", '')

def process_category_data(cur_dict, key, value):
    '''
    Função para processar a categoria de entidade presente no dataset
    '''
    # Necessário verificar a qual entidade esta categoria está relacionanda
    entity = cur_dict.get('head') if key == 'argument_1_category' else cur_dict.get('tail')
    entity['category'] = value

def process_sentence_data(cur_dict, key, value):
    '''
    Função para processar a sentença presente no dataset
    '''
    # Necessário tokenizar a sentença e separar os cada token por um espaço em branco na string gerafa
    cur_dict[key] = ' '.join(tokenize.word_tokenize(value.lower().replace("'", ''), language='portuguese'))

def process_relation_data(cur_dict, key, value):
    '''
    Função para processar o relacionamento presente entre entidades no dataset
    '''
    if(value == ''):
        value = 'NA'
        cur_dict[key] = value
    else:
        cur_dict[key] = value.lower()

def process_id_data(cur_dict, key, value):
    '''
    Função para processar os campos que contém ids no dataset
    '''
    cur_dict[key] = int(value)

def get_embeddings_dimensions(data):
    return len(data), len(data[0])

def get_longest_sentence_from_dataset(data):
    '''
    Procura a maior sentença do dataset
    '''
    longest = 0
    for sentence in data:
        lenght = len(sentence)
        if lenght > longest:
            longest = lenght
    
    return longest
