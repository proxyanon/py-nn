#-*-coding: utf8-*-

''' 
	
	@author Daniel Victor Frerie Feitosa
	@version 3.0.1
	@editor Sublime Text 3
	
	@copyrights by Daniel Victor Frerie Feitosa - 2018
	@license GPL 3.0
	
	coded with promethazine and coffee ...
'''

from numpy import dot, array, random, exp, savetxt, tanh
from os import path, makedirs, remove, walk, _exit as exit

''' funcoes de ativacao dos neuronios '''
def _activation(x, act='sigmoid'):
	if act == 'sigmoid':
		return 1 / (1 + exp(-x))
	elif act == 'tanh':
		return tanh(x)

''' funcoes de derivadas dos neuronios '''
def _derivate(x, act='sigmoid'):
	if act == 'sigmoid':
		return x * (1 - x)
	elif act == 'tanh':
		return 1 - x**2

''' foward unico para a execucao da rede '''
def single_foward(entradas, pesos, act='sigmoid'):
	layers = []
	for x in xrange(len(pesos)):
		if x == 0:
			l = _activation(x=dot(entradas, pesos[x]), act=act)
			layers.append(l)
		else:
			l = _activation(x=dot(layers[x-1], pesos[x]), act=act)
			layers.append(l)
	return layers

''' Rede neural by @DanielFreire00 '''
class PyNNq:

	def __init__(self, n_camadas, n_entradas, n_hidden, n_saida, activation='sigmoid'):

		self.n_camadas = n_camadas
		self.n_entradas = n_entradas
		self.n_hidden = n_hidden
		self.n_saida = n_saida
		self.activation = activation

		random.seed(1)

		self.pesos = []
		self.pesos.append(2*random.random((self.n_entradas, self.n_hidden))-1)
		
		for x in xrange(n_camadas):
			self.pesos.append(2*random.random((self.n_hidden, self.n_hidden))-1)
		
		self.pesos.append(2*random.random((self.n_hidden, self.n_saida))-1)
		self.n_pesos = len(self.pesos)

		if path.exists('weights/') == False:
			makedirs('weights')

	''' Foward => Ziw = (i1 * w1) + (i2 * w2) ... '''
	def feedfoward(self, entradas):

		layers = []
		for x in xrange(self.n_pesos):
			if x == 0:
				l = _activation(x=dot(entradas, self.pesos[x]), act=self.activation)
				layers.append(l)
			else:
				l = _activation(x=dot(layers[x-1], self.pesos[x]), act=self.activation)
				layers.append(l)

		return layers

	''' Backprop => pesos += layer * (error * deriv(layer)) '''
	def backpropagation(self, entradas, saidas, eta=1):

		layers = self.feedfoward(entradas)
		deltas = []

		for x in xrange(self.n_pesos):
			if x == 0:
				e = saidas - layers[len(layers)-1]
				d = e * _derivate(x=layers[self.n_pesos-1], act=self.activation)
				deltas.append(d)
			else:
				e = deltas[x-1].dot(self.pesos[self.n_pesos-x].T)
				d = e * _derivate(x=layers[(self.n_pesos-x)-1], act=self.activation)
				deltas.append(d)

		for x in xrange(self.n_pesos):
			if x != 0:
				self.pesos[x] += layers[x-1].T.dot(deltas[(self.n_pesos-x)-1]) * eta
			else:
				self.pesos[x] += entradas.T.dot(deltas[len(deltas)-1]) * eta

	''' Carrega os pesos a partir dos pesos salvos pela funcao saveweights '''
	def loadweights(self, path='weights/', delimiter=';'):
		
		pesos_ajustados = []
		for x in xrange(self.n_pesos):
			filename = path+'pesos_'+str(x)+'.txt'
			handle = open(filename, 'r')
			read = handle.read()
			handle.close()

			spl = read.split(delimiter)
			arr = array(spl[1:len(spl)], dtype=float)
			pesos_ajustados.append(arr)

		return pesos_ajustados

	''' Roda a rede neural com os pesos treinados, e com uma entrada qualquer '''
	def run(self, entrada, path='weights/', act='sigmoid'):

		pesos_ajustados = self.loadweights(path)
		for x, value in enumerate(pesos_ajustados):
			if x == 0:
				pesos_ajustados[x] = value.reshape(self.n_entradas, self.n_hidden)
			elif x < (self.n_pesos-1):
				pesos_ajustados[x] = value.reshape(self.n_hidden, self.n_hidden)
			else:
				pesos_ajustados[x] = value.reshape(self.n_hidden, self.n_saida)

		output = single_foward(entradas=entrada, pesos=pesos_ajustados, act=act)
		return output[len(output)-1]

	''' Salva os pesos na pasta weights/ '''
	def saveweights(self, path='weights/', delimiter=';'):
		for i, ps in enumerate(self.pesos):
			for z, p in enumerate(ps):
				for c, x in enumerate(p):
					handle = open(path+'pesos_'+str(i)+'.txt', 'a')
					handle.write(delimiter+str(x))
					handle.close()

	''' Treina a rede com as entradas, saidas, entrada epecifica, saida esperada depois salva os pesos do treino '''
	def train(self, entradas, saidas, entrada, saida=False, eta=1, path='weights/', svw=True):

		q = raw_input('Continuar vai remover todos os pesos salvos ... ')
		if len(q) == '' or q.upper() != 'N':
			
			for paths,dirs,files in walk('weights/'):
				for file in files:
					remove(paths+'\\'+file)

		epochs = 0
		try:
			dc = len(str(saida[0]).split('.')[1])+2
			outputs = self.feedfoward(entrada)[len(self.feedfoward(entrada))-1]
			while str(outputs[0])[0:dc] != saida[0]:
				self.backpropagation(entradas, saidas, eta)
				outputs = self.feedfoward(entrada)[len(self.feedfoward(entrada))-1]
				epochs += 1
				print str(outputs[0])[0:dc], saida[0], epochs
		except KeyboardInterrupt:
			pass

		if svw:
			print("\n[+] Salvando pesos ...")
			self.saveweights(path)

		#return outputs[len(outputs)-1]