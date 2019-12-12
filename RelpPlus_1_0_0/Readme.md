# Relp++


# Pré-requisitos

1) Requisitos do RELP

 	- Java Runtime Environment 8+
 	- interpretador Python 3.x
 	- Pacote py4j, scikit-learn, sklearn-crfsuite, scipy, pandas (*pip3 install py4j scikit-learn sklearn-crfsuite scipy pandas*)

2) Requisitos dos arquivos de entrada
	
	- Formato de entrada: .txt
	
	- Todos arquivos de entrada obrigatoriamente devem possuir o mesmo nome, seguido de underline e um seu respectivo ID, abaixo seguem 		  exemplos:

		- TextFile_1.txt
		- TextFile_2.txt
		- TextFile_3.txt
		- TextFile_4.txt


# Passo a passo para instalação

1) Clone este repositório.

2) Instale o NER, veja como instalar [aqui](https://github.com/jneto04/ner-pt) (na seção "Reproduce our tests for NER").

3) Após completar a instalação do NER, copie todo o conteúdo da pasta clonada e insira dentro da pasta 2_ner, dentro da pasta RelP++.


# Execução

1) Executando o CoGroo4py

	- Abra uma janela do terminal e execute o seguinte comando: java -jar cogroo4py.jar

2) Coloque seus exemplos/arquivos dentro da pasta RelP++/0_exemplos

3) Executando o Relp++

	- Abra outra janela do terminal e execute o seguinte comando: python3 pipeline.py nome_do_arquivo_sem_o_id

						 Exemplo de execução: python3 pipeline.py TextFile_
