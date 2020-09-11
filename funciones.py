import math,operator
def Coincidencias(vec1,vec2):
	num = 0
	radX = 0
	radY = 0
	for x, itemX in enumerate(vec1):
		idxX = itemX[0]
		valX = itemX[1]
		radX += (valX ** 2)
		for y, itemY in enumerate(vec2):
			idxY = itemY[0]
			valY = itemY[1]
			radY += (valY ** 2)
			if (idxX == idxY):
				num += (valY * valX)
	den = (math.sqrt(radX) * math.sqrt(radY/len(vec1)))
	total = num / den
	return total

def ExisteItem(vec,item):
	existe = [False,0]
	for x, itemX in enumerate(vec):
		if (itemX[0] == item):
			existe = [True,itemX[1]]
	return existe

def ListaRecomendados(vectores):
  calificacionesfinales = {}
  calificacionesrepetidas = {}
  for usuario, vector in vectores.items():
    for x, itemX in enumerate(vector[1]):
      for usuario_, vector_ in vectores.items():
        if ( usuario_ != usuario ):
          existencia = ExisteItem( vector_[1], itemX[0] )
          if ( existencia[0] == True ):
            if not (itemX[0] in calificacionesrepetidas):
              calificacionesrepetidas[itemX[0]] = []
              if (existencia[1]>2):
                calificacionesrepetidas[itemX[0]].append(vector_[0])
            else:
              if (existencia[1]>2):
                calificacionesrepetidas[itemX[0]].append(vector_[0])
          elif (itemX[1]>2):
              calificacionesfinales[itemX[0]] = vector[0]
  for usuario, calificacion in calificacionesrepetidas.items():
    calificacionesfinales[usuario]=(sum(calificacion) / float(len(calificacion)))
  recomendaciones = []
  recomendaciones_sort = sorted(calificacionesfinales.items(), key=operator.itemgetter(1), reverse=True)
  for name in enumerate(recomendaciones_sort):
  	recomendaciones.append([name[1][0],calificacionesfinales[name[1][0]]])
  return recomendaciones#calificacionesfinales