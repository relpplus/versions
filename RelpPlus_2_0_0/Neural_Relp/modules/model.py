import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
from tensorflow import keras
from helpers import file_helper, data_process_helper, visualization_helper
from tensorflow.keras.utils import plot_model
from tensorflow.keras import backend as K

class Model:

    def __init__(self, config):
        self.config = config
        self.model = None
        self.initialize_inputs()
        self.initialize_outputs()
    

    def initialize_inputs(self):
        '''
        Inicializa todos os inputs que vão ser utilizados no modelo
        '''
        inputs_config = self.get_config('input')
        path = inputs_config.get('path')

        # word embeddings pesos já treinados
        self.word_embeddings_matrix = np.asarray(file_helper.get_json_file_data(path, inputs_config.get('word_embeddings_weight')))
        '''
        print('word_embeddings_matrix')
        print(self.word_embeddings_matrix)
        '''

        # inputs de treino
        self.train_sentences_input = np.asarray(file_helper.get_json_file_data(path, inputs_config.get('train_sentence_input')))
        self.train_entities_input = np.asarray(file_helper.get_json_file_data(path, inputs_config.get('train_entity_input')))
        self.train_pos_tagged_input = np.asarray(file_helper.get_json_file_data(path, inputs_config.get('train_pos_tagged_input')))
        '''
        print('train_sentences_input')
        print(self.train_sentences_input)
        print('train_entities_input')
        print(self.train_entities_input)
        '''

        # inputs de teste
        self.test_sentences_input = np.asarray(file_helper.get_json_file_data(path, inputs_config.get('test_sentence_input')))
        self.test_entities_input = np.asarray(file_helper.get_json_file_data(path, inputs_config.get('test_entity_input')))
        self.test_pos_tagged_input = np.asarray(file_helper.get_json_file_data(path, inputs_config.get('test_pos_tagged_input')))
        '''
        print('test_sentences_input')
        print(self.test_sentences_input)
        print('test_entities_input')
        print(self.test_entities_input)
        '''
    

    def initialize_outputs(self):
        '''
        Inicializa todos os outputs que vão ser utilizados no modelo
        '''
        outputs_config = self.get_config('output')
        path = outputs_config.get('path')

        # output de treino
        self.train_sentences_output = np.asarray(file_helper.get_json_file_data(path, outputs_config.get('train_sentence_output')))
        '''
        print('train_sentences_output')
        print(self.train_sentences_output)
        '''

        # output de teste
        self.test_sentences_output = np.asarray(file_helper.get_json_file_data(path, outputs_config.get('test_sentence_output')))
        '''
        print('test_sentences_output')
        print(self.test_sentences_output)
        '''


    def get_config(self, str_config=None):
        return self.config.get_configuration(str_config)


    def create_input_layer(self, str_name, input_length):
        '''
        Cria um layer de input para o modelo
        '''
        return tf.keras.layers.Input(shape=(input_length,), name=str_name)

    
    def create_embedding_layer(self, str_name, embedding_matrix, input_length, trainable, model):
        '''
        Cria um layer de embedding para o modelo
        '''
        weights = None if trainable else [embedding_matrix]
        output_dim = 5 if trainable else embedding_matrix.shape[1]
        return tf.keras.layers.Embedding(embedding_matrix.shape[0], output_dim, weights=weights,input_length=input_length, name=str_name)(model)
    

    def concatenate_layers(self, str_name, layers_list):
        '''
        Concatena uma lista de layers, fazendo merge deles
        '''
        return tf.keras.layers.concatenate(layers_list, name=str_name)


    def create_dense_layer(self, str_name, output_shape, str_activation, model):
        '''
        Cria um layer Dense para o modelo
        '''
        return tf.keras.layers.Dense(output_shape, activation=str_activation, name=str_name)(model)

    
    def create_flatten_layer(self, str_name, model):
        '''
        Cria um layer Flatten para o modelo
        '''
        return tf.keras.layers.Flatten(name=str_name)(model)

    
    def create_bidirectional_layer(self, str_name, lstm, model, merge_mode='concat'):
        '''
        Cria um layer Bidirectional para o modelo
        '''
        return tf.keras.layers.Bidirectional(lstm, merge_mode=merge_mode)(model)

    
    def create_lstm_layer(self, str_name, input_dim, dropout,  bidirectional, model):
        '''
        Cria um layer LSTM para o modelo
        '''
        if bidirectional:
            return tf.keras.layers.LSTM(input_dim, return_sequences=True, dropout=dropout, name=str_name)
        else:
            return tf.keras.layers.LSTM(input_dim, return_sequences=True, dropout=dropout, name=str_name)(model)
    

    def create_time_distributed(self, str_name, output_dim, str_activation, model):
        '''
        Cria um layer Time Distributed para o modelo
        '''
        return tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(output_dim, activation=str_activation), name=str_name)(model)


    def create_model(self):
        '''
        Cria o modelo que vai ser utilizado, definindo todas as suas camadas e compilação
        '''
        input_length = self.train_sentences_input.shape[1]
        embeddings_layers = []
        input_layers = []
        
        # layer de input de word embeddings
        word_embeddings_input_layer = self.create_input_layer('word_embeddings_input_layer', input_length)
        input_layers.append(word_embeddings_input_layer)
        embeddings_layers.append(self.create_embedding_layer('word_embedding_layer', self.word_embeddings_matrix, input_length, False, word_embeddings_input_layer))

        # layer de input de entidades
        entity_input_layer = self.create_input_layer('entity_input_layer', input_length)
        input_layers.append(entity_input_layer)
        embeddings_layers.append(self.create_embedding_layer('entity_embedding_layer', self.train_entities_input, input_length, True, entity_input_layer))

        # layer de input de entidades
        pos_tagged_input_layer = self.create_input_layer('pos_tagged_input_layer', input_length)
        input_layers.append(pos_tagged_input_layer)
        embeddings_layers.append(self.create_embedding_layer('pos_tagged_embedding_layer', self.train_pos_tagged_input, input_length, True, pos_tagged_input_layer))
        

        # layer para concatenar os embeddings do modelo
        model = self.concatenate_layers('concatenate_embeddings_layer', embeddings_layers)

        # layer LSTM
        lstm = self.create_lstm_layer('lstm_layer', input_length, 0.5, True, model)

        # layer BI-LSTM
        model = self.create_bidirectional_layer('bi_lstm_layer', lstm, model)

        # layer Flatten
        #model = self.create_flatten_layer('flatten_layer_1', model)

        model = self.create_dense_layer('dense_layer_2', 32, 'relu', model)
        model = tf.keras.layers.Dropout(0.5)(model)

        output = self.create_time_distributed('time_distributed_layer', 1,'sigmoid', model)

        # criação do modelo
        model = tf.keras.Model(inputs=input_layers, outputs=output)

        # otimzadores
        #opt = tf.keras.optimizers.SGD(learning_rate=0.01, momentum=0.0, nesterov=False)
        opt = tf.keras.optimizers.Adam(learning_rate=0.01, beta_1=0.9, beta_2=0.999, amsgrad=False)

        # compilação do modelo
        model.compile(loss='binary_crossentropy', optimizer=opt, metrics=['accuracy', self.custom_accuracy_function()])

        print(model.summary())

        self.model = model
        plot_model(model, to_file='model.png', show_shapes=True, show_layer_names=True)


    def train_model(self):
        '''
        Realiza o treinamento do modelo
        '''
        train_inputs = [self.train_sentences_input, self.train_entities_input, self.train_pos_tagged_input]
        train_sentences_output = self.train_sentences_output
        model = self.model
        history = model.fit(train_inputs, train_sentences_output, epochs=50, verbose=1, batch_size=10)
        visualization_helper.plot_model_history_graph(history)
        
    
    
    def evaluate_model(self):
        model = self.model
        train_inputs = [self.train_sentences_input, self.train_entities_input, self.train_pos_tagged_input]
        test_inputs = [self.test_sentences_input, self.test_entities_input, self.test_pos_tagged_input]
        train_sentences_output = self.train_sentences_output
        test_sentences_output = self.test_sentences_output
        model.evaluate(train_inputs, train_sentences_output)
        model.evaluate(test_inputs, test_sentences_output)
    

    def predict(self):
        model = self.model
        test_inputs = [self.test_sentences_input, self.test_entities_input, self.test_pos_tagged_input]
        output = []
        prediction_probas = model.predict(test_inputs)
        for pred in prediction_probas:
            output.append([1 if p >= 0.5 else 0 for p in pred])

        return output
    

    def custom_accuracy_function(self):
        '''
        Função de precisão personalizada, para verificar a precisão somente no predict de relacionamento
        '''
        class_to_ignore = 0
        def custom_accuracy(data_true, data_pred):
            y_true_class = K.argmax(data_true, axis=-1)
            y_pred_class = K.argmax(data_pred, axis=-1)
    
            ignore_mask = K.cast(K.not_equal(y_pred_class, class_to_ignore), 'int32')
            matches = K.cast(K.equal(y_true_class, y_pred_class), 'int32') * ignore_mask
            accuracy = K.sum(matches) / K.maximum(K.sum(ignore_mask), 1)
            return accuracy
        
        return custom_accuracy