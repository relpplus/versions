def is_entity(key):
    '''
    Função para verificar se a chave é uma entidade
    '''
    return key == 'argument_1' or key == 'argument_2'

def is_category(key):
    '''
    Função para verificar se a chave é uma categoria
    '''
    return key == 'argument_1_category' or key == 'argument_2_category'

def is_sentence(key):
    '''
    Função para verificar se a chave é uma sentença
    '''
    return key == 'sentence'

def is_relation(key):
    '''
    Função para verificar se a chave é uma relação
    '''
    return key == 'relation'

def is_id_data(key):
    '''
    Função para verificar se a chave é um id
    '''
    return key == 'sentence_id' or key == 'relation_id'