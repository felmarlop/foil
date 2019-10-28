# coding=utf-8
import itertools
import math
import sys
import pprint

"""
    Nombre:FÉLIX MARTÍN LÓPEZ dni:47511647H
    Algoritmo Foil y nFoil con la resolución de los siguientes problemas:
    · Ser hija de
    · Ser abuelo de
    -Problemas nuevos inventados-
    · Ser madre de
    · Ser nieto de

El algoritmo Foil en el cual me baso se encuentra entre las transparencias 45 y
61 del tema 8 de Inteligencia Artificial, en las cuales aparecen
también los problemas hija y abuelo que se ejecutan al final. Los otros dos
problemas (madre y nieto) son inventados.

El algoritmo NFoil es bastante parecido a Foil, con la diferencia de algunos
metodos nuevos procedentes de Foil pero con algunas modificaciones. El "mejor",
que utiliza una ganancia distinta utilizando la antigua; y el nFoil, que ha
diferencia de Foil, tiene un umbral de parada en el bucle externo, que debe ser
menor que la ganancia actual, la cual vamos actualizando.
Los problemas que resuelvo con nFoil son los mismo que los de Foil.

La referencia donde me he basado para implementar nfoil es la siguiente:
http://people.csail.mit.edu/kersting/papers/landwehr07jmlr_nfoil.pdf

Reseña: Decisiones de implementación:
- Comencé implementando los métodos getCubiertos_regla() y genera()
especificamente para usar variables sólo hasta D. Sin embargo después cambié
el modo y lo hice de forma más genérica, sin tener en cuenta cuando nos llega
una C o una D. Para ello me creo una lista de múltiples variables (puede tener
muchas) y la voy recorriendo y utilizando en ambos métodos según hagan falta,
de esa manera podemos utilizar foil para reglas con muchas más variables de las
que hemos visto en teoría.
Por último, me decanté por ir generando tantas variables como me hagan falta,
acorde con la aridad de los predicados de la BC.
Utilizo una V más un numero que voy incrementando cuando sea necesario, es
mucho mejor para el caso genérico.
- Se utilizan listas para guardar variables o devolver resultados de los
métodos. También diccionarios donde guardo pares de valores de variables y su
correspondiente constante según los ejemplos que nos dan para ser cubiertos.
- En la ejecución, la base de conocimiento de cada problema será un metodo que
nos devuelve una lista con todos los predicados disponibles. También será un
método el que genera todos los ejemplos negativos de acuerdo con la hipótesis
del conjunto cerrado
-El parametro de ejemplos, E, que se le pasa al algoritmo, Foil y nFoil, lleva
dentro los ejemplos positivos y negativos. Yo se los paso al metodo por
separado, ejemplosP y ejemplosN.

Se utilizan dos tipos de estructuras de datos que son las clases pred() y
regla(), para crear predicados y reglas, necesarias para el algoritmo.
"""

# FOIL
# Clases para predicados y reglas


class pred():
    variables = []

    """Constructor del predicado. Nnombre y lista de variables"""
    def __init__(self, nPredicado, variables):
        self.nPredicado = nPredicado
        self.variables = variables

    """Devuelve el nombre del predicado"""
    def getnPredicado(self):
        return self.nPredicado

    """Devuelve las variables del predicado"""
    def getVariables(self):
        return self.variables

    """Metodos para mosrtrar el predicado y para comparar"""
    def __repr__(self):
        return self.nPredicado + self.variables.__repr__()

    def __equals__(self, other):
        return (self.nPredicado, self.variables) == \
            (other.nPredicado, other.variables)


class regla():
    cabecera = pred
    extensiones = []

    """Constructor de la regla. Cabecera y lista de predicados."""
    def __init__(self, cabecera, extensiones):
        self.cabecera = cabecera
        self.extensiones = extensiones

    """Devuelve la cabecera de la regla"""
    def getCabecera(self):
        return self.cabecera

    """Devuelve la lista de predicados o extensiones de la regla"""
    def getExtensiones(self):
        return self.extensiones

    """Metodo para añadir una extension o condicion"""
    def addExtension(self, extension):
        self.extensiones.append(extension)

    """Metodos para mostrar la regla y para comparar"""
    def __repr__(self):
        if not self.extensiones:
            return self.cabecera.__repr__()
        else:
            return (self.cabecera.__repr__() + " :- " +
                    self.extensiones.__repr__())


# Variables y Ganancia
# Método util que devuelve las variables de una regla
def getVariables_regla(r):
    listaVar = []
    varCabecera = r.getCabecera().getVariables()
    for i in range(varCabecera.__len__()):
        if varCabecera[i] not in listaVar:
            listaVar.append(varCabecera[i])
    varExtensiones = r.getExtensiones()
    if not len(varExtensiones) == 0:
        for i in range(varExtensiones.__len__()):
            for j in range(varExtensiones[i].getVariables().__len__()):
                if varExtensiones[i].getVariables()[j] not in listaVar:
                    listaVar.append(varExtensiones[i].getVariables()[j])
    sorted(listaVar)
    return listaVar


"""
t:Ejemplos positivos cubiertos por R y R'(regla nueva).
p:Ejemplos positivos cubiertos por R.
n:Ejemplos negativos cubiertos por R.
ppr:Ejemplos positivos cubiertos por R'.
npr:Ejemplos negativos cubiertos por R'.
"""


# Devuelve la ganancia de una regla
def getGanancia_informacion(t, p, n, ppr, npr):
    if (t == 0):
        res = 0
    else:
        try:
            res = round(t * (math.log(ppr / float(ppr + npr), 2) -
                             math.log(p / float(p + n), 2)), 3)
        except Exception:
            print("Oops! ocurrió un error calculando la ganacia.")
            res = 0
    return res


# Constantes, extender ejemplos y variables contenidas
# Metodo util que devuelve las constantes sin repetir del problema.
def getConstantes(bc):
    res = []
    for pred in bc:
        for v in pred.getVariables():
            if v not in res:
                res.append(v)
    return res


# Implementación del mundo cerrado
def mundoCerrado(bc, p, ejP):
    cl = []
    res = []
    cl.extend(itertools.product(getConstantes(bc),
              repeat=len(p.getVariables())))
    for c in cl:
        if list(c) not in ejP:
            res.append(list(c))
    return res


"""
El siguiente metodo devuelve tambien las variables que están en la condicion y
tambien en la cabecera. En el caso de que existan varias extensiones o
condiciones, comprueba si en la ultima extensión hay variables que están en la
cabecera o en el resto de extensiones, devolviendo tambien esa lista de
variables coincidentes.
"""


# Metodo util que prueba si hay variables no contenidas en la cabecera.
def contieneVar(r1):
    salida = []
    varCoincidentes = []
    c = 0
    varCabecera = r1.getCabecera().getVariables()
    varExtension = r1.getExtensiones()[-1].getVariables()
    varRestoExtensiones = []
    if len(r1.getExtensiones()) > 1:
        for n in range(len(r1.getExtensiones())-1):
            varRestoExtensiones.extend(r1.getExtensiones()[n].getVariables())
        for i in varExtension:
            if i not in varCabecera and i not in varRestoExtensiones:
                c = 1
            else:
                varCoincidentes.append(i)
    else:
        for i in varExtension:
            if i not in varCabecera:
                c = 1
            else:
                varCoincidentes.append(i)
    myset = set(varCoincidentes)
    listaFin = list(myset)
    salida.insert(0, c)
    salida.insert(1, listaFin)
    return salida


# Ejemplos cubiertos y métodos: genera, mejor y foil
"""
Calculamos los ejemplos que una regla cubre. Si la regla no tiene ninguna
extensión, los ejemplos que cubre son directamente los que le pasamos. Se
devolverá un array de dichos ejemplos
"""


def getCubiertos_regla(r1, ej, constantes_Problema, bc):
    """
    Definimos la lista de ejemplos, la de las variables conocidas, y
    guardamos en ella las variables de la regla que ya conocemos.
    """
    ejemplos = []
    varConocidas = []
    varConocidas.extend(r1.getCabecera().getVariables())
    constExtension = []

    """
    Inicializamos un diccionario llamado pares donde tendremos los pares de
    valores que sustsituyen las variables que conocemos por las constantes
    del ejemplo por donde iremos recorriendo.
    """
    pares = {}

    # Comprobamos si tenemos alguna condición o extensión.
    if len(r1.getExtensiones()) == 0:
        ejemplos.extend(ej)
    else:
        # Continuamos guardando las variables conocidas.
        for ex in r1.getExtensiones()[:-1]:
            for v in ex.getVariables():
                if v not in varConocidas:
                    varConocidas.append(v)

        contiene0 = contieneVar(r1)[0]
        contiene1 = contieneVar(r1)[1]

        """
        Guardamos en el diccionario los pares de valores. Tendremos despues
        dos casos. 1. Si todas las variables de la extension nueva están en la
        cabecera o en alguna otra extension o condicion. 2. Si hay variables en
        la extension que no están en la cabecera ni en ninguna otra extensión.
        """
        for i in range(len(ej)):
            for j in range(len(varConocidas)):
                pares[varConocidas[j]] = ej[i][j]
            # caso 1
            if not contiene0:
                """
                Una vez creado los pares, recorremos las variables de la
                extension y las sustituimos por la correspondiente constante.
                """
                for k in range(len(r1.getExtensiones()[-1].getVariables())):
                    constExtension.append(pares[r1.getExtensiones()[-1]
                                                .getVariables()[k]])
                """
                Creamos por ultimo el predicado con la lista de constantes y
                su nombre, y comprobamos si existe en la base de conocimiento.
                Si existe, el ejemplo por cual vamos es cubierto.
                """
                p1 = pred(r1.getExtensiones()[-1].getnPredicado(),
                          constExtension)
                for z in range(len(bc)):
                    if p1.__equals__(bc[z]):
                        ejemplos.append(ej[i])
                constExtension = []
            # caso 2
            elif contiene0 == 1:
                vNuevas = []
                for e in r1.getExtensiones()[-1].getVariables():
                    if e not in contiene1:
                        vNuevas.append(e)
                """
                Recorremos la base de conocimiento, comprobando si el nombre
                del predicado es igual al de la extension de la regla que nos
                llega. Guardamos en una lista el grupo de constantes de cada
                predicado de la bc.
                """
                for pr in bc:
                    ejCubierto = []
                    constPredicado = []
                    if (pr.getnPredicado() ==
                            r1.getExtensiones()[-1].getnPredicado()):
                        constPredicado.extend(pr.getVariables()[:])
                        """
                        Recorremos las variables que coinciden en la cabecera y
                        en el resto de extensiones (contieneVar(r1)[1]) y
                        sacamos sus posiciones en la nueva extensión.
                        """
                        for var in contiene1:
                            vUltima = r1.getExtensiones()[-1].getVariables()[:]
                            posiciones = [item for item in range(len(vUltima))
                                          if vUltima[item] == var]
                            """
                            Comprobamos si en las posiciones que hemos
                            calculado en el predicado de la BC se encuentra la
                            misma constanteque la asignada a la variable por la
                            que vamos comprobando, registrada en "pares". Si es
                            así, las vamos eliminando hasta quedarnos solo con
                            lo que valen las variables nuevas de la condición
                            que nos ha llegado.
                            """
                            for pos in posiciones:
                                if pr.getVariables()[pos] == pares[var]:
                                    constPredicado.remove(pares[var])
                                else:
                                    break
                        """
                        Por último, la lista de valores de las constantes
                        nuevas la añadimos al ejemplo cubierto. Tratando además
                        cuandoexisten variables repetidas.
                        """
                        if len(constPredicado) == len(vNuevas):
                            if len(set(constPredicado)) == len(set(vNuevas)):
                                nPares = {}
                                flag = True
                                for ii in range(len(vNuevas)):
                                    if vNuevas[ii] not in nPares:
                                        nPares[vNuevas[ii]] = \
                                            constPredicado[ii]
                                    else:
                                        if (nPares[vNuevas[ii]] !=
                                                constPredicado[ii]):
                                            flag = False
                                if flag:
                                    ejCubierto.extend(ej[i])
                                    ejCubierto.extend(constPredicado)
                                    ejemplos.append(ejCubierto)
    return ejemplos


"""
Método util que devuelve todos los posibles predicados que podemos añadir
al cuerpo de la regla.
"""


def genera(r2, bc):
    aux = []
    # Guardamos en una lista las variables de la regla.
    variables = getVariables_regla(r2)[:]
    pr1 = []
    prn = []
    nombreP = []
    combinaciones = []
    validas = []
    """
    Clasificamos los literales que tienen una variable de los que tiene más de
    una, guardando su nombre en el primer caso, en el segundo guardamos los
    literales completos, sin repetirlos con el mismo nombre.
    """
    for i in bc:
        if len(i.getVariables()) == 1:
            if i.getnPredicado() not in pr1:
                pr1.append(i.getnPredicado())
        else:
            if i.getnPredicado() not in nombreP:
                nombreP.append(i.getnPredicado())
                prn.append(i)
    """
    Recorremos los nombres de los literales y vamos creando predicados por
    cada variable que haya.
    """
    for j in pr1:
        for k in variables:
            p = pred(j, [k])
            aux.append(p)
    """
    Hacemos lo mismo para los siguientes literales, pero en este caso haciendo
    combinaciones de variables en tantas posiciones como constantes tenga el
    literal. Hay que tener en cuenta que alguna variable debe aparecer en la
    cabecera de la regla o en alguna extension o condición anterior. Para ello,
    cogemos las válidas, las que cumplan lo anterior.
    Añadimoss tantas variables según cual sea la aridad del literal por el que
    vamos menos 1. Este valor 1 es el de la variable que debe existir de antes.
    """
    for l in prn:
        variables = getVariables_regla(r2)[:]
        for ad in range(len(l.getVariables())-1):
            if variables[-1][0] == "V" and len(variables[-1]) > 1:
                i = int(variables[-1][1:])+1
                variables.append("V"+str(i))
            else:
                variables.append("V1")
        combinaciones.extend(itertools.product(variables,
                                               repeat=len(l.getVariables())))
        # Aquí escojo las combinaciones válidas.
        for item in combinaciones:
            if any(x in getVariables_regla(r2) for x in list(item)):
                if item not in validas:
                    validas.append(list(item))
        for m in validas:
            p1 = pred(l.getnPredicado(), m)
            aux.append(p1)
        combinaciones = []
        variables = []
    return aux


"""
Metodo que nos devuelve el mejor literal para añadir al cuerpo de la regla.
Inicialmente la regla no tiene niguna extension o condicion.
"""


def mejor(reg, pos, ejP, ejN, constantes_Problema, bc):
    ganancia = 0
    res = []
    """
    Guardamos la lista de literales o predicados a partir del metodo genera.
    Calculamos la lista de positivos y negativos cubiertos inicialmente.
    """
    literales = genera(reg, bc)
    cubiertosP = pos
    """
    Recorremos la lista de literales y vamos calculando, añadiendo el literal
    a la regla, los nuevos ejemplos negativos y positivos cubiertos.
    """
    for literal in literales:
        reg.addExtension(literal)
        cubiertosPn = getCubiertos_regla(reg, ejP, constantes_Problema, bc)
        cubiertosNn = getCubiertos_regla(reg, ejN, constantes_Problema, bc)
        """
        Calculamos la t (Necesaria para calcular la ganancia). La calculamos
        utilizando los primeros ejemplos positivos que tuvimos en el problema,
        haciendo una intersección con los actuales.
        """
        aux = []
        ej = []
        for i in cubiertosPn:
            for j in range(len(cubiertosP[0])):
                ej.append(i[j])
            if ej in cubiertosP:
                if ej not in aux:
                    aux.append(ej)
            ej = []
        t = len(aux)

        # Calculamos ganancia
        gananciaAct = getGanancia_informacion(t, len(ejP), len(ejN),
                                              len(cubiertosPn),
                                              len(cubiertosNn))
        """
        Pintamos la regla y borramos el ultimo literal añadido para seguir
        probando con los siguientes. Devolvemos el literal de mayor ganancia.
        """
        print("%s ----> Ganancia: %s" % (reg.__repr__(),
                                         gananciaAct.__repr__()))
        reg.getExtensiones().remove(literal)
        if gananciaAct > ganancia:
            ganancia = gananciaAct
            res = literal
    if res:
        print("Literal escogido: %s\n" % res)
    return res


"""
Metodo que nos devuelve la regla aprendida eligiendo los mejores literales o
predicados a partir del metodo mejor()
"""


def foil(ejemplosP, ejemplosN, bc, predObjetivo):
    # Seguiremos los pasos del algoritmo foil del Tema 8.
    # Guardamos las constantes del problema.
    constantes_Problema = getConstantes(bc)
    # 1.Reglas aprendidas igual a vacío.
    reglas_Aprendidas = []
    # 2.Hacer E igual a ejemplos.
    EP = []
    EN = []
    EP = ejemplosP
    EN = ejemplosN
    cubiertosFin = []
    ej = []
    literalL = []
    # Debemos comprobar si hay ejemplos positivos.
    if not EP:
        print("Debe haber al menos un ejemplo positivo.")
    # 3.Mientras en E haya ejemplos positivos.Bucle externo
    while EP:
        # 3.1 Crear una regla R sin cuerpo y con cabeza P(predObejtivo)
        reglaIni = regla(predObjetivo, [])
        # 3.2 Mientras haya en E ejemplos negativos cubiertos por R.
        positivos = []
        negativos = []
        positivos = EP
        negativos = EN
        # Bucle interno.
        while len(negativos) > 0:
            # 3.2.1 Posibles literales que pueden ser añadidos a la regla.
            # La lista de literales la crea dentro del metodo mejor()
            # 3.2.2 De todos ellos sea L el mejor.
            literalL = mejor(reglaIni, ejemplosP, positivos, negativos,
                             constantes_Problema, bc)
            if not literalL:
                print("\nNo se puede obtener el siguiente mejor literal" +
                      " para la regla " + reglaIni.__repr__() + " con los" +
                      " ejemplos ofrecidos")
                break
            # 3.2.3 Actualizar R añadiendo el literal L al cuerpo de R
            reglaIni.addExtension(literalL)
            # Calculo nuevos negativos y positivos para el literal mejor.
            negativos = getCubiertos_regla(reglaIni, negativos,
                                           constantes_Problema, bc)
            positivos = getCubiertos_regla(reglaIni, positivos,
                                           constantes_Problema, bc)
            """
            Voy creando una lista de todos los positivos cubiertos para
            despues borrarla de EP como dice el algoritmo.
            """
            for i in positivos:
                for j in range(len(predObjetivo.getVariables())):
                    ej.append(i[j])
                if ej not in cubiertosFin:
                    cubiertosFin.append(ej)
                ej = []
        # 3.3 Incluir R en reglas aprendidas.
        if not literalL:
            print("Regla aprendida:\n%s" % reglaIni.__repr__())
            break
        reglas_Aprendidas.append(reglaIni)
        print("Regla aprendida:\n%s" % reglaIni.__repr__())
        # Actualizar ejemplos quitando los que esten cubiertos por la regla.
        for m in cubiertosFin:
            if EP.__contains__(m):
                EP.remove(m)
    print("Total de reglas aprendidas: ")
    pprint.pprint(reglas_Aprendidas)
    return reglas_Aprendidas


"""NFOIL"""

"""
En NFOIL implementaremos 3 metodos nuevos que son diferentes con respecto
a los de FOIL. Son el mejorNfoil, el nfoil y el gananciaNofil
"""

"""
Delvuel el valor de la ganancia nfoil de una regla.
p:ejemplos positivos iniciales. Corresponde al método score de nFOIL
"""


def getGanancia_nFoil(t, p, n, ppr, npr):
    if (t == 0):
        res = 0
    else:
        try:
            res = round(((t / float(p + n + npr)) *
                         (math.log(ppr / float(ppr + npr), 2) -
                          math.log(p / float(p + n), 2))), 3)
        except Exception:
            res = 0
    return res


"""
Método similar al mejor de FOIL, pero en este caso la ganancia es distinta,
específica para nfoil. Devuelve, además del mejor literal, la ganancia o score
del mismo
"""


def mejorNfoil(reg, pos, ejP, ejN, constantes_Problema, bc):
    ganancia = 0
    res = []
    """
    Guardamos la lista de literales o predicados a partir del metodo genera.
    Calculamos la lista de positivos y negativos cubiertos inicialmente.
    """
    literales = genera(reg, bc)
    cubiertosP = pos
    """
    Recorremos la lista de literales y vamos calculando, añadiendo el literal
    a la regla, los nuevos ejemplos negativos y positivos cubiertos.
    """
    for literal in literales:
        reg.addExtension(literal)
        cubiertosPn = getCubiertos_regla(reg, ejP, constantes_Problema, bc)
        cubiertosNn = getCubiertos_regla(reg, ejN, constantes_Problema, bc)
        """
        Calculamos la t (Necesaria para calcular la ganancia). La calculamos
        utilizando los primeros ejemplos positivos que tuvimos en el problema,
        haciendo una intersección con los actuales.
        """
        aux = []
        ej = []
        for i in cubiertosPn:
            for j in range(len(cubiertosP[0])):
                ej.append(i[j])
            if ej in cubiertosP:
                if ej not in aux:
                    aux.append(ej)
            ej = []
        t = len(aux)
        # Calculamos ganancia
        gananciaAct = getGanancia_nFoil(t, len(ejP), len(ejN),
                                        len(cubiertosPn), len(cubiertosNn))
        """
        Pintamos la regla y borramos el ultimo literal añadido para seguir
        probando con los siguientes. Devolvemos el literal de mayor ganancia.
        """
        print("%s ----> Ganancia: %s" % (reg.__repr__(),
                                         gananciaAct.__repr__()))
        reg.getExtensiones().remove(literal)
        if gananciaAct > ganancia:
            ganancia = gananciaAct
            res = literal
    if (res != []):
        print("Literal escogido: %s\n" % res)
    resFin = [res, ganancia]
    return resFin


"""
Método similar al foil, sin embargo en este caso utilizamos el
mejorNfoil para calcular el mejor candidato. También ponemos un umbral
para terminar con el bucle externo, que debe ser menor que la ganancia
acumulada
"""


def nFoil(ejemplosP, ejemplosN, bc, predObjetivo):
    """
    Seguiremos los pasos del algoritmo foil del Tema 8.
    Guardamos las constantes del problema.
    """
    constantes_Problema = getConstantes(bc)
    # 1.Reglas aprendidas igual a vacío.
    reglas_Aprendidas = []
    # 2.Hacer E igual a ejemplos.
    EP = []
    EN = []
    EP = ejemplosP
    EN = ejemplosN
    cubiertosFin = []
    ej = []
    literalL = []
    # Tienen que existir ejemplos positivos.
    if not EP:
        print("Debe haber al menos un ejemplo positivo.")
    """
    Definimos el umbral correspondiente a nfoil necesario para la parada del
    bucle externo.
    """
    umbral = 0.9*len(ejemplosP)
    gananciaAct = 10
    # 3.Mientras en E haya ejemplos positivos.Bucle externo
    while gananciaAct > umbral:
        # 3.1 Crear una regla R sin cuerpo y con cabeza P(predObejtivo)
        reglaIni = regla(predObjetivo, [])
        # 3.2 Mientras haya en E ejemplos negativos cubiertos por R.
        positivos = []
        negativos = []
        positivos = EP
        negativos = EN
        # Bucle interno.
        while len(negativos) > 0:
            # 3.2.1 Generar los literales que pueden ser añadidos a la regla.
            # La lista de literales la crea dentro del metodo mejor()
            # 3.2.2 De todos ellos sea L el mejor.
            mejor = mejorNfoil(reglaIni, ejemplosP, positivos, negativos,
                               constantes_Problema, bc)
            literalL = mejor[0]
            gananciaAct = mejor[1]
            if not literalL:
                print("\nError: No se puede obtener el siguiente mejor" +
                      " literal para la regla " + reglaIni.__repr__() +
                      " con los ejemplos ofrecidos")
                break
            # 3.2.3 Actualizar R añadiendo el literal L al cuerpo de R
            reglaIni.addExtension(literalL)
            # Calculo los negativos y positivos para sacar el literal mejor.
            negativos = getCubiertos_regla(reglaIni, negativos,
                                           constantes_Problema, bc)
            positivos = getCubiertos_regla(reglaIni, positivos,
                                           constantes_Problema, bc)
            """
            Voy creando una lista de todos los positivos cubiertos para
            despues borrarla de EP como dice el algoritmo.
            """
            for i in positivos:
                for j in range(len(ejemplosP[0])):
                    ej.append(i[j])
                if ej not in cubiertosFin:
                    cubiertosFin.append(ej)
                ej = []
        # 3.3 Incluir R en reglas aprendidas.
        if not literalL:
            print("Regla aprendida:\n%s" % reglaIni.__repr__())
            break
        reglas_Aprendidas.append(reglaIni)
        print("Regla aprendida:\n %s" % reglaIni.__repr__())
        # Actualizar ejemplos quitando los que esten cubiertos por la regla.
        for m in cubiertosFin:
            if EP.__contains__(m):
                EP.remove(m)
    print("Total de reglas aprendidas: ")
    pprint.pprint(reglas_Aprendidas)
    return reglas_Aprendidas


"""
Ejecución de los Problemas
IMPORTANTE: Utilizar siempre variables de una sola letra. En el caso de
tener que utilizar más de un carácter, que sea una letra más un número.
"""
print("================")
print("     FOIL")
print("================")
print("Problema Ejemplo 2")
print("===============================================================\n")
pc11 = pred("r1", ["7", "1", "7", "5"])
pc22 = pred("r1", ["7", "2", "7", "3"])
pc33 = pred("r1", ["7", "1", "7", "8"])
pc44 = pred("r1", ["1", "7", "1", "8"])
bc2 = [pc11, pc22, pc33, pc44]
p11 = pred("p", ["A", "B"])
ejemplosPos = [["5", "6"], ["3", "4"], ["8", "9"]]
ejemplosNeg = [["2", "1"], ["7", "2"]]
print("Predicado objetivo: %s\n" % p11)
foil(ejemplosPos, ejemplosNeg, bc2, p11)
print("\n===============================================================")
print("Resolución: SER HIJA DE mediante FOIL")
print("===============================================================\n")

"""Creamos la base de conocimiento"""


def bc_hija():
    pc1 = pred("progenitor", ["Ana", "Maria"])
    pc2 = pred("progenitor", ["Ana", "Tomas"])
    pc3 = pred("mujer", ["Ana"])
    pc4 = pred("mujer", ["Maria"])
    pc5 = pred("progenitor", ["Sebas", "Ana"])
    pc6 = pred("mujer", ["Eva"])
    pc7 = pred("hombre", ["Tomas"])
    pc8 = pred("hombre", ["Ignacio"])
    pc9 = pred("progenitor", ["Tomas", "Eva"])
    pc10 = pred("progenitor", ["Tomas", "Ignacio"])

    return [pc1, pc2, pc3, pc4, pc5, pc6, pc7, pc8, pc9, pc10]


p = pred("hija", ["A", "B"])
print("Predicado objetivo: %s\n" % p)

"""Ejemplos positivos y negativos"""
ejemplosPhija = [["Maria", "Ana"], ["Eva", "Tomas"]]
ejemplosNhija = [["Tomas", "Ana"], ["Eva", "Ana"], ["Eva", "Ignacio"]]

"""Ejecución FOIL"""
foil(ejemplosPhija, ejemplosNhija, bc_hija(), p)


print("\n===============================================================")
print("Resolución: SER ABUELO DE mediante FOIL")
print("===============================================================\n")

"""Creamos la base de conocimiento"""


def bc_abuelo():
    res = []
    aux1 = ["CARLOS", "ANA", "ANDRES", "EDUARDO"]
    for i in range(len(aux1)):
        pr1 = pred("padre", ["FELIPE", aux1[i]])
        pr2 = pred("progenitor", ["FELIPE", aux1[i]])
        res.append(pr1)
        res.append(pr2)
    aux2 = ["GUILLERMO", "HARRY"]
    for i in range(len(aux2)):
        pr1 = pred("padre", ["CARLOS", aux2[i]])
        pr2 = pred("progenitor", ["CARLOS", aux2[i]])
        res.append(pr1)
        res.append(pr2)
    aux3 = ["PEDRO", "ZARA"]
    for i in range(len(aux3)):
        pr1 = pred("padre", ["MARK", aux3[i]])
        pr2 = pred("progenitor", ["MARK", aux3[i]])
        res.append(pr1)
        res.append(pr2)
    aux4 = ["BEATRIZ", "EUGENIA"]
    for i in range(len(aux4)):
        pr1 = pred("padre", ["ANDRES", aux4[i]])
        pr2 = pred("progenitor", ["ANDRES", aux4[i]])
        res.append(pr1)
        res.append(pr2)
    aux5 = ["CARLOS", "ANA", "ANDRES", "EDUARDO"]
    for i in range(len(aux5)):
        pr1 = pred("madre", ["ISABEL", aux5[i]])
        pr2 = pred("progenitor", ["ISABEL", aux5[i]])
        res.append(pr1)
        res.append(pr2)
    aux6 = ["GUILLERMO", "HARRY"]
    for i in range(len(aux6)):
        pr1 = pred("madre", ["DIANA", aux6[i]])
        pr2 = pred("progenitor", ["DIANA", aux6[i]])
        res.append(pr1)
        res.append(pr2)
    aux7 = ["ZARA", "PEDRO"]
    for i in range(len(aux7)):
        pr1 = pred("madre", ["ANA", aux7[i]])
        pr2 = pred("progenitor", ["ANA", aux7[i]])
        res.append(pr1)
        res.append(pr2)
    aux8 = ["BEATRIZ", "EUGENIA"]
    for i in range(len(aux8)):
        pr1 = pred("madre", ["SARA", aux8[i]])
        pr2 = pred("progenitor", ["SARA", aux8[i]])
        res.append(pr1)
        res.append(pr2)
    return res


p2 = pred("abuelo", ["A", "B"])
print("Predicado objetivo: %s\n" % p2)

"""Ejemplos positivos y negativos"""
ejemplosPabuelo = [["FELIPE", "GUILLERMO"], ["FELIPE", "HARRY"],
                   ["FELIPE", "PEDRO"], ["FELIPE", "ZARA"],
                   ["FELIPE", "BEATRIZ"], ["FELIPE", "EUGENIA"]]
"""Los ejemplos negativos deben calcularse respetando la hipótesis del mundo ce
rrado. El siguiente método devuelve una lista de dichos ejemplos"""
ejemplosNabuelo = mundoCerrado(bc_abuelo(), p2, ejemplosPabuelo)
ejemplosNabuelo2 = ejemplosNabuelo
"""Ejecución FOIL"""
foil(ejemplosPabuelo, ejemplosNabuelo, bc_abuelo(), p2)

"""Problemas nuevos"""
print("\n===============================================================")
print("Resolución: SER MADRE DE mediante FOIL")
print("===============================================================\n")

"""Creamos la base de conocimiento"""


def bc_madre():
    pc1 = pred("progenitor", ["CARMEN", "MARIA"])
    pc2 = pred("progenitor", ["MANOLI", "TOMAS"])
    pc3 = pred("mujer", ["CARMEN"])
    pc4 = pred("mujer", ["MANOLI"])
    pc5 = pred("progenitor", ["JUAN", "ANA"])
    pc6 = pred("mujer", ["ANA"])
    pc7 = pred("hombre", ["JUAN"])
    pc8 = pred("hombre", ["TOMAS"])
    pc9 = pred("progenitor", ["TOMAS", "EVA"])
    pc10 = pred("mujer", ["EVA"])
    return [pc1, pc2, pc3, pc4, pc5, pc6, pc7, pc8, pc9, pc10]


p3 = pred("madre", ["A", "B"])
print("Predicado objetivo: %s\n" % p3)

"""Ejemplos positivos y negativos"""
ejemplosPmadre = [["CARMEN", "MARIA"], ["MANOLI", "TOMAS"]]
ejemplosNmadre = mundoCerrado(bc_madre(), p3, ejemplosPmadre)
ejemplosNmadre2 = ejemplosNmadre

"""Ejecución FOIL"""
foil(ejemplosPmadre, ejemplosNmadre, bc_madre(), p3)

print("\n===============================================================")
print("Resolución: SER NIETO DE mediante FOIL")
print("===============================================================\n")

"""Base de conocimiento"""


def bc_nieto():
    res = []
    aux1 = ["CARLOS", "ANA", "ANDRES", "EDUARDO"]
    for i in range(len(aux1)):
        pr1 = pred("padre", ["FELIPE", aux1[i]])
        pr2 = pred("progenitor", ["FELIPE", aux1[i]])
        res.append(pr1)
        res.append(pr2)
    pr3 = pred("hombre", ["FELIPE"])
    res.append(pr3)
    aux2 = ["GUILLERMO", "HARRY"]
    for i in range(len(aux2)):
        pr1 = pred("padre", ["CARLOS", aux2[i]])
        pr2 = pred("progenitor", ["CARLOS", aux2[i]])
        res.append(pr1)
        res.append(pr2)
    aux3 = ["PEDRO", "ZARA"]
    for i in range(len(aux3)):
        pr1 = pred("padre", ["MARK", aux3[i]])
        pr2 = pred("progenitor", ["MARK", aux3[i]])
        res.append(pr1)
        res.append(pr2)
    pr3 = pred("hombre", ["MARK"])
    res.append(pr3)
    aux4 = ["BEATRIZ", "EUGENIA"]
    for i in range(len(aux4)):
        pr1 = pred("padre", ["ANDRES", aux4[i]])
        pr2 = pred("progenitor", ["ANDRES", aux4[i]])
        res.append(pr1)
        res.append(pr2)
    aux5 = ["CARLOS", "ANA", "ANDRES", "EDUARDO"]
    for i in range(len(aux5)):
        pr1 = pred("madre", ["ISABEL", aux5[i]])
        pr2 = pred("progenitor", ["ISABEL", aux5[i]])
        res.append(pr1)
        res.append(pr2)
    pr3 = pred("mujer", ["ISABEL"])
    pr4 = pred("hombre", ["ANDRES"])
    pr5 = pred("hombre", ["EDUARDO"])
    pr6 = pred("hombre", ["CARLOS"])
    res.append(pr3)
    res.append(pr4)
    res.append(pr5)
    res.append(pr6)
    aux6 = ["GUILLERMO", "HARRY"]
    for i in range(len(aux6)):
        pr1 = pred("madre", ["DIANA", aux6[i]])
        pr2 = pred("progenitor", ["DIANA", aux6[i]])
        res.append(pr1)
        res.append(pr2)
    pr3 = pred("hombre", ["GUILLERMO"])
    pr4 = pred("hombre", ["HARRY"])
    pr5 = pred("mujer", ["DIANA"])
    res.append(pr3)
    res.append(pr4)
    res.append(pr5)
    aux7 = ["ZARA", "PEDRO"]
    for i in range(len(aux7)):
        pr1 = pred("madre", ["ANA", aux7[i]])
        pr2 = pred("progenitor", ["ANA", aux7[i]])
        res.append(pr1)
        res.append(pr2)
    pr3 = pred("mujer", ["ZARA"])
    pr4 = pred("mujer", ["ANA"])
    pr5 = pred("hombre", ["PEDRO"])
    res.append(pr3)
    res.append(pr4)
    res.append(pr5)
    aux8 = ["BEATRIZ", "EUGENIA"]
    for i in range(len(aux8)):
        pr1 = pred("madre", ["SARA", aux8[i]])
        pr2 = pred("progenitor", ["SARA", aux8[i]])
        res.append(pr1)
        res.append(pr2)
    pr3 = pred("mujer", ["SARA"])
    pr4 = pred("mujer", ["BEATRIZ"])
    pr5 = pred("mujer", ["EUGENIA"])
    res.append(pr3)
    res.append(pr4)
    res.append(pr5)
    return res


p4 = pred("nieto", ["A", "B"])
print("Predicado objetivo: %s\n" % p4)

"""Ejemplos positivos y negativos"""
ejemplosPnieto = [["GUILLERMO", "FELIPE"], ["HARRY", "FELIPE"],
                  ["PEDRO", "FELIPE"], ["GUILLERMO", "ISABEL"],
                  ["HARRY", "ISABEL"], ["PEDRO", "ISABEL"]]
ejemplosNnieto = mundoCerrado(bc_nieto(), p4, ejemplosPnieto)
ejemplosNnieto2 = ejemplosNnieto
"""Ejecución FOIL"""
foil(ejemplosPnieto, ejemplosNnieto, bc_nieto(), p4)
print("================")
print("     NFOIL")
print("================")
"""Los predicados y las bases de conocimiento son las mismas que en FOIL"""
print("\n===============================================================")
print("Resolución: SER HIJA DE mediante NFOIL")
print("===============================================================\n")
print("Predicado objetivo: %s\n" % p)
"""Ejemplos positivos y negativos"""
ejemplosPhija = [["Maria", "Ana"], ["Eva", "Tomas"]]
ejemplosNhija = [["Tomas", "Ana"], ["Eva", "Ana"], ["Eva", "Ignacio"]]
nFoil(ejemplosPhija, ejemplosNhija, bc_hija(), p)

print("\n===============================================================")
print("Resolución: SER ABUELO DE mediante NFOIL")
print("===============================================================\n")
print("Predicado objetivo: %s\n" % p2)
"""Ejemplos positivos. Negativos creados en FOIL"""
ejemplosPabuelo = [["FELIPE", "GUILLERMO"], ["FELIPE", "HARRY"],
                   ["FELIPE", "PEDRO"], ["FELIPE", "ZARA"],
                   ["FELIPE", "BEATRIZ"], ["FELIPE", "EUGENIA"]]
nFoil(ejemplosPabuelo, ejemplosNabuelo2, bc_abuelo(), p2)

"""Problemas nuevos inventados"""
print("\n===============================================================")
print("Resolución: SER MADRE DE mediante NFOIL")
print("===============================================================\n")
print("Predicado objetivo: %s\n" % p3)
"""Ejemplos positivos. Negativos creados en FOIL"""
ejemplosPmadre = [["CARMEN", "MARIA"], ["MANOLI", "TOMAS"]]
nFoil(ejemplosPmadre, ejemplosNmadre2, bc_madre(), p3)

print("\n===============================================================")
print("Resolución: SER NIETO DE mediante NFOIL")
print("===============================================================\n")
print("Predicado objetivo: %s\n" % p4)
"""Ejemplos positivos. Negativos creados en FOIL"""
ejemplosPnieto = [["GUILLERMO", "FELIPE"], ["HARRY", "FELIPE"],
                  ["PEDRO", "FELIPE"], ["GUILLERMO", "ISABEL"],
                  ["HARRY", "ISABEL"], ["PEDRO", "ISABEL"]]
nFoil(ejemplosPnieto, ejemplosNnieto2, bc_nieto(), p4)
