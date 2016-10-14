############################################################
# HOMEWORK 5
#
# Team members: Deniz Celik, Jacob Riedel
#
# Emails: deniz.celik@students.olin.edu
#         jacob.riedel@students.olin.edu
#
# Remarks: 
#        



import sys

#
# Expressions
#

class Exp (object):
    pass


class EValue (Exp):
    # Value literal (could presumably replace EInteger and EBoolean)
    def __init__ (self,v):
        self._value = v
    
    def __str__ (self):
        return "EValue({})".format(self._value)

    def eval (self,env):
        return self._value

    
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

    def eval (self,env):
        vs = [ e.eval(env) for e in self._exps ]
        return apply(self._prim,vs)


class EIf (Exp):
    # Conditional expression

    def __init__ (self,e1,e2,e3):
        self._cond = e1
        self._then = e2
        self._else = e3

    def __str__ (self):
        return "EIf({},{},{})".format(self._cond,self._then,self._else)

    def eval (self,env):
        v = self._cond.eval(env)
        if v.type != "boolean":
            raise Exception ("Runtime error: condition not a Boolean")
        if v.value:
            return self._then.eval(env)
        else:
            return self._else.eval(env)


class EId (Exp):
    # identifier

    def __init__ (self,id):
        self._id = id

    def __str__ (self):
        return "EId({})".format(self._id)

    def eval (self,env):
        for (id,v) in env:
            if self._id == id:
                return v
        raise Exception("Runtime error: unknown identifier {}".format(self._id))


class ECall (Exp):
    # Call a defined function in the function dictionary
    # can be pass several arguments, but only handles one

    def __init__ (self,fun,exps):
        self._fun = fun
        #if len(exps) != 1:
        #    raise Exception("ERROR: multi-argument ECall not implemented")
        self._args = exps#[0]

    def __str__ (self):
        return "ECall({},[{}])".format(str(self._fun),",".join([ str(e) for e in self._args]))

    def eval (self,env):
        f = self._fun.eval(env)
        if f.type != "function":
            raise Exception("Runtime error: trying to call a non-function")
        new_env = [(p,a.eval(env)) for (p,a) in zip(f.params,self._args)] + f.env
        return f.body.eval(new_env)

class EFunction (Exp):
    # Creates an anonymous function 

    def __init__ (self,params,body,name=None):
        self._params = params
        self._body = body
        self._name=name

    def __str__ (self):
        if self._name==None:
            return "EFunction([{}],{})"\
                .format(",".join([ str(e) for e in self._params]),str(self._body))
        return "EFunction([{}],{},name={})"\
                .format(",".join([ str(e) for e in self._params]),str(self._body),str(self._name))

    def eval (self,env):
        if self._name==None:
            return VClosure(self._params,self._body,env)
        return VClosure(self._params,self._body,env,name=self._name)

    
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

    
class VClosure (Value):
    
    def __init__ (self,params,body,env,name=None):
        self.params = params
        self.body = body
        self.type = "function"
        if name==None:
            self.env = env
        else:
            self.env = [(name,self)]+env
        
    def __str__ (self):
        return "<function [{}] {}>".format(",".join([ str(e) for e in self.params]),str(self.body))



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


# Initial environment

# this initial environment works with Q1 when you've completed it

def initial_env ():
    env = []
    env.insert(0,
        ("+",
         VClosure(["x","y"],EPrimCall(oper_plus,
                                      [EId("x"),EId("y")]),
                  env)))
    env.insert(0,
        ("-",
         VClosure(["x","y"],EPrimCall(oper_minus,
                                      [EId("x"),EId("y")]),
                  env)))
    env.insert(0,
        ("*",
         VClosure(["x","y"],EPrimCall(oper_times,
                                      [EId("x"),EId("y")]),
                  env)))
    env.insert(0,
        ("zero?",
         VClosure(["x"],EPrimCall(oper_zero,
                                  [EId("x")]),
                  env)))
    env.insert(0,
        ("square",
         VClosure(["x"],ECall(EId("*"),[EId("x"),EId("x")]),
                  env)))
    env.insert(0,
        ("=",
         VClosure(["x","y"],ECall(EId("zero?"),
                                  [ECall(EId("-"),[EId("x"),EId("y")])]),
                  env)))
    env.insert(0,
        ("+1",
         VClosure(["x"],ECall(EId("+"),[EId("x"),EValue(VInteger(1))]),
                  env)))
    return env



##
## PARSER
##
# cf http://pyparsing.wikispaces.com/

from pyparsing import Word, Literal, ZeroOrMore, OneOrMore, Keyword, Forward, alphas, alphanums
from pyparsing import Group


def letUnimplementedError ():
    raise Exception ("ERROR: let functionality not implemented yet")

def parse (input):
    # parse a string into an element of the abstract representation

    # Grammar:
    #
    # <expr> ::= <integer>
    #            true
    #            false
    #            <identifier>
    #            ( if <expr> <expr> <expr> )
    #            ( let ( ( <name> <expr> ) ) <expr )
    #            (function ( <name> ) <expr> )
    #            ( <expr> <expr> )
    #
    # <definition> ::= ( defun <name> ( <name> ) <expr> )
    #


    idChars = alphas+"_+*-~/?!=<>"

    pIDENTIFIER = Word(idChars, idChars+"0123456789")
    pIDENTIFIER.setParseAction(lambda result: EId(result[0]))

    # A name is like an identifier but it does not return an EId...
    pNAME = Word(idChars,idChars+"0123456789")

    pINTEGER = Word("0123456789")
    pINTEGER.setParseAction(lambda result: EValue(VInteger(int(result[0]))))

    pBOOLEAN = Keyword("true") | Keyword("false")
    pBOOLEAN.setParseAction(lambda result: EValue(VBoolean(result[0]=="true")))

    pEXPR = Forward()

    pIF = "(" + Keyword("if") + pEXPR + pEXPR + pEXPR + ")"
    pIF.setParseAction(lambda result: EIf(result[2],result[3],result[4]))

    pBINDING = "(" + pNAME + pEXPR + ")"
    pBINDING.setParseAction(lambda result: (result[1],result[2]))

    pBINDINGS = OneOrMore(pBINDING)
    pBINDINGS.setParseAction(lambda result: [ result ])

    def letparse(result):
        return ECall(EFunction([id for (id,_) in result[3]],result[5]),[val for (_,val) in result[3]])

    pLET = "(" + Keyword("let") + "(" + pBINDINGS + ")" + pEXPR + ")"
    pLET.setParseAction(letparse)

    pCALL = "(" + pEXPR + Group(OneOrMore(pEXPR)) + ")"
    pCALL.setParseAction(lambda result: ECall(result[1],result[2]))

    pFUN = "(" + Keyword("function") + "(" + Group(OneOrMore(pNAME)) + ")" + pEXPR + ")"
    pFUN.setParseAction(lambda result: EFunction(result[3],result[5]))

    pRECFUN = "(" + Keyword("function") + pNAME + "(" + Group(OneOrMore(pNAME)) + ")" + pEXPR + ")"
    pRECFUN.setParseAction(lambda result: EFunction(result[4],result[6],name=result[2]))

    pEXPR << (pINTEGER | pBOOLEAN | pIDENTIFIER | pIF | pLET | pFUN | pRECFUN | pCALL)

    # can't attach a parse action to pEXPR because of recursion, so let's duplicate the parser
    pTOPEXPR = pEXPR.copy()
    pTOPEXPR.setParseAction(lambda result: {"result":"expression","expr":result[0]})

    pDEFUN = "(" + Keyword("defun") + pNAME + "(" + Group(OneOrMore(pNAME)) + ")" + pEXPR + ")"
    pDEFUN.setParseAction(lambda result: {"result":"function",
                                          "name":result[2],
                                          "param":result[4],
                                          "body":result[6]})
    pTOP = (pDEFUN | pTOPEXPR)

    result = pTOP.parseString(input)[0]
    return result    # the first element of the result is the expression


def shell ():
    # A simple shell
    # Repeatedly read a line of input, parse it, and evaluate the result

    print "Homework 5 - Func Language"
    print "#quit to quit"
    env = []

    ## UNCOMMENT THIS LINE WHEN YOU COMPLETE Q1 IF YOU WANT TO TRY
    ## EXAMPLES
    env = initial_env()
    while True:
        inp = raw_input("func> ")

        if inp == "#quit":
            return

        try:
            result = parse(inp)

            if result["result"] == "expression":
                exp = result["expr"]
                print "Abstract representation:", exp
                v = exp.eval(env)
                print v

            elif result["result"] == "function":
                # the top-level environment is special, it is shared
                # amongst all the top-level closures so that all top-level
                # functions can refer to each other
                env.insert(0,(result["name"],VClosure(result["param"],result["body"],env)))
                print "Function {} added to top-level environment".format(result["name"])

        except Exception as e:
            print "Exception: {}".format(e)


        
# increase stack size to let us call recursive functions quasi comfortably
sys.setrecursionlimit(10000)



def initial_env_curry ():
    env = []
    env.insert(0,
        ("+",
         VClosure(["x"],EFunction("y",EPrimCall(oper_plus,
                                              [EId("x"),EId("y")])),
                  env)))
    env.insert(0,
        ("-",
         VClosure(["x"],EFunction("y",EPrimCall(oper_minus,
                                              [EId("x"),EId("y")])),
                  env)))
    env.insert(0,
        ("*",
         VClosure(["x"],EFunction("y",EPrimCall(oper_times,
                                              [EId("x"),EId("y")])),
                  env)))
    env.insert(0,
        ("zero?",
         VClosure(["x"],EPrimCall(oper_zero,
                                         [EId("x")]),
                           env)))
    env.insert(0,
        ("square",
         VClosure(["x"],ECall(ECall(EId("*"),[EId("x")]),
                            [EId("x")]),
                  env)))
    env.insert(0,
        ("=",
         VClosure(["x"],EFunction("y",ECall(EId("zero?"),
                                          [ECall(ECall(EId("-"),[EId("x")]),
                                                 [EId("y")])])),
                  env)))
    env.insert(0,
        ("+1",
         VClosure(["x"],ECall(ECall(EId("+"),[EId("x")]),
                            [EValue(VInteger(1))]),
                  env)))
    return env



def parse_curry (input):
    # parse a string into an element of the abstract representation

    # Grammar:
    #
    # <expr> ::= <integer>
    #            true
    #            false
    #            <identifier>
    #            ( if <expr> <expr> <expr> )
    #            ( let ( ( <name> <expr> ) ) <expr )
    #            (function ( <name> ) <expr> )
    #            ( <expr> <expr> )
    #
    # <definition> ::= ( defun <name> ( <name> ) <expr> )
    #

    idChars = alphas+"_+*-~/?!=<>"

    pIDENTIFIER = Word(idChars, idChars+"0123456789")
    pIDENTIFIER.setParseAction(lambda result: EId(result[0]))

    # A name is like an identifier but it does not return an EId...
    pNAME = Word(idChars,idChars+"0123456789")

    pINTEGER = Word("0123456789")
    pINTEGER.setParseAction(lambda result: EValue(VInteger(int(result[0]))))

    pBOOLEAN = Keyword("true") | Keyword("false")
    pBOOLEAN.setParseAction(lambda result: EValue(VBoolean(result[0]=="true")))

    pEXPR = Forward()

    pIF = "(" + Keyword("if") + pEXPR + pEXPR + pEXPR + ")"
    pIF.setParseAction(lambda result: EIf(result[2],result[3],result[4]))

    pBINDING = "(" + pNAME + pEXPR + ")"
    pBINDING.setParseAction(lambda result: (result[1],result[2]))

    pBINDINGS = OneOrMore(pBINDING)
    pBINDINGS.setParseAction(lambda result: [ result ])

    def letparse(result):
        return ECall(EFunction([id for (id,_) in result[3]],result[5]),[val for (_,val) in result[3]])

    pLET = "(" + Keyword("let") + "(" + pBINDINGS + ")" + pEXPR + ")"
    pLET.setParseAction(letparse)

    def callparse(result):
        def call_recurse(lst):
            if len(lst)==1:
                return ECall(result[1],lst)
            return ECall(call_recurse(lst[:-1]),[lst[-1]])
        return call_recurse(result[2])

    pCALL = "(" + pEXPR + Group(OneOrMore(pEXPR)) + ")"
    pCALL.setParseAction(callparse)

    def funparse(result):
        def fun_recurse(lst):
            if len(lst)==1:
                return EFunction(lst,result[5])
            return EFunction(lst[0],fun_recurse(lst[1:]))
        return fun_recurse(result[3])

    pFUN = "(" + Keyword("function") + "(" + Group(OneOrMore(pNAME)) + ")" + pEXPR + ")"
    pFUN.setParseAction(funparse)

    pEXPR << (pINTEGER | pBOOLEAN | pIDENTIFIER | pIF | pLET | pFUN | pCALL)

    # can't attach a parse action to pEXPR because of recursion, so let's duplicate the parser
    pTOPEXPR = pEXPR.copy()
    pTOPEXPR.setParseAction(lambda result: {"result":"expression","expr":result[0]})

    def defunparse(result):
        temp = funparse(["(","function","(",result[4][1:],")",result[6],")"])
        #print temp

        return {"result":"function",
                  "name":result[2],
                  "param":result[4][0],
                  "body":temp}

    pDEFUN = "(" + Keyword("defun") + pNAME + "(" + Group(OneOrMore(pNAME)) + ")" + pEXPR + ")"
    pDEFUN.setParseAction(defunparse)
    pTOP = (pDEFUN | pTOPEXPR)

    result = pTOP.parseString(input)[0]
    return result    # the first element of the result is the expression


def shell_curry ():

    print "Homework 5 - Func Language"
    print "#quit to quit"
    env = initial_env_curry()
    
    while True:
        inp = raw_input("func/curry> ")

        if inp == "#quit":
            return

        try:
            result = parse_curry(inp)

            if result["result"] == "expression":
                exp = result["expr"]
                print "Abstract representation:", exp
                v = exp.eval(env)
                print v

            elif result["result"] == "function":
                env.insert(0,(result["name"],VClosure(result["param"],result["body"],env)))
                print "Function {} added to top-level environment".format(result["name"])

        except Exception as e:
            print "Exception: {}".format(e)

def printTest (exp,env):
    print "func> {}".format(exp)
    result = parse(exp)

    if result["result"] == "expression":
        exp = result["expr"]
        print "Abstract representation:", exp
        v = exp.eval(env)
        print v

    elif result["result"] == "function":
        env.insert(0,(result["name"],VClosure(result["param"],result["body"],env)))
        print "Function {} added to top-level environment".format(result["name"])


def printTestCurry(exp,env):
    print "func/curry> {}".format(exp)
    result = parse_curry(exp)

    if result["result"] == "expression":
        exp = result["expr"]
        print "Abstract representation:", exp
        v = exp.eval(env)
        print v

    elif result["result"] == "function":
        env.insert(0,(result["name"],VClosure(result["param"],result["body"],env)))
        print "Function {} added to top-level environment".format(result["name"])

if __name__ == '__main__':

    # Question 1
    print "Question 1"
    global_env = initial_env()
    printTest("(function (x y) (+ x y))",global_env)
    printTest("((function (x y) (+ x y)) 10 20)",global_env)
    printTest("(defun sum2 (x y) (+ x y))",global_env)
    printTest("(sum2 10 20)",global_env)
    printTest("(defun sum3 (x y z) (+ x (+ y z)))",global_env)
    printTest("(sum3 10 20 30)",global_env)
    printTest("(sum3 (sum2 10 20) 30 40)",global_env)

    # Question 2A
    print "Question 2A"
    global_env = initial_env()
    printTest("(let ((x 10)) x)",global_env)
    printTest("(let ((x 10)) (+ x 1))",global_env)
    printTest("(let ((x 10) (y 20)) (+ x y))",global_env)
    printTest("(let ((x (* 2 3)) (y (* 4 5))) (+ x y))",global_env)
    printTest("(let ((x 1) (y 2) (z 3)) (+ x (* y z)))",global_env)
    printTest("(let ((x (let ((y 10)) y))) x)",global_env)

    # Question 2B
    print "Question 2B"
    global_env_curry = initial_env_curry()
    printTestCurry("+",global_env_curry)
    printTestCurry("(+ 10 20)",global_env_curry)
    printTestCurry("(* 2 3)",global_env_curry)
    printTestCurry("((function (x y) (+ x y)) 10 20)",global_env_curry)
    printTestCurry("(function (x y) (+ x y))",global_env_curry)
    printTestCurry("(defun test (x y z) (+ x (+ y z)))",global_env_curry)
    printTestCurry("test",global_env_curry)
    printTestCurry("(test 1 2 3)",global_env_curry)

    # Question 3A
    print "Question 3A"
    e = EFunction(["n"],
                  EIf(ECall(EId("zero?"),[EId("n")]),
              EValue(VInteger(0)),
              ECall(EId("+"),[EId("n"),
                              ECall(EId("me"),[ECall(EId("-"),[EId("n"),EValue(VInteger(1))])])])),
                  name="me")
    f = e.eval(initial_env())
    print f
    print ECall(EValue(f),[EValue(VInteger(10))]).eval([]).value

    #Question 3B
    print "Question 3B"
    printTest("((function (x y) (+ x y)) 10 20)",global_env)
    printTest("((function me (n) (if (zero? n) 0 (+ n (me (- n 1))))) 10)",global_env)
    printTest("(let ((sum (function me (n) (if (zero? n) 0 (+ n (me (- n 1))))))) (sum 100))",global_env)
    printTest("((function me2 (n1 n2) (if (= n2 n1) n2 (+ n2 (me2 n1 (- n2 1))))) 0 20)",global_env)