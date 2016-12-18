############################################################
# FUNC 
# S-expressions surface syntax
# reference cells
#
# Compiled to a register machine
# Compilation strategy that "inlines"
#   primitive function calls and that
#   removes anonymous functions passed
#   as continuations to primitive functions 
#

import sys
import time
import traceback



############################################################
# helper code to time the execution of a piece of code
#

class Timer(object):
    def __enter__(self):
        self.__start = time.time()
        return self

    def __exit__(self, type, value, traceback):
        # Error handling here
        self.__finish = time.time()

    def duration_in_seconds(self):
        return self.__finish - self.__start

    def time (self):
        return time.time() - self.__start




#
# Expressions
#


# CHANGE: BUILD THE ENVIRONMENT FROM THE RIGHT!


# evaluation function -- all the evaluation code is here now

def eval_iter (exp,env):
    current_exp = exp
    current_env = env
    while True:
        # these are all the special forms which directly
        # return the result of evaluating an expression
        if current_exp.expForm == "ECall":

            f = eval_iter(current_exp._fun,current_env)
            if f.type != "function":
                raise Exception("Runtime error: trying to call a non-function")
            args = [ eval_iter(e,current_env) for e in current_exp._args]
            if len(args) != len(f._params):
                raise Exception("Runtime error: argument # mismatch in call")
            new_env = f._env + zip(f._params,args)
            current_exp = f._body
            current_env = new_env

        elif current_exp.expForm == "EIf":

            v = eval_iter(current_exp._cond,current_env)
            if v.type != "boolean":
                raise Exception ("Runtime error: condition not a Boolean")
            if v.value:
                current_exp = current_exp._then
            else:
                current_exp = current_exp._else

        elif current_exp.expForm == "EValue":

            return current_exp._value

        elif current_exp.expForm == "EPrimCall":

            vs = [ eval_iter(e,current_env) for e in current_exp._exps ]
            return apply(current_exp._prim,vs)

        elif current_exp.expForm == "EId":

            for (id,v) in reversed(current_env):
                if current_exp._id == id:
                    return v
            raise Exception("Runtime error: unknown identifier {}".format(current_exp._id))

        elif current_exp.expForm == "EIdIndex":

            return current_env[current_exp._index][1]

        elif current_exp.expForm == "EFunction":
            
            return VClosure(current_exp._params,current_exp._body,current_env,current_exp._name)

        else:

            raise Exception("Unrecognized expression form: {}".format(current_exp.expForm))


class Exp (object):
    pass

    
class EValue (Exp):
    # Value literal (could presumably replace EInteger and EBoolean)
    def __init__ (self,v):
        self._value = v
        self.expForm = "EValue"
        self.is_basic = True
    
    def __str__ (self):
        return "EValue({})".format(self._value)

    def eval (self,env):
        return eval_iter(self,env)

    def cps (self,k):
        return ECall(k,[self])

    def compile_env (self,symtable):
        return self

    def compile (self):
        return ["LOAD",self._value]

    
class EPrimCall (Exp):
    # Call an underlying Python primitive, passing in Values
    #
    # simplifying the prim call
    # it takes an explicit function as first argument

    def __init__ (self,prim,es):
        self._prim = prim
        self._exps = es
        self.expForm = "EPrimCall"
        self.is_basic = True

    def __str__ (self):
        return "EPrimCall(<prim>,[{}])".format(",".join([ str(e) for e in self._exps]))

    def eval (self,env):
        return eval_iter(self,env)

    def cps (self,k):
        # under the assumption that all primcalls wrapped as a function in the top-level environment
        return ECall(k,[self])

    def compile_env (self,symtable):
        exps = [ exp.compile_env(symtable) for exp in self._exps ]
        return EPrimCall(self._prim,exps)

    def compile (self):
        raise Exception("Cannot compile EPrimCall - those should be compiled manually")


COUNTER = 0
def fresh ():
    global COUNTER
    COUNTER += 1
    return COUNTER-1


class EIf (Exp):
    # Conditional expression

    def __init__ (self,e1,e2,e3):
        self._cond = e1
        self._then = e2
        self._else = e3
        self.expForm = "EIf"
        self.is_basic = False

    def __str__ (self):
        return "EIf({},{},{})".format(self._cond,self._then,self._else)

    def eval (self,env):
        return eval_iter(self,env)

    def cps (self,k):
        if self._cond.is_basic:
            return EIf(self._cond,self._then.cps(k),self._else.cps(k))
        var = " _x{}_".format(fresh())
        return self._cond.cps(EFunction([var],EIf(EId(var),self._then.cps(k),self._else.cps(k))))

    def compile_env (self,symtable):
        condexp = self._cond.compile_env(symtable)
        thenexp = self._then.compile_env(symtable)
        elseexp = self._else.compile_env(symtable)
        return EIf(condexp,thenexp,elseexp)

    def compile (self):
        jump = "L{}".format(fresh())
        result = self._cond.compile()
        result += ["LOAD-ADDR",
                   "@"+jump,
                   "JUMP-TRUE"]
        result += self._else.compile()
        result += ["#"+jump]
        result += self._then.compile()
        return result


    
class EId (Exp):
    # identifier

    def __init__ (self,id):
        self._id = id
        self.expForm = "EId"
        self.is_basic = True

    def __str__ (self):
        return "EId({})".format(self._id)

    def eval (self,env):
        return eval_iter(self,env)

    def cps (self,k):
        return ECall(k,[self])

    def compile_env (self,symtable):
        for (index,name) in reversed(list(enumerate(symtable))):
            if name == self._id:
                return EIdIndex(index)
        raise Exception("Runtime error: unbound identifier {}".format(self._id))

    def compile (self):
        raise Exception("Cannot compile EId")

    
class EIdIndex (Exp):
    # identifier

    def __init__ (self,index):
        self._index = index
        self.expForm = "EIdIndex"
        self.is_basic = True

    def __str__ (self):
        return "EIdIndex({})".format(self._index)

    def eval (self,env):
        return eval_iter(self,env)

    def compile (self):
        return ["LOOKUP",self._index]


class ECall (Exp):
    # Call a defined function in the function dictionary
    # uses an "apply" function in the closure for encapsulation

    def __init__ (self,fun,exps):
        self._fun = fun
        self._args = exps
        self.expForm = "ECall"
        self.is_basic = False

    def __str__ (self):
        return "ECall({},[{}])".format(str(self._fun),",".join([str(e) for e in self._args]))

    def eval (self,env):
        return eval_iter(self,env)

    def cps (self,k):
        vars_e = [ " _x{}_".format(fresh()) for e in self._args ]
        var_f = " _x{}_".format(fresh())
        args = []
        cont_args = []
        cont_exps = []
        if self._fun.is_basic:
            fun = self._fun
        else:
            if self._fun.expForm == "EFunction":
                # do something special for functions
                # they are values
                # but they still need recursive transformation
                fun = self._fun.cps_function()
            else:
                fun = EId(var_f)
                cont_args.append(var_f)
                cont_exps.append(self._fun)
        for (var,e) in zip(vars_e,self._args):
            if e.is_basic:
                args.append(e)
            else:
                if e.expForm == "EFunction":
                    args.append(e.cps_function())
                else:
                    args.append(EId(var))
                    cont_args.append(var)
                    cont_exps.append(e)
        result = ECall(fun,args + [k])
        for (var,exp) in reversed(zip(cont_args,cont_exps)):
            result = exp.cps(EFunction([var],result))
        return result

    def compile_env (self,symtable):
        fun = self._fun.compile_env(symtable)
        args = [ exp.compile_env(symtable) for exp in self._args ]
        return ECall(fun,args)
        

    def compile (self):
        if self._fun.expForm == "EIdIndex" and self._fun._index < NUM_PRIMITIVES:
            # we have a call to a primitive
            # compile it specially
            result = ["CLEAR-ARGS"]
            for e in self._args[:-1]:
                result += (e.compile() + ["PUSH-ARGS"])
            result += ["PRIM-CALL",
                       PRIMITIVES[self._fun._index]]
            if self._args[-1].expForm == "EFunction":
                # NEW: 
                # we can optimize away this continuation!
                result += (["PUSH-ENV"] + 
                           self._args[-1]._body.compile())
                return result
            else:
                result += ["CLEAR-ARGS",
                           "PUSH-ARGS"]
                result += (self._args[-1].compile() + ["LOAD-ADDR-ENV","JUMP"])
                return result

        result = ["CLEAR-ARGS"]
        for e in self._args[:-1]:
            result += (e.compile() + ["PUSH-ARGS"])
        result += (self._args[-1].compile() + ["PUSH-ARGS"])
        result += (self._fun.compile() + ["LOAD-ADDR-ENV","JUMP"])
        return result


class EFunction (Exp):
    # Creates an anonymous function

    def __init__ (self,params,body,name=None):
        self._params = params
        self._body = body
        self._name = name
        self.expForm = "EFunction"
        self.is_basic = False

    def __str__ (self):
        return "EFunction([{}],{})".format(",".join(self._params),str(self._body))

    def eval (self,env):
        return eval_iter(self,env)

    def cps (self,k):
        var = " _k_{}_".format(fresh())
        return ECall(k,[EFunction([ p for p in self._params] + [var],self._body.cps(EId(var)),name=self._name)])

    # hack to get functions to compile faster...
    def cps_function (self):
        var = " _k_{}_".format(fresh())
        return EFunction([ p for p in self._params] + [var],self._body.cps(EId(var)),name=self._name)
    
    def compile_env (self,symtable):
        rec_name = [ self._name ] if self._name else []
        body = self._body.compile_env(symtable+rec_name+self._params)
        return EFunction(self._params,body,self._name)

    def compile (self):
        addr_cont = "A{}".format(fresh())
        addr_fun = "B{}".format(fresh())
        result = ["LOAD-ADDR",
                  "@"+addr_cont,
                  "JUMP"]
        result += ["#"+addr_fun]
        if self._name:
            result += ["LOAD-FUN","PUSH-ENV"]
        result += ["PUSH-ENV-ARGS"]
        result += self._body.compile()
        result += ["#"+addr_cont,
                   "LOAD-ADDR",
                   "@"+addr_fun,
                   "LOAD-FUN"]
        return result
        
    
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
        self._params = params
        self._body = body
        extra = [(name,self)] if name else []
        self._env = env + extra
        self.type = "function"

    def __str__ (self):
        return "<function [{}] {}>".format(",".join(self._params),str(self._body))


class VClosureAddr (Value):

    def __init__ (self,addr,env):
        self._addr = addr
        self._env = env    # recursive env?
        self.type = "function_addr"
        
    def __str__ (self):
        return "<function {}>".format(self._addr)
    
class VRefCell (Value):

    def __init__ (self,initial):
        self.content = initial
        self.type = "ref"

    def __str__ (self):
        return "<ref {}>".format(str(self.content))


class VNone (Value):

    def __init__ (self):
        self.type = "none"

    def __str__ (self):
        return "none"




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


def oper_ref (v1):
    return VRefCell(v1)

def oper_deref (v1):
    if v1.type == "ref":
        return v1.content
    raise Exception ("Runtime error: dereferencing a non-reference value")

def oper_update (v1,v2):
    if v1.type == "ref":
        v1.content = v2
        return VNone()
    raise Exception ("Runtime error: updating a non-reference value")
 
def oper_print (v1):
    print v1
    return VNone()





##
## PARSER
##
# cf http://pyparsing.wikispaces.com/
import subprocess
from pyparsing import Word, Literal, ZeroOrMore, OneOrMore, Keyword, Forward, alphas, alphanums, NoMatch


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
    #            ( function ( <name> ... ) <expr> )
    #            ( ref <expr> )
    #            ( <expr> <expr> ... )
    #


    idChars = alphas+"_+*-?!=<>"

    pIDENTIFIER = Word(idChars, idChars+"0123456789")
    pIDENTIFIER.setParseAction(lambda result: EId(result[0]))

    # A name is like an identifier but it does not return an EId...
    pNAME = Word(idChars,idChars+"0123456789")

    pNAMES = ZeroOrMore(pNAME)
    pNAMES.setParseAction(lambda result: [result])

    pINTEGER = Word("0123456789")
    pINTEGER.setParseAction(lambda result: EValue(VInteger(int(result[0]))))

    pBOOLEAN = Keyword("true") | Keyword("false")
    pBOOLEAN.setParseAction(lambda result: EValue(VBoolean(result[0]=="true")))

    pEXPR = Forward()

    pEXPRS = ZeroOrMore(pEXPR)
    pEXPRS.setParseAction(lambda result: [result])

    pIF = "(" + Keyword("if") + pEXPR + pEXPR + pEXPR + ")"
    pIF.setParseAction(lambda result: EIf(result[2],result[3],result[4]))

    pBINDING = "(" + pNAME + pEXPR + ")"
    pBINDING.setParseAction(lambda result: (result[1],result[2]))

    pBINDINGS = ZeroOrMore(pBINDING)
    pBINDINGS.setParseAction(lambda result: [ result ])

    def makeLet (bindings,body):
        params = [ param for (param,exp) in bindings ]
        args = [ exp for (param,exp) in bindings ]
        return ECall(EFunction(params,body),args)

    pLET = "(" + Keyword("let") + "(" + pBINDINGS + ")" + pEXPR + ")"
    pLET.setParseAction(lambda result: makeLet(result[3],result[5]))

    pCALL = "(" + pEXPR + pEXPRS + ")"
    pCALL.setParseAction(lambda result: ECall(result[1],result[2]))

    pFUN = "(" + Keyword("function") + "(" + pNAMES + ")" + pEXPR + ")"
    pFUN.setParseAction(lambda result: EFunction(result[3],result[5]))

    pFUNrec = "(" + Keyword("function") + pNAME + "(" + pNAMES + ")" + pEXPR + ")"
    pFUNrec.setParseAction(lambda result: EFunction(result[4],result[6],name=result[2]))

    def makeDo (exprs):
        result = exprs[-1]
        for e in reversed(exprs[:-1]):
            # space is not an allowed identifier in the syntax!
            result = makeLet([(" ",e)],result)
        return result

    pDO = "(" + Keyword("do") + pEXPRS + ")"
    pDO.setParseAction(lambda result: makeDo(result[2]))

    def makeWhile (cond,body):
        return makeLet([(" while",
                         EFunction([],EIf(cond,makeLet([(" ",body)],ECall(EId(" while"),[])),EValue(VNone())),name=" while"))],
                       ECall(EId(" while"),[]))

    pWHILE = "(" + Keyword("while") + pEXPR + pEXPR + ")"
    pWHILE.setParseAction(lambda result: makeWhile(result[2],result[3]))

    pEXPR << (pINTEGER | pBOOLEAN | pIDENTIFIER | pIF | pLET | pFUN | pFUNrec| pDO | pWHILE | pCALL)

    # can't attach a parse action to pEXPR because of recursion, so let's duplicate the parser
    pTOPEXPR = pEXPR.copy()
    pTOPEXPR.setParseAction(lambda result: {"result":"expression","expr":result[0]})

    pDEFINE = "(" + Keyword("define") + pNAME + pEXPR + ")"
    pDEFINE.setParseAction(lambda result: {"result":"value",
                                           "name":result[2],
                                           "expr":result[3]})

    pDEFUN = "(" + Keyword("defun") + pNAME + "(" + pNAMES + ")" + pEXPR + ")"
    pDEFUN.setParseAction(lambda result: {"result":"function",
                                          "name":result[2],
                                          "params":result[4],
                                          "body":result[6]})

    pABSTRACT = "#abs" + pEXPR
    pABSTRACT.setParseAction(lambda result: {"result":"abstract",
                                             "expr":result[1]})

    pQUIT = Keyword("#quit")
    pQUIT.setParseAction(lambda result: {"result":"quit"})
    
    pTOP = (pDEFUN | pDEFINE | pQUIT | pABSTRACT | pTOPEXPR)

    result = pTOP.parseString(input)[0]
    return result    # the first element of the result is the expression



def initial_env_cps ():
    env = []
    env = add_binding("+",
                      VClosure(["x","y","k"],
                               ECall(EId("k"),[EPrimCall(oper_plus,[EId("x"),EId("y")])]),
                               []),
                      env)
    env = add_binding("-",
                      VClosure(["x","y","k"],
                               ECall(EId("k"),[EPrimCall(oper_minus,[EId("x"),EId("y")])]),
                               []),
                      env)
    env = add_binding("*",
                      VClosure(["x","y","k"],
                               ECall(EId("k"),[EPrimCall(oper_times,[EId("x"),EId("y")])]),
                               []),
                      env)
    env = add_binding("zero?",
                      VClosure(["x","k"],
                               ECall(EId("k"),[EPrimCall(oper_zero,[EId("x")])]),
                               []),
                      env)
    env = add_binding("ref",
                      VClosure(["x","k"],
                               ECall(EId("k"),[EPrimCall(oper_ref, [EId("x")])]),
                               []),
                      env)
    env = add_binding("deref",
                      VClosure(["x","k"],
                               ECall(EId("k"),[EPrimCall(oper_deref, [EId("x")])]),
                               []),
                      env)
    env = add_binding("update!",
                      VClosure(["x","y","k"],
                               ECall(EId("k"),[EPrimCall(oper_update,[EId("x"),EId("y")])]),
                               []),
                      env)
    env = add_binding("print!",
                      VClosure(["x","k"],
                               ECall(EId("k"),[EPrimCall(oper_print,[EId("x")])]),
                               []),
                      env)
    return env




def shell_cps ():
    # A simple shell
    # Repeatedly read a line of input, parse it, and evaluate the result

    print "Lecture 8 - REF Language (defun, define, CPS)"
    print "#quit to quit, #abs to see abstract representation"
    env = initial_env_cps()
        
    while True:
        inp = raw_input("ref/cps> ")

        try:
            result = parse(inp)

            if result["result"] == "expression":
                exp = result["expr"]
                with Timer() as timer:
                    cps_exp = exp.cps(EFunction(["x"],EId("x")))
                    v = cps_exp.eval(env)
                    print "Eval time: {}s".format(round(timer.time(),3))
                print v

            elif result["result"] == "abstract":
                exp = result["expr"]
                cps_exp = exp.cps(EFunction(["x"],EId("x")))
                print cps_exp

            elif result["result"] == "quit":
                return

            elif result["result"] == "function":
                # the top-level environment is special, it is shared
                # amongst all the top-level closures so that all top-level
                # functions can refer to each other
                var = " _k_{}_".format(fresh())
                env.insert(0,(result["name"],VClosure([ p for p in result["params"]] + [var],
                                                      result["body"].cps(EId(var)),
                                                      env,
                                                      name=result["name"])))
                print "{} defined".format(result["name"])

            elif result["result"] == "value":
                exp = result["expr"]
                cps_exp = exp.cps(EFunction(["x"],EId("x")))
                v = cps_exp.eval(env)
                env.insert(0,(result["name"],v))
                print "{} defined".format(result["name"])
                
        except Exception as e:
            print "Exception: {}".format(e)


def add_binding (name,value,env):
    return env + [(name,value)]


def initial_env_compenv ():
    # In a compiled environment, we want the initial environment to be fixed
    # adding to the environment creates a new environment
    # previously defined functions cannot refer to later functions -- they
    # always refer to functions that existed when the function was defined

    env = []
    env = add_binding("+",
                      VClosure(["x","y","k"],
                               ECall(EIdIndex(2),[EPrimCall(oper_plus,[EIdIndex(0),EIdIndex(1)])]),
                               env),
                      env)
    # symtable = ["+"]
    env = add_binding("-",
                      VClosure(["x","y","k"],
                               ECall(EIdIndex(3),[EPrimCall(oper_minus,[EIdIndex(1),EIdIndex(2)])]),
                               env),
                      env)
    # symtable = ["+","-"]
    env = add_binding("*",
                      VClosure(["x","y","k"],
                               ECall(EIdIndex(4),[EPrimCall(oper_times,[EIdIndex(2),EIdIndex(3)])]),
                               env),
                      env)
    # symtable = ["+","-","*"]
    env = add_binding("zero?",
                      VClosure(["x","k"],
                               ECall(EIdIndex(4),[EPrimCall(oper_zero,[EIdIndex(3)])]),
                               env),
                      env)
    # symtable = ["+","-","*","zero?"]
    env = add_binding("ref",
                      VClosure(["x","k"],
                               ECall(EIdIndex(5),[EPrimCall(oper_ref, [EIdIndex(4)])]),
                               env),
                      env)
    # symtable = ["+","-","*","zero?","ref"]
    env = add_binding("deref",
                      VClosure(["x","k"],
                               ECall(EIdIndex(6),[EPrimCall(oper_deref, [EIdIndex(5)])]),
                               env),
                      env)
    # symtable = ["+","-","*","zero?","ref","deref"]
    env = add_binding("update!",
                      VClosure(["x","y","k"],
                               ECall(EIdIndex(8),[EPrimCall(oper_update,[EIdIndex(6),EIdIndex(7)])]),
                               env),
                      env)
    # symtable = ["+","-","*","zero?","ref","deref","update!"]
    env = add_binding("print!",
                      VClosure(["x","k"],
                               ECall(EIdIndex(8),[EPrimCall(oper_print,[EIdIndex(7)])]),
                               env),
                      env)
    return env


def shell_compenv ():
    # A simple shell
    # Repeatedly read a line of input, parse it, and evaluate the result

    print "Lecture 8 - REF Compiled Language (defun, define)"
    print "#quit to quit, #abs to see abstract representation"
    env = initial_env_compenv()
    symtable = [ name for (name,_) in env ]
        
    while True:
        inp = raw_input("ref/env> ")

        try:
            result = parse(inp)

            if result["result"] == "expression":
                exp = result["expr"]
                with Timer() as timer:
                    cps_exp = exp.cps(EFunction(["x"],EId("x")))
                    comp_exp = cps_exp.compile_env(symtable)
                    v = comp_exp.eval(env)
                    print "Eval time: {}s".format(round(timer.time(),3))
                print v

            elif result["result"] == "abstract":
                exp = result["expr"]
                cps_exp = exp.cps(EFunction(["x"],EId("x")))
                comp_exp = cps_exp.compile_env(symtable)
                print comp_exp

            elif result["result"] == "quit":
                return

            elif result["result"] == "function":
                var = " _k_{}_".format(fresh())
                body = result["body"].cps(EId(var))
                fun = EFunction([ p for p in result["params"]] + [var],
                                body,
                                name=result["name"])
                fun = fun.compile_env(symtable).eval(env)
                env = add_binding(result["name"],fun,env)
                symtable += [result["name"]]
                print "{} defined".format(result["name"])

            elif result["result"] == "value":
                exp = result["expr"]
                cps_exp = exp.cps(EFunction(["x"],EId("x")))
                v = cps_exp.compile_env(symtable).eval(env)
                env = add_binding(result["name"],v,env)
                symtable += [result["name"]]
                print "{} defined".format(result["name"])
                
        except Exception as e:
            print "Exception: {}".format(e)


            
# KEEP THIS IN SYNC WITH THE ENVIRONMENT IN shell_comp():
            
NUM_PRIMITIVES = 3   # the number of primitives in the environment
PRIMITIVES = [oper_plus,oper_minus,oper_zero]                       
            
def shell_comp ():

    print "Lecture 9 - REF Compiled Language (defun, define)"
    print "#quit to quit, #abs to see abstract representation and code"
    code = ["#start0","PUSH-ENV-ARGS","CLEAR-ARGS","LOOKUP",0,"PUSH-ARGS","LOOKUP",1,"PUSH-ARGS","PRIM-CALL",oper_plus,"CLEAR-ARGS","PUSH-ARGS","LOOKUP",2,"LOAD-ADDR-ENV","JUMP","#start16",
                "PUSH-ENV-ARGS","CLEAR-ARGS","LOOKUP",0,"PUSH-ARGS","LOOKUP",1,"PUSH-ARGS","PRIM-CALL",oper_minus,"CLEAR-ARGS","PUSH-ARGS","LOOKUP",2,"LOAD-ADDR-ENV","JUMP","#start32",
                "PUSH-ENV-ARGS","CLEAR-ARGS","LOOKUP",0,"PUSH-ARGS","PRIM-CALL",oper_zero,"CLEAR-ARGS","PUSH-ARGS","LOOKUP",1,"LOAD-ADDR-ENV","JUMP","#start45",
                "PUSH-ENV-ARGS","LOOKUP",0,"RETURN","#START_FUNC"]

    c_back = code

    symtable = [ "+" ,
                 "-",
                 "zero?",
                 "  K_DONE" ]  # special continuation that returns control to the shell
                                 
        
    while True:
        code = c_back
        inp = raw_input("ref/comp> ")

        try:
            result = parse(inp)

            if result["result"] == "expression":
                exp = result["expr"]
                with Timer() as timer:
                    # compile & execute:
                    # - convert to CPS
                    # - compile EId's to EIdIndex's
                    # - compile to register machine code
                    # - append to existing compiled code
                    # - execute newly compiled code
                    cps_exp = exp.cps(EId("  K_DONE"))
                    comp_exp = cps_exp.compile_env(symtable)
                    start = len(code)
                    c = comp_exp.compile()
                    code = code + c
                    #code = code+assemble(c,start)
                    assemble_c(code)
                    subprocess.call(["gcc","-O3","auto_build.c"])
                    subprocess.call(["./a.out"])
                    print "\n"
                    #v = execute(code,start,env)
                    print "Eval time: {}s".format(round(timer.time(),3))

            elif result["result"] == "abstract":
                exp = result["expr"]
                cps_exp = exp.cps(EId("  K_DONE"))
                comp_exp = cps_exp.compile_env(symtable)
                print comp_exp
                start = len(code)
                c = comp_exp.compile()
                print_code(c,start)

            elif result["result"] == "quit":
                return

            elif result["result"] == "function":
                fun = EFunction(result["params"],
                                result["body"],
                                name=result["name"])
                cps_fun = fun.cps(EId("  K_DONE"))
                comp_fun = cps_fun.compile_env(symtable)
                start = len(code)
                c = comp_fun.compile()
                code = code+assemble(c,start)
                v = execute(code,start,env)
                env = env + [v]
                symtable += [result["name"]]
                print "{} defined".format(result["name"])

            elif result["result"] == "value":
                exp = result["expr"]
                cps_exp = exp.cps(EId("  K_DONE"))
                comp_exp = cps_exp.compile_env(symtable)
                c = comp_exp.compile()
                start = len(code)
                code = code + assemble(c,start)
                v = execute(code,start,env)
                env = env + [v]
                symtable += [result["name"]]
                print "{} defined".format(result["name"])
                
        except Exception as e:
            print "Exception: {}".format(e)
            if not str(e).startswith("Runtime"):
                traceback.print_exc()



############################################################
# REGISTER MACHINE

CODE = {"RETURN":0,
        "CLEAR-ARGS":1,
        "LOAD":2,
        "PUSH-ARGS":3,
        "LOOKUP":4,
        "LOAD-ADDR-ENV":5,
        "JUMP":6,
        "PUSH-ENV-ARGS":7,
        "PUSH-ENV":8,
        "LOAD-ADDR":9,
        "LOAD-FUN":10,
        "PRIM-CALL":11,
        "JUMP-TRUE":12}


def assemble (code,addr):
    # CONVERT "assembly code" (instructions in text and labels in the code)
    # INTO "machine code" (instruction numbers and explicit addresses)
    

    # take a pass and get a final address for all labels
    labels = {}
    a = addr
    for (i,c) in enumerate(code):
        if type(c) is str and c.startswith("#"):
            labels[c[1:]] = a
        else:
            a += 1

    # take another pass to construct the final code
    # - transform operations into opcodes
    # - remove labels
    # - change address labels to underlying addresses

    result = []
    for c in code:
        if type(c) is str:
            if not c.startswith("#"):
                if c.startswith("@"):
                    result.append(labels[c[1:]])
                else:
                    result.append(CODE[c])
        else:
            result.append(c)

    return result


def assemble_c (code):
    # CONVERT "assembly code" (instructions in text and labels in the code)
    # INTO "machine code" (instruction numbers and explicit addresses)
    
    # take another pass to construct the final code
    # - transform operations into opcodes
    # - remove labels
    # - change address labels to underlying addresses


    index = 0
    with open("auto_build.c",'w') as t:
        t.write("#include <stdlib.h>\
                \n#include <stdio.h>\
                \n#define array_size 12\
                \n\
                \ntypedef struct tClosure{\
                \n    long long val;\
                \n    void* addr;\
                \n    int envLen;\
                \n    struct tClosure* p_env;\
                \n} tClosure;\
                \n\
                \nvoid* addr;\
                \n\
                \n//RESULT\
                \ntClosure result;\
                \n//ARGS\
                \ntClosure args[array_size];\
                \nint args_index = 0;\
                \n//ENV\
                \ntClosure env[array_size];\
                \nint env_index = 0;\
                \n\
                \nint i;\
                \n\
                \nlong long oper_plus(tClosure clo[]){\
                \n    return clo[0].val+clo[1].val;\
                \n}\
                \nlong long oper_minus(tClosure clo[]){\
                \n    return clo[0].val-clo[1].val;\
                \n}\
                \nlong long oper_times(tClosure clo[]){\
                \n    return clo[0].val*clo[1].val;\
                \n}\
                \nlong long oper_zero(tClosure clo[]){\
                \n    //true->1\
                \n    //false->0\
                \n    return clo[0].val==0;\
                \n}\
                \n\
                \nlong long func(){\
                \n    //Setup result\
                \n    result.val = -1;\
                \n    result.envLen = 0;\
                \n    result.p_env = (tClosure*)malloc(sizeof(tClosure)*array_size);\
                \n\
                \n    tClosure addr1;\
                \n    addr1.addr = &&PL_start0;\
                \n    addr1.envLen = 0;\
                \n    addr1.p_env = (tClosure*)malloc(sizeof(tClosure)*array_size);\
                \n    env[0] = addr1;\
                \n    env_index++;\
                \n\
                \n    tClosure addr2;\
                \n    addr2.addr = &&PL_start16;\
                \n    addr2.envLen = 0;\
                \n    addr2.p_env = (tClosure*)malloc(sizeof(tClosure)*array_size);\
                \n    env[1] = addr2;\
                \n    env_index++;\
                \n\
                \n    tClosure addr3;\
                \n    addr3.addr = &&PL_start32;\
                \n    addr3.envLen = 0;\
                \n    addr3.p_env = (tClosure*)malloc(sizeof(tClosure)*array_size);\
                \n    env[2] = addr3;\
                \n    env_index++;\
                \n\
                \n    tClosure addr4;\
                \n    addr4.addr = &&PL_start45;\
                \n    addr4.envLen = 0;\
                \n    addr4.p_env = (tClosure*)malloc(sizeof(tClosure)*array_size);\
                \n    env[3] = addr4;\
                \n    env_index++;\
                \n\
                \n    goto PL_START_FUNC;\n")

        while index<len(code):
            op = code[index]
            if type(op) is str:
                if op.startswith("#"):
                    t.write("\n")
                    t.write("    PL_{}:\n".format(op[1:]))
                    index +=1

                elif op == "RETURN":
                    t.write("\n")
                    t.write("    return result.val;\n")
                    index += 1

                elif op == "CLEAR-ARGS":
                    t.write("\n")
                    t.write("    args_index = 0;\n")
                    index+=1

                elif op == "LOAD":
                    t.write("\n")
                    t.write("    result.val = {};\n  ".format(code[index+1].value))
                    index += 2
                          
                elif op == "PUSH-ARGS":
                    t.write("\n")
                    t.write("    args[args_index] = result;\n    args_index++;\n")
                    index += 1

                elif op == "LOOKUP":
                    t.write("\n")
                    t.write("    result = env[{}];\n".format(code[index+1]))
                    index += 2

                elif op == "LOAD-ADDR-ENV":
                    t.write("\n")
                    t.write("    addr = result.addr;\
                            \n    memcpy(env,result.p_env,result.envLen*sizeof(tClosure));\
                            \n    env_index = result.envLen;\n")                     
                    index += 1

                elif op == "JUMP":
                    t.write("\n")
                    t.write("    goto *addr;\n")
                    index += 1
                          
                elif op == "PUSH-ENV-ARGS":
                    t.write("\n")
                    t.write("    for (i=0;i<args_index;i++){\
                            \n        env[env_index] = args[i];\
                            \n        env_index++;\
                            \n    }\n")
                    index += 1
                  
                elif op == "PUSH-ENV":
                    t.write("\n")
                    t.write("    env[env_index]=result;\n    env_index++;\n")
                    index += 1

                elif op == "LOAD-ADDR":
                    t.write("\n")
                    t.write("    addr = &&PL_{};\n".format(code[index+1][1:]))
                    index += 2

                elif op == "LOAD-FUN":
                    t.write("\n")
                    t.write("    result.addr = addr;\
                            \n    memcpy(result.p_env,env,env_index*sizeof(tClosure));\
                            \n    result.envLen = env_index;\n")
                    index += 1

                elif op == "PRIM-CALL":
                    t.write("\n")
                    t.write("    result.val = {}(args);\n".format(code[index+1].__name__))
                    index += 2

                elif op == "JUMP-TRUE":
                    t.write("\n")
                    t.write("    if(result.val==1){\n        goto *addr;\n    }\n")
                    index += 1

                else:
                    raise Exception("Unrecognized opcode: {}".format(op))

        t.write("}\n\nint main(){\n    printf(\"Answer: %lli\",func());\n    return 0;\n}\n")
    print("File Created!")
    return

def execute (code,start_pc,start_env):
    result = VNone()
    args = []
    pc = start_pc
    addr = start_pc
    env = start_env

    while True:

        op = code[pc]
        #print "pc = {} [{}] addr = {} result = {}".format(pc,decode(op),addr,result)
        #print "  args = {}".format([ str(a) for a in args])
        #print "  env = {}".format([ str(e) for e in env])
        
        if op == 0: # "RETURN":
            return result

        elif op == 1: #"CLEAR-ARGS":
            args = []
            pc += 1

        elif op == 2: #"LOAD":
            result = code[pc+1]
            pc += 2
            
        elif op == 3: #"PUSH-ARGS":
            args = args + [result]
            pc += 1

        elif op == 4: #"LOOKUP":
            result = env[code[pc+1]]
            pc += 2

        elif op == 5: #"LOAD-ADDR-ENV":
            addr = result._addr
            env = result._env
            pc += 1

        elif op == 6: #"JUMP":
            pc = addr
            
        elif op == 7: #"PUSH-ENV-ARGS":
            env = env + args
            pc += 1
    
        elif op == 8: #"PUSH-ENV":
            env = env + [result]
            pc += 1

        elif op == 9: #"LOAD-ADDR":
            addr = code[pc+1]
            pc += 2

        elif op == 10: #"LOAD-FUN":
            result = VClosureAddr(addr,env)
            pc += 1

        elif op == 11: #"PRIM-CALL":
            # print [ str(a) for a in args ]
            oper = code[pc+1]
            result = apply(oper,args)
            pc += 2

        elif op == 12: #"JUMP-TRUE":
            if result.value:
                pc = addr
            else:
                pc += 1

        else:
            raise Exception("Unrecognized opcode: {}".format(op))


#######################################################################################
####################################### Code_C ########################################
#######################################################################################
#       RETURN:
#             return result.val;
#
#       LOAD:
#       n:
#             result.val = n;
#             result.isInt = 1;
#
#       LOAD-ADDR:
#       label:
#             addr = &&label;
#
#       LOOKUP:
#       env-index:
#             result = env[env-index];
#
#       CLEAR-ARGS:
#             args_index = 0;
#
#       PUSH-ARGS:
#             args[args_index] = result;
#             args_index++;
#
#       PRIM-CALL:
#       oper:
#             result.val = oper(args);
#             result.isInt = 1;
#
#       PUSH-ENV:
#             tClosure* temp_env = realloc(env,sizeof(env)+sizeof(result));
#             env = temp_env;
#             env[env_index]=result;
#             env_index++;
#
#       PUSH-ENV-ARGS:
#             temp_env = realloc(env,sizeof(env)+sizeof(args));
#             env = temp_env;
#             if(args_index>=1){
#                   env[env_index]=args[0];
#                   env_index++;
#             }
#             if(args_index==2){
#                   env[env_index]=args[1];
#                   env_index++;
#             }
#     
#       JUMP:
#             goto addr;
#
#       JUMP-TRUE:
#             if(result.val==1){
#                   goto addr;
#             }
#
#       LOAD-FUN:
#             result.addr = addr;
#             result.envLen = sizeof(env)/sizeof(tClosure);
#             result.p_env = env;
#
#       LOAD-ADDR-ENV:
#             addr = result.addr;
#             env = (tClosure *)malloc(sizeof(tClosure)*result.envLen);
#             env = result.p_env;
#
#######################################################################################
#######################################################################################

def print_code (c,start):

    
    for (i,x) in enumerate(c):
        print " {:04}  {}".format(start+i,x)


def decode (c):

    for k in CODE:
        if CODE[k] == c:
            return k

shell_comp()
