############################################################
# HOMEWORK 4
#
# Team members: Deniz Celik and Jacob Riedel
#
# Emails: deniz.celik@students.olin.edu
#         jacob.riedel@students.olin.edu
#
# Remarks:
#


import sys
from pyparsing import Word, Literal, ZeroOrMore, OneOrMore, Keyword, Forward, alphas, alphanums
from pyparsing import Group, Suppress


#
# Expressions
#

class Exp (object):
    def type ():
        return "expression"


class EValue (Exp):
    # Value literal (could presumably replace EInteger and EBoolean)
    def __init__ (self,v):
        self._value = v
    
    def __str__ (self):
        return "EValue({})".format(self._value)

    def eval (self,fun_dict):
        return self._value

    def substitute (self,id,new_e):
        return self

    def evalEnv(self, fun_dict, env):
        return self.eval(fun_dict)


class EInteger (Exp):
    # Integer literal

    def __init__ (self,i):
        self._integer = i

    def __str__ (self):
        return "EInteger({})".format(self._integer)

    def eval (self,fun_dict):
        return VInteger(self._integer)

    def substitute (self,id,new_e):
        return self

    def evalEnv(self, fun_dict, env):
        return self.eval(fun_dict)


class EBoolean (Exp):
    # Boolean literal

    def __init__ (self,b):
        self._boolean = b

    def __str__ (self):
        return "EBoolean({})".format(self._boolean)

    def eval (self,fun_dict):
        return VBoolean(self._boolean)

    def substitute (self,id,new_e):
        return self

    def evalEnv(self, fun_dict, env):
        return self.eval(fun_dict)


class EPrimCall (Exp):
    # Call an underlying Python primitive, passing in Values
    #
    # simplifying the prim call
    # it takes an explicit function as first argument

    def __init__ (self,prim,es):
        self._prim = prim
        self._exps = es

    def __str__ (self):
        return "EPrimCall(<prim>,[{}])".format(",".join([ str(e) for e in self._exps]))

    def eval (self,fun_dict):
        vs = [ e.eval(fun_dict) for e in self._exps ]
        return apply(self._prim,vs)

    def substitute (self,id,new_e):
        new_es = [ e.substitute(id,new_e) for e in self._exps]
        return EPrimCall(self._prim,new_es)

    def evalEnv (self, fun_dict, env):
        vs = [ e.evalEnv(fun_dict,env) for e in self._exps]
        return apply(self._prim,vs)


class EIf (Exp):
    # Conditional expression

    def __init__ (self,e1,e2,e3):
        self._cond = e1
        self._then = e2
        self._else = e3

    def __str__ (self):
        return "EIf({},{},{})".format(self._cond,self._then,self._else)

    def eval (self,fun_dict):
        v = self._cond.eval(fun_dict)
        if v.type != "boolean":
            raise Exception ("Runtime error: condition not a Boolean")
        if v.value:
            return self._then.eval(fun_dict)
        else:
            return self._else.eval(fun_dict)

    def substitute (self,id,new_e):
        return EIf(self._cond.substitute(id,new_e),
                   self._then.substitute(id,new_e),
                   self._else.substitute(id,new_e))

    def evalEnv(self, fun_dict, env):
        v = self._cond.evalEnv(fun_dict,env)
        if v.type != "boolean":
            raise Exception ("Runtime error: condition not a Boolean")
        if v.value:
            return self._then.evalEnv(fun_dict,env)
        else:
            return self._else.evalEnv(fun_dict,env)


class ELet (Exp):
    # local binding
    # allow multiple bindings
    # eager (call-by-avlue)

    def __init__ (self,bindings,e2):
        self._bindings = bindings
        self._e2 = e2

    def __str__ (self):
        return "ELet([{}],{})".format(",".join([ "({},{})".format(id,str(exp)) for (id,exp) in self._bindings ]),self._e2)

    def eval (self,fun_dict):
        # by this point, all substitutions in bindings expressions have happened already (!)
        new_e2 = self._e2
        for (id,e) in self._bindings:
            v = e.eval(fun_dict)
            new_e2 = new_e2.substitute(id,EValue(v))
        return new_e2.eval(fun_dict)

    def substitute (self,id,new_e):
        new_bindings = [ (bid,be.substitute(id,new_e)) for (bid,be) in self._bindings]
        if id in [ bid for (bid,_) in self._bindings]:
            return ELet(new_bindings, self._e2)
        return ELet(new_bindings, self._e2.substitute(id,new_e))

    def evalEnv (self, fun_dict, env):
        for (id,e) in self._bindings:
            env.append((id,e.evalEnv(fun_dict,env)))
        temp = self._e2.evalEnv(fun_dict,env)
        env.pop()
        return temp


class EId (Exp):
    # identifier

    def __init__ (self,id):
        self._id = id

    def __str__ (self):
        return "EId({})".format(self._id)

    def eval (self,fun_dict):
        raise Exception("Runtime error: unknown identifier {}".format(self._id))

    def substitute (self,id,new_e):
        if id == self._id:
            return new_e
        return self

    def evalEnv (self, fun_dict, env):
        # print env
        for i in xrange(len(env)-1,-1,-1):
            #print env[i][0]
            if env[i][0]==self._id:
                #print env[i][1]
                return env[i][1]
        return self

class ECall (Exp):
    # Call a defined function in the function dictionary

    def __init__ (self,name,es):
        self._name = name
        self._exps = es

    def __str__ (self):
        return "ECall({},[{}])".format(self._name,",".join([ str(e) for e in self._exps]))

    def eval (self,fun_dict):
        vs = [ e.eval(fun_dict) for e in self._exps ]
        params = fun_dict[self._name]["params"]
        body = fun_dict[self._name]["body"]
        if len(params) != len(vs):
            raise Exception("Runtime error: wrong number of argument calling function {}".format(self._name))
        for (val,p) in zip(vs,params):
            body = body.substitute(p,EValue(val))
        return body.eval(fun_dict)

    def substitute (self,var,new_e):
        new_es = [ e.substitute(var,new_e) for e in self._exps]
        return ECall(self._name,new_es)

    def evalEnv (self, fun_dict, env):
        vs = [ e.evalEnv(fun_dict,env) for e in self._exps]

        params = fun_dict[self._name]["params"]
        body = fun_dict[self._name]["body"]
        if len(params) != len(vs):
            raise Exception("Runtime error: wrong number of argument calling function {}".format(self._name))
        
        for (val,p) in zip(vs,params):
            body = body.substitute(p,EValue(val))
        
        return body.evalEnv(fun_dict,env)


    
#
# Values
#

class Value (object):
    pass


class VInteger (Value):
    # Value representation of integers
    
    def __init__ (self,i):
        self.value = i
        self.type = "integer"

    def __str__ (self):
        return str(self.value)

class VBoolean (Value):
    # Value representation of Booleans
    
    def __init__ (self,b):
        self.value = b
        self.type = "boolean"

    def __str__ (self):
        return "true" if self.value else "false"



# Primitive operations

def oper_plus (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value + v2.value)
    raise Exception ("Runtime error: trying to add non-numbers")

def oper_minus (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value - v2.value)
    raise Exception ("Runtime error: trying to subtract non-numbers")

def oper_times (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value * v2.value)
    raise Exception ("Runtime error: trying to multiply non-numbers")

def oper_zero (v1):
    if v1.type == "integer":
        return VBoolean(v1.value==0)
    raise Exception ("Runtime error: type error in zero?")


# Initial primitives dictionary

INITIAL_FUN_DICT = {
    "+": {"params":["x","y"],
          "body":EPrimCall(oper_plus,[EId("x"),EId("y")])},
    "-": {"params":["x","y"],
          "body":EPrimCall(oper_minus,[EId("x"),EId("y")])},
    "*": {"params":["x","y"],
          "body":EPrimCall(oper_times,[EId("x"),EId("y")])},
    "zero?": {"params":["x"],
              "body":EPrimCall(oper_zero,[EId("x")])},
    "square": {"params":["x"],
               "body":ECall("*",[EId("x"),EId("x")])},
    "=": {"params":["x","y"],
          "body":ECall("zero?",[ECall("-",[EId("x"),EId("y")])])},
    "+1": {"params":["x"],
           "body":ECall("+",[EId("x"),EValue(VInteger(1))])},
    "sum_from_to": {"params":["s","e"],
                    "body":EIf(ECall("=",[EId("s"),EId("e")]),
                               EId("s"),
                               ECall("+",[EId("s"),
                                          ECall("sum_from_to",[ECall("+1",[EId("s")]),
                                                               EId("e")])]))}
}



##
## PARSER
##
# cf http://pyparsing.wikispaces.com/


def parse (input):
    # parse a string into an element of the abstract representation

    # Grammar:
    #
    # <expr> ::= <integer>
    #            true
    #            false
    #            <identifier>
    #            ( if <expr> <expr> <expr> )
    #            ( let ( ( <name> <expr> ) ) <expr> )
    #            ( <name> <expr> ... )
    #


    idChars = alphas+"_+*-?!=<>"

    pIDENTIFIER = Word(idChars, idChars+"0123456789")
    pIDENTIFIER.setParseAction(lambda result: EId(result[0]))

    # A name is like an identifier but it does not return an EId...
    pNAME = Word(idChars,idChars+"0123456789")

    pNAMES = ZeroOrMore(pNAME)
    pNAMES.setParseAction(lambda result: [result])

    pINTEGER = Word("-0123456789","0123456789")
    pINTEGER.setParseAction(lambda result: EInteger(int(result[0])))

    pBOOLEAN = Keyword("true") | Keyword("false")
    pBOOLEAN.setParseAction(lambda result: EBoolean(result[0]=="true"))

    pEXPR = Forward()

    pIF = "(" + Keyword("if") + pEXPR + pEXPR + pEXPR + ")"
    pIF.setParseAction(lambda result: EIf(result[2],result[3],result[4]))

    pBINDING = "(" + pNAME + pEXPR + ")"
    pBINDING.setParseAction(lambda result: (result[1],result[2]))

    pBINDINGS = OneOrMore(pBINDING)
    pBINDINGS.setParseAction(lambda result: [ result ])

    def parseCOND(result):
        # print result
        if len(result) == 3:
            return EBoolean(False)
        if len(result) == 7:
            return EIf(result[3],result[4],EBoolean(False))
        return EIf(result[3],result[4],parseCOND(result[0:2]+result[6:]))


    pCOND = "(" + Keyword("cond") + ZeroOrMore("(" + pEXPR + pEXPR + ")") + ")"
    pCOND.setParseAction(parseCOND)

    pLET = "(" + Keyword("let") + "(" + pBINDINGS + ")" + pEXPR + ")"
    pLET.setParseAction(lambda result: ELet(result[3],result[5]))

    def parseLETS(result):
        if len(result[3])==1:
            return ELet(result[3],result[5])
        return ELet([result[3][0]],parseLETS(result[0:3]+[result[3][1:]]+result[-3:]))

    pLETS = "(" + Keyword("let*") + "(" + pBINDINGS + ")" + pEXPR + ")"
    pLETS.setParseAction(parseLETS)

    pEXPRS = ZeroOrMore(pEXPR)
    pEXPRS.setParseAction(lambda result: [result])

    def parseAND(result):
        if len(result)==3:
            return EBoolean(True)
        if len(result)==4:
            return result[2]
        if len(result)==5:
            return EIf(result[2],result[3],EBoolean(False))
        return EIf(result[2],parseAND(result[0:2]+result[3:]),EBoolean(False))

    pAND = "(" + Keyword("and") + ZeroOrMore(pEXPR) + ")"
    pAND.setParseAction(parseAND)

    def parseOR(result):
        if len(result)==3:
            return EBoolean(False)
        if len(result)==4:
            return result[2]
        if len(result)==5:
            return EIf(result[2],EBoolean(True),result[3])
        return EIf(result[2],EBoolean(True),parseOR(result[0:2]+result[3:]))

    pOR = "(" + Keyword("or") + ZeroOrMore(pEXPR) + ")"
    pOR.setParseAction(parseOR)

    def parseCASE(result):
        body = EBoolean(False)
        if len(result[3])==0:
            return ELet([("___case___",result[2])],body)
        for group in result[3]:
            body = EIf(parseOR(["(","or"]+[ECall("=",[EId("___case___"),e]) for e in group[:-1]]+[")"]),group[-1],body)

        #body = EIf(parseOR(),body)
        return ELet([("___case___",result[2])],body)

    pCASE = "(" + Keyword("case") + pEXPR + Group(ZeroOrMore(Suppress("(" + "(") + Group(OneOrMore(pINTEGER) + Suppress(")") + pEXPR) + Suppress(")"))) + ")"
    pCASE.setParseAction(parseCASE)

    pCALL = "(" + pNAME + pEXPRS + ")"
    pCALL.setParseAction(lambda result: ECall(result[1],result[2]))

    pEXPR << (pINTEGER | pBOOLEAN | pIDENTIFIER | pAND | pOR | pIF | pLETS | pLET | pCOND | pCASE | pCALL)

    # can't attach a parse action to pEXPR because of recursion, so let's duplicate the parser
    pTOPEXPR = pEXPR.copy()
    pTOPEXPR.setParseAction(lambda result: {"result":"expression","expr":result[0]})
    
    pDEFUN = "(" + Keyword("defun") + pNAME + "(" + pNAMES + ")" + pEXPR + ")"
    pDEFUN.setParseAction(lambda result: {"result":"function",
                                          "name":result[2],
                                          "params":result[4],
                                          "body":result[6]})

    pTOP = (pDEFUN | pTOPEXPR)

    result = pTOP.parseString(input)[0]
    return result    # the first element of the result is the expression


def shell ():
    # A simple shell
    # Repeatedly read a line of input, parse it, and evaluate the result

    print "Homework 4 - Calc Language"

    # work on a copy because we'll be adding to it
    fun_dict = INITIAL_FUN_DICT.copy()
    
    while True:
        inp = raw_input("calc> ")
        if not inp:
            return
        result = parse(inp)
        if result["result"] == "expression":
            exp = result["expr"]
            print "Abstract representation:", exp
            v = exp.eval(fun_dict)
            print v
        elif result["result"] == "function":
            # a result is already of the right form to put in the
            # functions dictionary
            fun_dict[result["name"]] = result
            print "Function {} added to functions dictionary".format(result["name"])

def shellEnv():
    # A simple shell
    # Repeatedly read a line of input, parse it, and evaluate the result

    print "Homework 4 - Calc Language"

    # work on a copy because we'll be adding to it
    fun_dict = INITIAL_FUN_DICT.copy()
    
    while True:
        inp = raw_input("calc> ")
        if not inp:
            return
        result = parse(inp)
        if result["result"] == "expression":
            exp = result["expr"]
            print "Abstract representation:", exp
            v = exp.evalEnv(fun_dict,[])
            print v
        elif result["result"] == "function":
            # a result is already of the right form to put in the
            # functions dictionary
            fun_dict[result["name"]] = result
            print "Function {} added to functions dictionary".format(result["name"])


# increase stack size to let us call recursive functions quasi comfortably
sys.setrecursionlimit(10000)

def printTest (exp):
    result = parse(exp)
    fun_dict = INITIAL_FUN_DICT.copy()
    print "calc> {}".format(exp)
    if result["result"] == "expression":
            exp = result["expr"]
            print "Abstract representation:", exp
            v = exp.eval(fun_dict)
            print v
    elif result["result"] == "function":
        # a result is already of the right form to put in the
        # functions dictionary
        fun_dict[result["name"]] = result
        print "Function {} added to functions dictionary".format(result["name"])

def printTestEnv (exp):
    result = parse(exp)
    fun_dict = INITIAL_FUN_DICT.copy()
    print "calc> {}".format(exp)
    if result["result"] == "expression":
            exp = result["expr"]
            print "Abstract representation:", exp
            v = exp.evalEnv(fun_dict,[])
            print v
    elif result["result"] == "function":
        # a result is already of the right form to put in the
        # functions dictionary
        fun_dict[result["name"]] = result
        print "Function {} added to functions dictionary".format(result["name"])


if __name__ == '__main__':
    #Question 1a
    print "Tests for Question 1a"
    printTest("(and)")
    printTest("(and true)")
    printTest("(and true false)")
    printTest("(and false true)")
    printTest("(and false 999)")
    printTest("(and (= 1 1))")
    printTest("(and (= 1 1) (= 1 2))")
    printTest("(and true false true)")
    printTest("(let ((x true)) (and x x false true))")

    printTest("(or)")
    printTest("(or true)")
    printTest("(or false)")
    printTest("(or true false)")
    printTest("(or false false)")
    printTest("(or true false false)")
    printTest("(or true false 99)")
    printTest("(or true false false true)")
    printTest("(or (= 1 1))")
    printTest("(or (= 1 1) (= 1 2))")

    #Question 1b
    print "Tests for Question 1b"
    printTest("(let* ((x 10)) x)")
    printTest("(let* ((x 10) (y (+ x 1))) y)")
    printTest("(let* ((x 10) (y (+ x 1)) (z (+ y 1))) x)")
    printTest("(let* ((x 10) (y (+ x 1)) (z (+ y 1))) y)")
    printTest("(let* ((x 10) (y (+ x 1)) (z (+ y 1))) z)")

    #Question 1c
    print "Tests for Question 1c"
    printTest("(cond)")
    printTest("(cond (true 10))")
    printTest("(cond (false 20) (true 30))")
    printTest("(cond ((= 1 2) 20) ((= 1 1) 30))")
    printTest("(cond ((= 1 2) 20) ((= 1 3) 30))")

    #Question 1d
    print "Tests for Question 1d"
    printTest("(case 1)")
    printTest("(case 1 ((1 2 3) 99) ((4 5 6) 66))")
    printTest("(case 2 ((1 2 3) 99) ((4 5 6) 66))")
    printTest("(case 5 ((1 2 3) 99) ((4 5 6) 66))")
    printTest("(case 8 ((1 2 3) 99) ((4 5 6) 66))")

    #Question 2
    print "Tests for Question 2"
    printTestEnv("(let ((x 10)) (+ (let ((x 20)) (* x x)) x))")
    printTestEnv("(let ((x 10)) (+ (let ((y 20)) (* y y)) x))")
    printTestEnv("(let ((x 10)) (let ((y (+ x 1))) (let ((x (* y 2))) (* x x))))")
    printTestEnv("(let* ((x 10)) x)")
    printTestEnv("(let* ((x 10) (y (+ x 1))) y)")
    printTestEnv("(let* ((x 10) (y (+ x 1)) (z (+ y 1))) x)")
    printTestEnv("(let* ((x 10) (y (+ x 1)) (z (+ y 1))) y)")
    printTestEnv("(let* ((x 10) (y (+ x 1)) (z (+ y 1))) z)")
    printTestEnv("(let ((x 10) (y 30)) (+ (let ((x 20)) (* x y)) x))")

    #shell()
