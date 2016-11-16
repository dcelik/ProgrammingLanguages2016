############################################################
# Simple imperative language
# C-like surface syntac
# with S-expression syntax for expressions
# (no recursive closures)
#

############################################################
# HOMEWORK 7
#
# Team members: Deniz Celik, Jacob Riedel
#
# Emails: deniz.celik@students.olin.edu
#         jacob.riedel@students.olin.edu
#

import sys, copy

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

class ERefCell (Exp):
    # this could (should) be turned into a primitive
    # operation.  (WHY?)

    def __init__ (self,initialExp):
        self._initial = initialExp

    def __str__ (self):
        return "ERefCell({})".format(str(self._initial))

    def eval (self,env):
        v = self._initial.eval(env)
        return VRefCell(v)


class EAnd (Exp):

    def __init__ (self,e1,e2):
        self._exp1 = e1
        self._exp2 = e2

    def __str__ (self):
        return "EAnd({},{})".format(self._exp1,self._exp2)

    def eval (self,env):
        v1 = self._exp1.eval(env)
        if v1.type == "boolean" and not v1.value:
            # short circuit
            return VBoolean(False)
        v2 = self._exp2.eval(env)
        return oper_and(v1,v2)

class EOr (Exp):

    def __init__ (self,e1,e2):
        self._exp1 = e1
        self._exp2 = e2

    def __str__ (self):
        return "EOr({},{})".format(self._exp1,self._exp2)

    def eval (self,env):
        v1 = self._exp1.eval(env)
        if v1.type == "boolean" and v1.value:
            # short circuit
            return VBoolean(True)
        v2 = self._exp2.eval(env)
        return oper_or(v1,v2)

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


class ELet (Exp):
    # local binding
    # allow multiple bindings
    # eager (call-by-value)

    def __init__ (self,bindings,e2):
        self._bindings = bindings
        self._e2 = e2

    def __str__ (self):
        return "ELet([{}],{})".format(",".join([ "({},{})".format(id,str(exp)) for (id,exp) in self._bindings ]),self._e2)

    def eval (self,env):
        new_env = [ (id,e.eval(env)) for (id,e) in self._bindings] + env
        return self._e2.eval(new_env)

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

    def __init__ (self,fun,exps):
        self._fun = fun
        self._args = exps

    def __str__ (self):
        return "ECall({},[{}])".format(str(self._fun),",".join(str(e) for e in self._args))

    def eval (self,env):
        f = self._fun.eval(env)
        if f.type != "function":
            raise Exception("Runtime error: trying to call a non-function")
        args = [ e.eval(env) for e in self._args]
        if len(args) != len(f.params):
            raise Exception("Runtime error: argument # mismatch in call")
        new_env = zip(f.params,args) + f.env
        return f.body.eval(new_env)

class EFunction (Exp):
    # Creates an anonymous function

    def __init__ (self,params,body,name=None):
        self._params = params
        self._body = body
        self._name = name

    def __str__ (self):
        return "EFunction([{}],{})".format(",".join(self._params),str(self._body))

    def eval (self,env):
        return VClosure(self._params,self._body,env,self._name)

class EDo (Exp):

    def __init__ (self,exps):
        self._exps = exps

    def __str__ (self):
        return "EDo([{}])".format(",".join(str(e) for e in self._exps))

    def eval (self,env):
        # default return value for do when no arguments
        v = VNone()
        for e in self._exps:
            v = e.eval(env)
        return v

class EWhile (Exp):

    def __init__ (self,cond,exp):
        self._cond = cond
        self._exp = exp

    def __str__ (self):
        return "EWhile({},{})".format(str(self._cond),str(self._exp))

    def eval (self,env): 
        c = self._cond.eval(env)
        if c.type != "boolean":
            raise Exception ("Runtime error: while condition not a Boolean")
        
        raw_exp = copy.deepcopy(self._exp)
        while c.value:
            raw_exp.eval(env)
            c = self._cond.eval(env)
            if c.type != "boolean":
                raise Exception ("Runtime error: while condition not a Boolean")
            raw_exp = copy.deepcopy(self._exp)
        return VNone()

class EFor(Exp):

    def __init__(self,iterator,array,exp):
        self._iter = iterator
        self._array = array
        self._exp = exp

    def __str__ (self):
        return "EFor({} in {},{})".format(str(self._iter),str(self._array),str(self._exp))

    def eval (self,env):
        arr = self._array.eval(env).value
        raw_exp = copy.deepcopy(self._exp)
        for x in arr:
            new_env = [(self._iter,VRefCell(x))] + env
            raw_exp.eval(new_env)
            raw_exp = copy.deepcopy(self._exp)
            #self._exp.eval(new_env)
        return VNone()

class EArray(Exp):
    def __init__(self,lst):
        self._arr = lst

    def __str__ (self):
        return "EArray([{}])".format(",".join(str(v) for v in self._arr))

    def eval (self,env):
        for i in xrange(len(self._arr)):
            temp = self._arr[i]
            if type(temp) != EValue:
                eval = temp.eval(env)
                if type(eval) != EValue:
                    self._arr[i] = EValue(eval)
                else: 
                    self._arr[i] = eval
        return VArray(self._arr)

class EDict(Exp):
    def __init__(self,dic):
        self._dict = dic

    def __str__ (self):
        return "EDict({})".format(",".join(str(k)+":"+str(v) for (k,v) in self._dict.items()))

    def eval (self,env):
        return VDict(self._dict)

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

class VRefCell (Value):

    def __init__ (self,initial):
        self.content = initial
        self.type = "ref"

    def __str__ (self):
        return "<ref {}>".format(str(self.content))

class VClosure (Value):
    
    def __init__ (self,params,body,env,name=None):
        self.params = params
        self.body = body
        extra = [(name,VRefCell(self))] if name else []
        self.env = extra + env
        self.type = "function"

    def __str__ (self):
        return "<function [{}] {}>".format(",".join(self.params),str(self.body))

    def apply (self,args):
        if len(args) != len(self.params):
            raise Exception("Runtime error: argument # mismatch in call")
        new_env = zip(self.params,args) + self.env
        return self.body.eval(new_env)

class VNone (Value):

    def __init__ (self):
        self.type = "none"

    def __str__ (self):
        return "none"

class VString (Value):

    def __init__ (self,value):
        self.value = value
        self.type = "string"

    def __str__ (self):
        return self.value

class VArray(Value):
    def __init__(self, array):
        self.type = "array"
        self._len = len(array)
        self.value = array

    def __str__ (self):
        return "<array [{}]>".format(",".join(str(v) for v in self.value))

class VDict(Value):
    def __init__(self, dic):
        self.type = "dict"
        self.value = dic

    def __str__ (self):
        return "<dict {} >".format("{" + ", ".join(str(k)+" : "+str(v) for (k,v) in self.value.items()) + "}")

# Primitive operations

def oper_plus (v1,v2): 
    if type(v1) == EValue:
        v1 = v1._value
    if type(v2) == EValue:
        v2 = v2._value
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value + v2.value)
    if v1.type == "array" and v2.type == "array":
        return VArray(v1.value + v2.value)
    if v1.type == "string" and v2.type == "string":
        return VString(v1.value + v2.value)
    raise Exception ("Runtime error: trying to apply '+' to non-numbers, non-arrays or non-strings")

def oper_minus (v1,v2):
    if type(v1) == EValue:
        v1 = v1._value
    if type(v2) == EValue:
        v2 = v2._value
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value - v2.value)
    raise Exception ("Runtime error: trying to subtract non-numbers")

def oper_times (v1,v2):
    if type(v1) == EValue:
        v1 = v1._value
    if type(v2) == EValue:
        v2 = v2._value
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value * v2.value)
    raise Exception ("Runtime error: trying to multiply non-numbers")

def oper_zero (v1):
    if v1.type == "integer":
        return VBoolean(v1.value==0)
    raise Exception ("Runtime error: type error in zero?")

def oper_deref (v1):
    if v1.type == "ref":
        return v1.content
    raise Exception ("Runtime error: dereferencing a non-reference value")

def oper_update (v1,v2):
    if v1.type == "ref":
        v1.content = v2
        return VNone()
    raise Exception ("Runtime error: updating a non-reference value")
 
def oper_print (v1,*args):
    print v1,
    for i in args:
        print ",", 
        print i,
    print
    return VNone()

def oper_not (v1):
    if v1.type == "boolean":
        return VBoolean(not v1.value)
    raise Exception ("Runtime error: type error in not")

def oper_greater (v1,v2):
    if (v1.type == "integer" and v2.type == "integer") or (v1.type == "string" and v2.type == "string"):
        return VBoolean(v1.value>v2.value)
    raise Exception ("Runtime error: type error in >")

def oper_greater_equal (v1,v2):
    if (v1.type == "integer" and v2.type == "integer") or (v1.type == "string" and v2.type == "string"):
        return VBoolean(v1.value>=v2.value)
    raise Exception ("Runtime error: type error in >=")

def oper_less (v1,v2):
    if (v1.type == "integer" and v2.type == "integer") or (v1.type == "string" and v2.type == "string"):
        return VBoolean(v1.value<v2.value)
    raise Exception ("Runtime error: type error in <") 

def oper_less_equal (v1,v2):
    if (v1.type == "integer" and v2.type == "integer") or (v1.type == "string" and v2.type == "string"):
        return VBoolean(v1.value<=v2.value)
    raise Exception ("Runtime error: type error in <=")

def oper_equal (v1,v2):
    return VBoolean(v1.value==v2.value)

def oper_not_equal (v1,v2):
    return VBoolean(v1.value!=v2.value)

def oper_and (v1,v2):
    if v1.type == "boolean" and v2.type == "boolean":
        return VBoolean(v1.value and v2.value)
    raise Exception("Runtime error: wrong types for AND ({} and {})".format(v1.type,v2.type))

def oper_or (v1,v2):
    if v1.type == "boolean" and v2.type == "boolean":
        return VBoolean(v1.value or v2.value)
    raise Exception("Runtime error: wrong types for OR ({} and {})".format(v1.type,v2.type))

def oper_len(obj):
    if obj.type == "string" or obj.type == "array":
        return VInteger(len(obj.value))
    raise Exception ("Runtime error: trying to get length of non-string or non-array")

def oper_index(obj,ind):
    if (obj.type == "array" or obj.type == "string") and (ind.type == "integer"):
        return obj.value[ind.value]
    if obj.type == "dict" and (ind.type == "integer" or ind.type == "string" or ind.type == "boolean"):
        return obj.value[ind.value]
    raise Exception ("Runtime error: trying to get value in non-array, non-dict, or non-string, or using a non-integer index")

def oper_obj_update(obj,ind,val):
    if obj.type == "array" and ind.type == "integer":
        obj.value[ind.value] = EValue(val)
        return VNone()
    if obj.type == "dict" and (ind.type == "integer" or ind.type == "boolean" or ind.type == "string"):
        obj.value[ind.value] = EValue(val)
        return VNone()
    raise Exception ("Runtime error: trying to update value in non-array or with non-integer index")

############################################################
# IMPERATIVE SURFACE SYNTAX
#

##
## PARSER
##
# cf http://pyparsing.wikispaces.com/

from pyparsing import Word, Literal, ZeroOrMore, OneOrMore, Keyword, Forward, alphas, alphanums, NoMatch
from pyparsing import Group, QuotedString, Optional, Suppress, NotAny, FollowedBy, StringEnd, Empty


def initial_env ():
    # A sneaky way to allow functions to refer to functions that are not
    # yet defined at top level, or recursive functions
    env = []
    env.insert(0,
               ("len",
                VRefCell(VClosure(["x"],
                                  EPrimCall(oper_len,[EId("x")]),
                                  env))))
    return env

def parse (input):
    # parse a string into an element of the abstract representation

    # Grammar:
    #
    # <expr> ::= <integer>
    #            true
    #            false
    #            <identifier>
    #            ( if <expr> <expr> <expr> )
    #            ( function ( <name ... ) <expr> )    
    #            ( <expr> <expr> ... )
    #
    # <decl> ::= var name = expr ; 
    #
    # <stmt> ::= if <expr> <stmt> else <stmt>
    #            while <expr> <stmt>
    #            name <- <expr> ;
    #            print <expr> ;
    #            <block>
    #            for ( name <- <expr> ; <name> <expr> <expr> ; <name> = <expr> <expr> <expr> ) <block>
    #
    # <block> ::= { <decl> ... <stmt> ... }
    #
    # <toplevel> ::= <decl>
    #                <stmt>
    #


    #idChars = alphas+"_+*-?!=<>"
    idChars = alphas+"_"

    pIDENTIFIER = Word(idChars, idChars+"0123456789")
    pIDENTIFIER.setParseAction(lambda result: EPrimCall(oper_deref,[EId(result[0])]))

    # A name is like an identifier but it does not return an EId...
    pNAME = Word(idChars,idChars+"0123456789")

    pSTRING = QuotedString('"',escChar='\\')
    pSTRING.setParseAction(lambda result: EValue(VString(result[0])))

    pNAMES = ZeroOrMore(pNAME)
    pNAMES.setParseAction(lambda result: [result])

    pINTEGER = Word("0123456789")
    pINTEGER.setParseAction(lambda result: EValue(VInteger(int(result[0]))))

    pBOOLEAN = Keyword("true") | Keyword("false")
    pBOOLEAN.setParseAction(lambda result: EValue(VBoolean(result[0]=="true")))

    pEXPR = Forward()

    pEXPR_PAREN = "(" + pEXPR + ")"
    pEXPR_PAREN.setParseAction(lambda result: result[1])

    pNOT = Keyword("not") + pEXPR
    pNOT.setParseAction(lambda result: EPrimCall(oper_not, result[1]))

    def parse_let(result):
        bindings = [(result[2],ERefCell(result[4]))]
        for vs in result[5]:
            bindings.append((vs[0],ERefCell(vs[2])))
        return ELet(bindings,result[7])

    pLET = Keyword("let") + "(" + pNAME + "=" + pEXPR + Group(ZeroOrMore( Suppress(",") + Group(pNAME + "=" + pEXPR) ))+ ")" + pEXPR
    pLET.setParseAction(parse_let)

    def parse_dict(result):
        vals = {result[1][0]:result[1][2]}
        for b in result[2]:
            vals[b[0]]=b[2]
        return EDict(vals)

    pDICT = "{" + Group(Optional(pNAME + ":" + pEXPR)) + Group(ZeroOrMore(Group(Suppress(",") + pNAME + ":" + pEXPR))) + "}"
    pDICT.setParseAction(parse_dict)

    pARRAY = "[" + Group(Optional(pEXPR) + ZeroOrMore(Suppress(",") + pEXPR)) + "]"
    pARRAY.setParseAction(lambda result: EArray(result[1]))

    pBODY = Forward()

    def mkFunBody (params,body):
        bindings = [ (p,ERefCell(EId(p))) for p in params ]
        return ELet(bindings,body)

    pFUN = Keyword("fun") + "(" + Group(Optional(pNAME) + ZeroOrMore(Suppress(",") + pNAME)) + ")" + pBODY
    pFUN.setParseAction(lambda result: EFunction(result[2],mkFunBody(result[2],result[4])))

    pFUN_REC = Keyword("fun") + pNAME + "(" + Group(Optional(pNAME) + ZeroOrMore(Suppress(",") + pNAME)) + ")" + pBODY
    pFUN_REC.setParseAction(lambda result: EFunction(result[3],mkFunBody(result[3],result[5]),name=result[1]))

    # left-recursive fix parser
    pADD = "+" + pEXPR
    pADD.setParseAction(lambda result: (oper_plus, result[1]))

    pSUB = "-" + pEXPR
    pSUB.setParseAction(lambda result: (oper_minus, result[1]))

    pMUL = "*" + pEXPR
    pMUL.setParseAction(lambda result: (oper_times, result[1]))

    pAND = "and" + pEXPR
    pAND.setParseAction(lambda result: ("ADD", result[1]))

    pOR = "or" + pEXPR
    pOR.setParseAction(lambda result: ("OR", result[1]))

    pGTR = ">" + pEXPR
    pGTR.setParseAction(lambda result: (oper_greater, result[1]))

    pGTR_EQ = ">=" + pEXPR
    pGTR_EQ.setParseAction(lambda result: (oper_greater_equal, result[1]))

    pLSS = "<" + pEXPR
    pLSS.setParseAction(lambda result: (oper_less, result[1]))

    pLSS_EQ = "<=" + pEXPR
    pLSS_EQ.setParseAction(lambda result: (oper_less_equal, result[1]))

    pEQ = "==" + pEXPR
    pEQ.setParseAction(lambda result: (oper_equal, result[1]))

    pNOT_EQ = "<> " + pEXPR
    pNOT_EQ.setParseAction(lambda result: (oper_not_equal, result[1]))

    pCOND = "?" + pEXPR + ":" + pEXPR
    pCOND.setParseAction(lambda result: ("COND", result[1], result[3]))

    pCALL = "(" + Group(Optional(pEXPR) + ZeroOrMore(Suppress(",") + pEXPR)) + ")"
    pCALL.setParseAction(lambda result: ("CALL", result[1]))

    pACCESS = "[" + pEXPR + "]" + NotAny("=")
    pACCESS.setParseAction(lambda result: (oper_index, result[1]))

    def finalparse(result):
        if result[1][0] == "AND":
            return EAnd(result[0],result[1][1])
        if result[1][0] == "OR":
            return EOr(result[0],result[1][1])
        if result[1][0] == "COND":
            return EIf(result[0],result[1][1],result[1][2])
        if result[1][0] == "CALL":
            return ECall(result[0],result[1][1])
        return EPrimCall(result[1][0],[result[0],result[1][1]]) 

    pNON_FINAL = (pINTEGER | pBOOLEAN | pSTRING |  pNOT | pLET | pEXPR_PAREN | pARRAY | pFUN_REC | pFUN | pDICT | pIDENTIFIER)

    pFINAL = pNON_FINAL + (pMUL | pADD | pSUB | pGTR_EQ | pGTR | pLSS_EQ | pLSS | pEQ | pNOT_EQ | pAND | pOR | pCOND | pCALL | pACCESS)
    pFINAL.setParseAction(finalparse)

    pEXPR << ( pFINAL | pINTEGER | pBOOLEAN | pSTRING |  pNOT | pLET | pEXPR_PAREN | pARRAY | pFUN_REC | pFUN | pDICT | pIDENTIFIER )

    pDECL_VAR = Keyword("var") + pNAME + ";"
    pDECL_VAR.setParseAction(lambda result: (result[1],EValue(VNone())))

    pDECL_VAR_INST = Keyword("var") + pNAME + "=" + pEXPR + ";"
    pDECL_VAR_INST.setParseAction(lambda result: (result[1],result[3]))

    pDEF = Keyword("def") + pNAME + "(" + Group(Optional(pNAME) + ZeroOrMore(Suppress(",") + pNAME)) + ")" + pBODY 
    pDEF.setParseAction(lambda result: (result[1], EFunction(result[3],mkFunBody(result[3],result[5]),name=result[1])))

    pDECL = (pDECL_VAR | pDECL_VAR_INST | pDEF)

    pSTMT_EVAL = pEXPR + ";"
    pSTMT_EVAL.setParseAction(lambda result: result[0])

    pSTMT_VAR = pNAME + "=" + pEXPR + ";"
    pSTMT_VAR.setParseAction(lambda result: EPrimCall(oper_update,[EId(result[0]),result[2]]))

    pSTMT_PRINT = Keyword("print") + Group(pEXPR + ZeroOrMore(Suppress(",") + pEXPR)) + ";"
    pSTMT_PRINT.setParseAction(lambda result: EPrimCall(oper_print,result[1]))

    pSTMT_ASSIGN = pEXPR + "[" + pEXPR + "]" + "=" + pEXPR + ";"
    pSTMT_ASSIGN.setParseAction(lambda result: EPrimCall(oper_obj_update,[result[0],result[2],result[5]]))

    pSTMT_COND = "if" + pEXPR + pBODY
    pSTMT_COND.setParseAction(lambda result: EIf(result[1],result[2],EValue(VBoolean(True))))

    pSTMT_COND_ELSE = "if" + pEXPR + pBODY + "else" + pBODY
    pSTMT_COND_ELSE.setParseAction(lambda result: EIf(result[1],result[2],result[4]))

    pSTMT_WHILE = Keyword("while") + pEXPR + pBODY
    pSTMT_WHILE.setParseAction(lambda result: EWhile(result[1],result[2]))

    # def parse_for(result):
    #     init = result[2]
    #     cond = ECall(EPrimCall(oper_deref,[EId(result[3][1])]),[result[3][0],result[3][2]])

    #     if result[3][1] == "!=":
    #         cond = ECall(EPrimCall(oper_deref,[EId("not")]),[ECall(EPrimCall(oper_deref,[EId("zero?")]),[ECall(EPrimCall(oper_deref,[EId("-")]),[result[3][0],result[3][2]])])])

    #     mod = EPrimCall(oper_update,[EId(result[5]),ECall(result[8],[result[7],result[9]])])
    #     return EFor(init,cond,mod,result[11])

    # pSTMT_FOR = Keyword("for") + "(" + pSTMT_UPDATE + Group(pEXPR + pNAME + pEXPR) + ";" + pNAME + "=" + pEXPR + pEXPR + pEXPR + ")"+ pSTMT_BLOCK
    # pSTMT_FOR.setParseAction(parse_for)

    pSTMT_FOR = Keyword("for") + "(" + pNAME + Keyword("in") + pEXPR + ")" + pBODY
    pSTMT_FOR.setParseAction(lambda result: EFor(result[2],result[4],result[6]))

    pSTMT = (pSTMT_EVAL | pSTMT_VAR | pSTMT_PRINT | pSTMT_ASSIGN | pSTMT_COND_ELSE | pSTMT_COND | pSTMT_WHILE | pSTMT_FOR)

    def mkBlock (decls,stmts):
        bindings = [ (n,ERefCell(expr)) for (n,expr) in decls ]
        return ELet(bindings,EDo(stmts))

    pBODY << "{" + Group(ZeroOrMore(pDECL)) + Group(ZeroOrMore(pSTMT)) + "}"
    pBODY.setParseAction(lambda result: mkBlock(result[1],result[2]))

    # pEXPRS = ZeroOrMore(pEXPR)
    # pEXPRS.setParseAction(lambda result: [result])

    # pIF = "(" + Keyword("if") + pEXPR + pEXPR + pEXPR + ")"
    # pIF.setParseAction(lambda result: EIf(result[2],result[3],result[4]))

    # def mkFunBody (params,body):
    #     bindings = [ (p,ERefCell(EId(p))) for p in params ]
    #     return ELet(bindings,body)

    # pFUN = "(" + Keyword("function") + "(" + pNAMES + ")" + pEXPR + ")"
    # pFUN.setParseAction(lambda result: EFunction(result[3],mkFunBody(result[3],result[5])))

    # pARRAY = "(" + Keyword("new-array") + pEXPR + ")"
    # pARRAY.setParseAction(lambda result:EArray(result[2]))

    # pWITH = "(" + Keyword("with") + pEXPR + pEXPR + ")"
    # pWITH.setParseAction(lambda result: EWithObj(result[2],result[3]))
    
    # pCALL = "(" + pEXPR + pEXPRS + ")"
    # pCALL.setParseAction(lambda result: ECall(result[1],result[2]))

    # pEXPR << (pINTEGER | pBOOLEAN | pSTRING | pARRAY | pWITH | pIDENTIFIER | pIF | pFUN | pCALL)

    # pSTMT = Forward()

    # pDECL_VAR = "var" + pNAME + "=" + pEXPR + ";"
    # pDECL_VAR.setParseAction(lambda result: (result[1],result[3]))

    # pDECL_PROC = Keyword("procedure") + pNAME + "(" + pNAMES + ")" + pSTMT
    # pDECL_PROC.setParseAction(lambda result: (result[1], EFunction(result[3], mkFunBody(result[3],result[5]))))

    # # hack to get pDECL to match only pDECL_VAR (but still leave room
    # # to add to pDECL later)
    # pDECL = ( pDECL_PROC | pDECL_VAR | NoMatch() )

    # pDECLS = ZeroOrMore(pDECL)
    # pDECLS.setParseAction(lambda result: [result])

    # pSTMT_IF_1 = "if" + pEXPR + pSTMT + "else" + pSTMT
    # pSTMT_IF_1.setParseAction(lambda result: EIf(result[1],result[2],result[4]))

    # pSTMT_IF_2 = "if" + pEXPR + pSTMT
    # pSTMT_IF_2.setParseAction(lambda result: EIf(result[1],result[2],EValue(VBoolean(True))))
   
    # pSTMT_WHILE = "while" + pEXPR + pSTMT
    # pSTMT_WHILE.setParseAction(lambda result: EWhile(result[1],result[2]))

    # pSTMT_PRINT = "print" + pEXPR + ";"
    # pSTMT_PRINT.setParseAction(lambda result: EPrimCall(oper_print,[result[1]]));

    # pSTMT_UPDATE = pNAME + "<-" + pEXPR + ";"
    # pSTMT_UPDATE.setParseAction(lambda result: EPrimCall(oper_update,[EId(result[0]),result[2]]))

    # pSTMT_UPDATE_ARR = pEXPR + "[" + pEXPR + "]" + "<-" + pEXPR + ";"
    # pSTMT_UPDATE_ARR.setParseAction(lambda result:EPrimCall(arr_oper_update,[result[0],result[2],result[5]]))

    # pSTMT_PROC = pEXPR + "(" + pEXPRS + ")" + ";"
    # pSTMT_PROC.setParseAction(lambda result: ECall(result[0],result[2]))

    # pSTMTS = ZeroOrMore(pSTMT)
    # pSTMTS.setParseAction(lambda result: [result])

    # def mkBlock (decls,stmts):
    #     bindings = [ (n,ERefCell(expr)) for (n,expr) in decls ]
    #     return ELet(bindings,EDo(stmts))
        
    # pSTMT_BLOCK = "{" + pDECLS + pSTMTS + "}"
    # pSTMT_BLOCK.setParseAction(lambda result: mkBlock(result[1],result[2]))

    # def parse_for(result):
    #     init = result[2]
    #     cond = ECall(EPrimCall(oper_deref,[EId(result[3][1])]),[result[3][0],result[3][2]])

    #     if result[3][1] == "!=":
    #         cond = ECall(EPrimCall(oper_deref,[EId("not")]),[ECall(EPrimCall(oper_deref,[EId("zero?")]),[ECall(EPrimCall(oper_deref,[EId("-")]),[result[3][0],result[3][2]])])])

    #     mod = EPrimCall(oper_update,[EId(result[5]),ECall(result[8],[result[7],result[9]])])
    #     return EFor(init,cond,mod,result[11])

    # pSTMT_FOR = Keyword("for") + "(" + pSTMT_UPDATE + Group(pEXPR + pNAME + pEXPR) + ";" + pNAME + "=" + pEXPR + pEXPR + pEXPR + ")"+ pSTMT_BLOCK
    # pSTMT_FOR.setParseAction(parse_for)
    
    # pSTMT << ( pSTMT_IF_1 | pSTMT_IF_2 | pSTMT_WHILE | pSTMT_PRINT | pSTMT_UPDATE_ARR | pSTMT_UPDATE |  pSTMT_BLOCK | pSTMT_FOR | pSTMT_PROC)


    # can't attach a parse action to pSTMT because of recursion, so let's duplicate the parser
    pTOP_STMT = pSTMT.copy()
    pTOP_STMT.setParseAction(lambda result: {"result":"statement",
                                             "stmt":result[0]})


    pTOP_DECL = pDECL.copy()
    pTOP_DECL.setParseAction(lambda result: {"result":"declaration",
                                             "decl":result[0]})

    #pABSTRACT = "#abs" + pSTMT
    #pABSTRACT.setParseAction(lambda result: {"result":"abstract",
    #                                         "stmt":result[1]})

    #pQUIT = Keyword("#quit")
    #pQUIT.setParseAction(lambda result: {"result":"quit"})
    
    #pTOP = (pQUIT | pABSTRACT | pTOP_DECL | pTOP_STMT )

    pTOP = OneOrMore(pTOP_DECL | pTOP_STMT) #+ FollowedBy(StringEnd())

    return pTOP
    result = pTOP.parseString(input)[0]
    return result    # the first element of the result is the expression

def parse_test():

    idChars = alphas+"_"

    pIDENTIFIER = Word(idChars, idChars+"0123456789")
    pIDENTIFIER.setParseAction(lambda result: EPrimCall(oper_deref,[EId(result[0])]))

    # A name is like an identifier but it does not return an EId...
    pNAME = Word(idChars,idChars+"0123456789")

    pSTRING = QuotedString('"',escChar='\\')
    pSTRING.setParseAction(lambda result: EValue(VString(result[0])))

    pNAMES = ZeroOrMore(pNAME)
    pNAMES.setParseAction(lambda result: [result])

    pINTEGER = Word("0123456789")
    pINTEGER.setParseAction(lambda result: EValue(VInteger(int(result[0]))))

    pBOOLEAN = Keyword("true") | Keyword("false")
    pBOOLEAN.setParseAction(lambda result: EValue(VBoolean(result[0]=="true")))

    pEXPR = Forward()

    pEXPR_PAREN = "(" + pEXPR + ")"
    pEXPR_PAREN.setParseAction(lambda result: result[1])

    pNOT = Keyword("not") + pEXPR
    pNOT.setParseAction(lambda result: EPrimCall(oper_not, [result[1]]))

    def parse_let(result):
        bindings = [(result[2],ERefCell(result[4]))]
        for vs in result[5]:
            bindings.append((vs[0],ERefCell(vs[2])))
        return ELet(bindings,result[7])

    pLET = Keyword("let") + "(" + pNAME + "=" + pEXPR + Group(ZeroOrMore( Suppress(",") + Group(pNAME + "=" + pEXPR) ))+ ")" + pEXPR
    pLET.setParseAction(parse_let)

    def parse_dict(result):
        vals = {result[1][0]:result[1][2]}
        for b in result[2]:
            vals[b[0]]=b[2]
        return EDict(vals)

    pDICT = "{" + Group(Optional(pNAME + ":" + pEXPR)) + Group(ZeroOrMore(Group(Suppress(",") + pNAME + ":" + pEXPR))) + "}"
    pDICT.setParseAction(parse_dict)

    pARRAY = "[" + Group(Optional(pEXPR) + ZeroOrMore(Suppress(",") + pEXPR)) + "]"
    pARRAY.setParseAction(lambda result: EArray(result[1]))

    pBODY = Forward()

    def mkFunBody (params,body):
        bindings = [ (p,ERefCell(EId(p))) for p in params ]
        return ELet(bindings,body)

    pFUN = Keyword("fun") + "(" + Group(Optional(pNAME) + ZeroOrMore(Suppress(",") + pNAME)) + ")" + pBODY
    pFUN.setParseAction(lambda result: EFunction(result[2],mkFunBody(result[2],result[4])))

    pFUN_REC = Keyword("fun") + pNAME + "(" + Group(Optional(pNAME) + ZeroOrMore(Suppress(",") + pNAME)) + ")" + pBODY
    pFUN_REC.setParseAction(lambda result: EFunction(result[3],mkFunBody(result[3],result[5]),name=result[1]))

    pCORE = (pINTEGER | pBOOLEAN | pSTRING | pARRAY | pDICT | pEXPR_PAREN | pNOT | pIDENTIFIER)

    pCALL = "(" + Group(Optional(pEXPR) + ZeroOrMore(Suppress(",") + pEXPR)) + ")"
    pCALL.setParseAction(lambda result: ("CALL", result[1]))

    pACCESS = "[" + pEXPR + "]" + NotAny("=")
    pACCESS.setParseAction(lambda result: (oper_index, result[1]))

    pP1_back = (pCALL | pACCESS | Empty())

    def parse_oper_p1(result):
        if len(result)==2:
            if result[1][0] == "CALL":
                return ECall(result[0],result[1][1])
            return EPrimCall(result[1][0],[result[0],result[1][1]])
        if len(result)==1:
            return result


    pP1 = pCORE + pP1_back
    pP1.setParseAction(parse_oper_p1)

    pP2 = Forward()

    pMUL = "*" + pP2
    pMUL.setParseAction(lambda result: (oper_times, result[1]))

    pP2_back = (pMUL | Empty())

    def parse_oper(result):
        if len(result)==2:
            return EPrimCall(result[1][0],[result[0],result[1][1]])
        if len(result)==1:
            return result

    pP2 << pP1 + pP2_back
    pP2.setParseAction(parse_oper)

    pP3 = Forward()

    pADD = "+" + pP3
    pADD.setParseAction(lambda result: (oper_plus, result[1]))

    pSUB = "-" + pP3
    pSUB.setParseAction(lambda result: (oper_minus, result[1]))

    pP3_back = (pSUB | pADD | Empty())

    pP3 << pP2 + pP3_back
    pP3.setParseAction(parse_oper)

    pP4 = Forward()

    pGTR = ">" + pP4
    pGTR.setParseAction(lambda result: (oper_greater, result[1]))

    pGTR_EQ = ">=" + pP4
    pGTR_EQ.setParseAction(lambda result: (oper_greater_equal, result[1]))

    pLSS = "<" + pP4
    pLSS.setParseAction(lambda result: (oper_less, result[1]))

    pLSS_EQ = "<=" + pP4
    pLSS_EQ.setParseAction(lambda result: (oper_less_equal, result[1]))

    pEQ = "==" + pP4
    pEQ.setParseAction(lambda result: (oper_equal, result[1]))

    pNOT_EQ = "<>" + pP4
    pNOT_EQ.setParseAction(lambda result: (oper_not_equal, result[1]))

    pP4_back = (pNOT_EQ | pGTR | pGTR_EQ | pLSS | pLSS_EQ | pEQ | Empty())

    pP4 << pP3 + pP4_back
    pP4.setParseAction(parse_oper)

    pP5 = Forward()

    pAND = "and" + pP5
    pAND.setParseAction(lambda result: ("AND", result[1]))

    pOR = "or" + pP5
    pOR.setParseAction(lambda result: ("OR", result[1]))

    pP5_back = (pAND | pOR | Empty())

    def parse_oper_bools(result):
        if len(result)==2:
            if result[1][0] == "AND":
                return EAnd(result[0],result[1][1])
            if result[1][0] == "OR":
                return EOr(result[0],result[1][1])
        if len(result)==1:
            return result

    pP5 << pP4 + pP5_back
    pP5.setParseAction(parse_oper_bools)

    pP6 = Forward()

    pCOND = "?" + pP6 + ":" + pP6
    pCOND.setParseAction(lambda result: ("COND", result[1], result[3]))

    pP6_back = (pCOND | Empty())

    def parse_oper_cond(result):
        if len(result)==2 and result[1][0] == "COND":
            return EIf(result[0],result[1][1],result[1][2])
        if len(result)==1:
            return result

    pP6 << pP5 + pP6_back
    pP6.setParseAction(parse_oper_cond)

    pEXPR << (pLET | pFUN_REC | pFUN | pP6)

    pDECL_VAR = Keyword("var") + pNAME + ";"
    pDECL_VAR.setParseAction(lambda result: (result[1],EValue(VNone())))

    pDECL_VAR_INST = Keyword("var") + pNAME + "=" + pEXPR + ";"
    pDECL_VAR_INST.setParseAction(lambda result: (result[1],result[3]))

    pDEF = Keyword("def") + pNAME + "(" + Group(Optional(pNAME) + ZeroOrMore(Suppress(",") + pNAME)) + ")" + pBODY 
    pDEF.setParseAction(lambda result: (result[1], EFunction(result[3],mkFunBody(result[3],result[5]),name=result[1])))

    pDECL = (pDECL_VAR | pDECL_VAR_INST | pDEF)

    pSTMT_EVAL = pEXPR + ";"
    pSTMT_EVAL.setParseAction(lambda result: result[0])

    pSTMT_VAR = pNAME + "=" + pEXPR + ";"
    pSTMT_VAR.setParseAction(lambda result: EPrimCall(oper_update,[EId(result[0]),result[2]]))

    pSTMT_PRINT = Keyword("print") + Group(pEXPR + ZeroOrMore(Suppress(",") + pEXPR)) + ";"
    pSTMT_PRINT.setParseAction(lambda result: EPrimCall(oper_print,result[1]))

    pSTMT_ASSIGN = pEXPR + "[" + pEXPR + "]" + "=" + pEXPR + ";"
    pSTMT_ASSIGN.setParseAction(lambda result: EPrimCall(oper_obj_update,[result[0],result[2],result[5]]))

    pSTMT_COND = "if" + pEXPR + pBODY
    pSTMT_COND.setParseAction(lambda result: EIf(result[1],result[2],EValue(VBoolean(True))))

    pSTMT_COND_ELSE = "if" + pEXPR + pBODY + "else" + pBODY
    pSTMT_COND_ELSE.setParseAction(lambda result: EIf(result[1],result[2],result[4]))

    pSTMT_WHILE = Keyword("while") + pEXPR + pBODY
    pSTMT_WHILE.setParseAction(lambda result: EWhile(result[1],result[2]))

    pSTMT_FOR = Keyword("for") + "(" + pNAME + Keyword("in") + pEXPR + ")" + pBODY
    pSTMT_FOR.setParseAction(lambda result: EFor(result[2],result[4],result[6]))

    pSTMT = ( pSTMT_VAR | pSTMT_PRINT | pSTMT_ASSIGN | pSTMT_COND_ELSE | pSTMT_COND | pSTMT_WHILE | pSTMT_FOR | pSTMT_EVAL)

    def mkBlock (decls,stmts):
        bindings = [ (n,ERefCell(expr)) for (n,expr) in decls ]
        return ELet(bindings,EDo(stmts))

    pBODY << "{" + Group(ZeroOrMore(pDECL)) + Group(ZeroOrMore(pSTMT)) + "}"
    pBODY.setParseAction(lambda result: mkBlock(result[1],result[2]))


    # can't attach a parse action to pSTMT because of recursion, so let's duplicate the parser
    pTOP_STMT = pSTMT.copy()
    pTOP_STMT.setParseAction(lambda result: {"result":"statement",
                                             "stmt":result[0]})


    pTOP_DECL = pDECL.copy()
    pTOP_DECL.setParseAction(lambda result: {"result":"declaration",
                                             "decl":result[0]})

    pTOP = OneOrMore(pTOP_DECL | pTOP_STMT) + FollowedBy(StringEnd())

    return pTOP

def shell ():
    # A simple shell
    # Repeatedly read a line of input, parse it, and evaluate the result

    print "Homework 6 - Imp Language"
    print "#quit to quit, #abs to see abstract representation"
    env = initial_env()
    while True:
        inp = raw_input("inp> ")

        try:
            result = parse(inp).parseString(inp)[0]

            if result["result"] == "statement":
                stmt = result["stmt"]
                # print "Abstract representation:", exp
                v = stmt.eval(env)

            elif result["result"] == "abstract":
                print result["stmt"]

            elif result["result"] == "quit":
                return

            elif result["result"] == "declaration":
                (name,expr) = result["decl"]
                v = expr.eval(env)
                env.insert(0,(name,VRefCell(v)))
                print "{} defined".format(name)
                
                
        except Exception as e:
            print "Exception: {}".format(e)

def printTest (exp,env):
    print "func> {}".format(exp)
    #result = parse(exp)
    #result = parse(exp).parseString(exp)[0]
    result = parse_test().parseString(exp)[0]
    print result

    if result["result"] == "statement":
        stmt = result["stmt"]
        print stmt
        #print "Abstract representation:", exp
        v = stmt.eval(env)

    elif result["result"] == "abstract":
        print result["stmt"]

    elif result["result"] == "quit":
        return

    elif result["result"] == "declaration":
        #print result
        (name,expr) = result["decl"]
        v = expr.eval(env)
        env.insert(0,(name,VRefCell(v)))
        #print "{} defined".format(name)

def execute(filename):
    result = parse(filename).parseFile(filename)
    result = parse_test().parseFile(filename)
    env = initial_env()
    call_main = {'result': 'statement', 'stmt': ECall(EPrimCall(oper_deref,[EId("main")]),[])}
    result.append(call_main)

    for res in result:

        # Statement
        if res["result"] == "statement":
            stmt = res["stmt"]
            stmt.eval(env)

        # Declaration
        elif res["result"] == "declaration":
            (name,expr) = res["decl"]
            v = expr.eval(env)
            env.insert(0,(name,VRefCell(v)))
            #print "{} defined".format(name)



if __name__ == '__main__':
    sys.setrecursionlimit(100000)
    for arg in sys.argv[1:]:
        print "Running file {}".format(arg)
        execute(arg)
    exit()

    print "Homework 7"
    global_env = initial_env()
  

    printTest("var global_number = 10;",global_env)
    printTest("var x = global_number;",global_env)
    printTest("var y = global_number+1;",global_env)
    printTest("print x<>y;",global_env)
    printTest("def main () { var x1 = global_number; var y1 = global_number+1; print true;}",global_env)
  #   printTest("def main () {\
  # var x = global_number;\
  # var y = global_number+1;\
  # \}",global_env)
#   print true;\
#   print false;\
#   print true and true,true;\
#   print false or true,true;\
#   print false or false, false;\
#   print x == y, false;\
#   print (x > y), false;\
# \}",global_env)

#   print x==y,x>y,x>=y,x<y,x<=y,x<>y;\
#   print y==x,y>x,y>=x,y<x,y<=x,y<>x;\
#   print x==y or x>y, x>=y;\
#   print x==y and x>y, false;\
#   print not x==y, x<>y;\
#   print not true and not false,false;\
#   print not true or not false,true;\
#   print not false and true, true;\
# \
#   print true ? true : false, true;\
#   print false ? true : false, false;\
# }",global_env)