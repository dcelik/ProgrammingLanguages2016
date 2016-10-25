############################################################
# Simple imperative language
# C-like surface syntac
# with S-expression syntax for expressions
# (no recursive closures)
#

############################################################
# HOMEWORK 6
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


class ELet (Exp):
    # local binding
    # allow multiple bindings
    # eager (call-by-avlue)

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
        # if f.type != "function" and f.type != "procedure":
        if f.type != "function":
            #raise Exception("Runtime error: trying to call a non-function or non-procedure")
            raise Exception("Runtime error: trying to call a non-function")
        args = [ e.eval(env) for e in self._args]
        if len(args) != len(f.params):
            raise Exception("Runtime error: argument # mismatch in call")
        new_env = zip(f.params,args) + f.env
        return f.body.eval(new_env)


class EFunction (Exp):
    # Creates an anonymous function

    def __init__ (self,params,body):
        self._params = params
        self._body = body

    def __str__ (self):
        return "EFunction([{}],{})".format(",".join(self._params),str(self._body))

    def eval (self,env):
        return VClosure(self._params,self._body,env)

# class EProcedure (EFunction):
#     def __str__ (self):
#         return "EProcedure([{}],{})".format(",".join(self._params),str(self._body))

#     def eval(self,env):
#         return VClosure(self._params,self._body,env,closure_type="procedure")


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
        while c.value:
            self._exp.eval(env)
            c = self._cond.eval(env)
            if c.type != "boolean":
                raise Exception ("Runtime error: while condition not a Boolean")
        return VNone()

class EFor(Exp):

    def __init__(self,init,cond,mod,exp):
        self._init = init #binding
        self._cond = cond #conditional
        self._mod = mod #value for new binding
        self._exp = exp #eval every loop

    def __str__ (self):
        return "EFor({},{},{},{})".format(str(self._init),str(self._cond),str(self._mod),str(self._exp))

    def eval (self,env):
        self._init.eval(env)
        c = self._cond.eval(env)
        if c.type != "boolean":
            raise Exception ("Runtime error: while condition not a Boolean")

        while c.value:
            self._exp.eval(env)
            self._mod.eval(env)
            c = self._cond.eval(env)
            if c.type != "boolean":
                raise Exception ("Runtime error: while condition not a Boolean")
        return VNone()



### Adapted from Lecture 6 Code by Riccardo Pucella
class EArray(Exp):
    def __init__(self,len_exp):
        self._len = len_exp
        self._arr = []
        self._fields = []
        self._methods = []

    def mkArrMethods(self):
        len_meth = EFunction([],EWithObj(EId("this"),ECall(EId("deref"),[EId("__length__")])))
        self._methods.insert(0,("length",EFunction(["this"],len_meth)))

        index_meth = EFunction(["x"],EWithObj(EId("this"),EPrimCall(arr_oper_index,[EId("this"),EId("x")])))
        self._methods.insert(0,("index",EFunction(["this"],index_meth)))

        map_meth = EFunction(["__function__"],EWithObj(EId("this"),EPrimCall(arr_oper_map,[EId("this"),EId("__function__")])))
        self._methods.insert(0,("map",EFunction(["this"],map_meth)))

    def eval (self,env):
        self._fields = [("__length__",EPrimCall(oper_ref,[self._len]))]
        fields = [ (id,e.eval(env)) for (id,e) in self._fields]

        self.mkArrMethods()
        methods = [ (id,e.eval(env)) for (id,e) in self._methods]

        self._arr = [VNone() for _ in xrange(fields[0][1].content.value)]
        
        return VArray(self._arr,fields,methods)



### Taken from Lecture 6 Code
#Author: Riccardo Pucella
class EWithObj (Exp):
    def __init__ (self,exp1,exp2):
        self._object = exp1
        self._exp = exp2
        
    def __str__ (self):
        return "EWithObj({},{})".format(str(self._object),str(self._exp))

    def eval (self,env):
        object = self._object.eval(env)
        if object.type != "object" and object.type != "array":
            raise Exception("Runtime error: expected an object")
        return self._exp.eval(object.env+env)

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
    
    def __init__ (self,params,body,env,closure_type="function"):
        self.params = params
        self.body = body
        self.env = env
        self.type = closure_type

    def __str__ (self):
        return "<{} [{}] {}>".format(str(self.type),",".join(self.params),str(self.body))

    ### Taken from Lecture 6 Code
    #Author: Riccardo Pucella
    def apply (self,args):
        if len(args) != len(self.params):
            raise Exception("Runtime error: argument # mismatch in call")
        new_env = zip(self.params,args) + self.env
        return self.body.eval(new_env)

### Adapted from Lecture 6 Code by Riccardo Pucella
class VArray(Value):
    def __init__(self, array, fields, methods):
        self.type = "array"
        self._fields = fields
        self._methods = methods
        self.value = array
        self.env = fields + [ (id,VRefCell(v.apply([self]))) for (id,v) in methods]

    def __str__ (self):
        f = self._fields + [("__array__",self.value)]
        return "<{} {} {}>".format(self.type,",".join( id+":"+(str(v)) for (id,v) in f),
                                       ",".join( id+":"+(str(v)) for (id,v) in self._methods))

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

class VString (Value):

    def __init__ (self,value):
        self.value = value
        self.type = "string"

    def __str__ (self):
        return self.value


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

def oper_ref (v1):
    return VRefCell(v1)

def oper_not (v1):
    if v1.type == "boolean":
        return VBoolean(not v1.value)
    raise Exception ("Runtime error: type error in not")

def oper_greater (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VBoolean(v1.value>v2.value)
    raise Exception ("Runtime error: type error in >")

def oper_greater_equal (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VBoolean(v1.value>=v2.value)
    raise Exception ("Runtime error: type error in >=")

def oper_less (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VBoolean(v1.value<v2.value)
    raise Exception ("Runtime error: type error in <") 

def oper_less_equal (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VBoolean(v1.value<=v2.value)
    raise Exception ("Runtime error: type error in <=")

# Primitive string operations

def str_oper_length(s1):
    if s1.type == "string":
        return len(s1.value)
    raise Exception ("Runtime error: trying to get length of non-string")

def str_oper_substring(s1,start,end):
    if s1.type == "string":
        return s1.value[start.value:end.value]
    raise Exception ("Runtime error: trying to get substring of non-string")

def str_oper_concat(s1,s2):
    if s1.type == "string" and s2.type == "string":
        return s1.value+s2.value
    raise Exception ("Runtime error: trying to get concat of non-strings")

def str_oper_startswith(s1,s2):
    #checks if s1 starts with s2
    if s1.type == "string" and s2.type == "string":
        return s1.value[:len(s2.value)]==s2.value
    raise Exception ("Runtime error: trying to apply startswith on non-strings")

def str_oper_endswith(s1,s2):
    #checks if s1 ends with s2
    if s1.type == "string" and s2.type == "string":
        return s1.value[-len(s2.value):]==s2.value
    raise Exception ("Runtime error: trying to apply endswith on non-strings")

def str_oper_lower(s1):
    if s1.type == "string":
        return s1.value.lower()
    raise Exception ("Runtime error: trying to get lowercase version of non-string")

def str_oper_upper(s1):
    if s1.type == "string":
        return s1.value.upper()
    raise Exception ("Runtime error: trying to get uppercase version of non-string")

# Primitive array operations

def arr_oper_update(arr,ind,val):
    if arr.type == "array" and ind.type == "integer":
        arr.value[ind.value] = val
        return arr
    raise Exception ("Runtime error: trying to update value in non-array or with non-integer index")

def arr_oper_index(arr,ind):
    if arr.type == "array" and ind.type == "integer":
        return arr.value[ind.value]
    raise Exception ("Runtime error: trying to get value in non-array or with non-integer index")

def arr_oper_length(arr):
    if arr.type == "array":
        return len(arr.value)
    raise Exception ("Runtime error: trying to get length of non-array")

def arr_oper_map(arr,function):
    if arr.type == "array":
        return [function.apply([e]) for e in arr.value]
    raise Exception ("Runtime error: trying to length of non-array")

def arr_partition_hoare(obj,first,last):
    if obj.type = "array":
        array_list = obj.array
        pivot = array_list[first]
        i = first
        j = last
        while True:
            while array_list[i] < pivot:
                i = i + 1
                
            while array_list[j] > pivot:
                j = j-1
            if i >= j:
                obj.array = array_list
                return j
            else:
                holder = array_list[i]
                array_list[i] = array_list[j]
                array_list[j] = holder
    raise Exception ("Runtime error: trying to partition non-array")

def arr_partition_lomuto(obj,first,last):
    if obj.type = "array":
        array_list = obj.array
        pivot = array_list[last]
        j = first
        for i in xrange(first,last):
            if array_list[i] <= pivot:
                holder = array_list[i]
                array_list[i] = array_list[j]
                array_list[j] = holder
                j = j + 1
        holder = array_list[j]
        array_list[j] = array_list[last]
        array_list[last] = holder
        obj.array = array_list
        return j
    raise Exception ("Runtime error: trying to partition non-array")

def arr_quicksort(obj,first = 1, last = None):
    if obj.type = "array":
        if last = None:
            last = obj.length-1
        if first < last:
            p = arr_partition_lomuto(obj,first,last)
            arr_quicksort(obj,first,p-1)
            arr_quicksort(obj,p+1,last)
            return obj
    raise Exception ("Runtime error: trying to quicksort non-array")

############################################################
# IMPERATIVE SURFACE SYNTAX
#



##
## PARSER
##
# cf http://pyparsing.wikispaces.com/

from pyparsing import Word, Literal, ZeroOrMore, OneOrMore, Keyword, Forward, alphas, alphanums, NoMatch
from pyparsing import Group, QuotedString


def initial_env_imp ():
    # A sneaky way to allow functions to refer to functions that are not
    # yet defined at top level, or recursive functions
    env = []
    env.insert(0,
               ("+",
                VRefCell(VClosure(["x","y"],
                                  EPrimCall(oper_plus,[EId("x"),EId("y")]),
                                  env))))
    env.insert(0,
               ("-",
                VRefCell(VClosure(["x","y"],
                                  EPrimCall(oper_minus,[EId("x"),EId("y")]),
                                  env))))
    env.insert(0,
               ("*",
                VRefCell(VClosure(["x","y"],
                                  EPrimCall(oper_times,[EId("x"),EId("y")]),
                                  env))))
    env.insert(0,
               ("zero?",
                VRefCell(VClosure(["x"],
                                  EPrimCall(oper_zero,[EId("x")]),
                                  env))))
    env.insert(0,
               ("not",
                VRefCell(VClosure(["x"],
                                  EPrimCall(oper_not,[EId("x")]),
                                  env))))
    env.insert(0,
               ("<",
                VRefCell(VClosure(["x","y"],
                                  EPrimCall(oper_less,[EId("x"),EId("y")]),
                                  env))))
    env.insert(0,
               (">",
                VRefCell(VClosure(["x","y"],
                                  EPrimCall(oper_greater,[EId("x"),EId("y")]),
                                  env))))
    env.insert(0,
               ("<=",
                VRefCell(VClosure(["x","y"],
                                  EPrimCall(oper_less_equal,[EId("x"),EId("y")]),
                                  env))))
    env.insert(0,
               (">=",
                VRefCell(VClosure(["x","y"],
                                  EPrimCall(oper_greater_equal,[EId("x"),EId("y")]),
                                  env))))
    env.insert(0,
               ("length",
                VRefCell(VClosure(["x"],
                                  EPrimCall(str_oper_length,[EId("x")]),
                                  env))))
    env.insert(0,
               ("substring",
                VRefCell(VClosure(["x","y","z"],
                                  EPrimCall(str_oper_substring,[EId("x"),EId("y"),EId("z")]),
                                  env))))
    env.insert(0,
               ("concat",
                VRefCell(VClosure(["x","y"],
                                  EPrimCall(str_oper_concat,[EId("x"),EId("y")]),
                                  env))))
    env.insert(0,
               ("startswith",
                VRefCell(VClosure(["x","y"],
                                  EPrimCall(str_oper_startswith,[EId("x"),EId("y")]),
                                  env))))
    env.insert(0,
               ("endswith",
                VRefCell(VClosure(["x","y"],
                                  EPrimCall(str_oper_endswith,[EId("x"),EId("y")]),
                                  env))))
    env.insert(0,
               ("lower",
                VRefCell(VClosure(["x"],
                                  EPrimCall(str_oper_lower,[EId("x")]),
                                  env))))
    env.insert(0,
               ("upper",
                VRefCell(VClosure(["x"],
                                  EPrimCall(str_oper_upper,[EId("x")]),
                                  env))))
    env.insert(0,
               ("arr_update",
                VRefCell(VClosure(["x","y","z"],
                                  EPrimCall(arr_oper_update,[EId("x"),EId("y"),EId("z")]),
                                  env))))
    env.insert(0,
               ("deref",
                VClosure(["x"],
                         EPrimCall(oper_deref, [EId("x")]),
                         env)))
    return env




def parse_imp (input):
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


    idChars = alphas+"_+*-?!=<>"

    pIDENTIFIER = Word(idChars, idChars+"0123456789")
    #### NOTE THE DIFFERENCE
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

    pEXPRS = ZeroOrMore(pEXPR)
    pEXPRS.setParseAction(lambda result: [result])

    pIF = "(" + Keyword("if") + pEXPR + pEXPR + pEXPR + ")"
    pIF.setParseAction(lambda result: EIf(result[2],result[3],result[4]))

    def mkFunBody (params,body):
        bindings = [ (p,ERefCell(EId(p))) for p in params ]
        return ELet(bindings,body)

    pFUN = "(" + Keyword("function") + "(" + pNAMES + ")" + pEXPR + ")"
    pFUN.setParseAction(lambda result: EFunction(result[3],mkFunBody(result[3],result[5])))

    pARRAY = "(" + Keyword("new-array") + pEXPR + ")"
    pARRAY.setParseAction(lambda result:EArray(result[2]))

    pWITH = "(" + Keyword("with") + pEXPR + pEXPR + ")"
    pWITH.setParseAction(lambda result: EWithObj(result[2],result[3]))
    #pWITH.setParseAction(lambda result: EWithObj(result[2],result[3]))
    
    pCALL = "(" + pEXPR + pEXPRS + ")"
    pCALL.setParseAction(lambda result: ECall(result[1],result[2]))

    pEXPR << (pINTEGER | pBOOLEAN | pSTRING | pARRAY | pWITH | pIDENTIFIER | pIF | pFUN | pCALL)

    pSTMT = Forward()

    pDECL_VAR = "var" + pNAME + "=" + pEXPR + ";"
    pDECL_VAR.setParseAction(lambda result: (result[1],result[3]))

    pDECL_PROC = Keyword("procedure") + pNAME + "(" + pNAMES + ")" + pSTMT
    pDECL_PROC.setParseAction(lambda result: (result[1], EFunction(result[3], mkFunBody(result[3],result[5]))))
    #pDECL_PROC.setParseAction(lambda result: (result[1], EProcedure(result[3], mkFunBody(result[3],result[5]))))

    # hack to get pDECL to match only pDECL_VAR (but still leave room
    # to add to pDECL later)
    pDECL = ( pDECL_PROC | pDECL_VAR | NoMatch() )

    pDECLS = ZeroOrMore(pDECL)
    pDECLS.setParseAction(lambda result: [result])

    pSTMT_IF_1 = "if" + pEXPR + pSTMT + "else" + pSTMT
    pSTMT_IF_1.setParseAction(lambda result: EIf(result[1],result[2],result[4]))

    pSTMT_IF_2 = "if" + pEXPR + pSTMT
    pSTMT_IF_2.setParseAction(lambda result: EIf(result[1],result[2],EValue(VBoolean(True))))
   
    pSTMT_WHILE = "while" + pEXPR + pSTMT
    pSTMT_WHILE.setParseAction(lambda result: EWhile(result[1],result[2]))

    pSTMT_PRINT = "print" + pEXPR + ";"
    pSTMT_PRINT.setParseAction(lambda result: EPrimCall(oper_print,[result[1]]));

    pSTMT_UPDATE = pNAME + "<-" + pEXPR + ";"
    pSTMT_UPDATE.setParseAction(lambda result: EPrimCall(oper_update,[EId(result[0]),result[2]]))

    pSTMT_UPDATE_ARR = pEXPR + "[" + pEXPR + "]" + "<-" + pEXPR + ";"
    pSTMT_UPDATE_ARR.setParseAction(lambda result:EPrimCall(arr_oper_update,[result[0],result[2],result[5]]))

    pSTMT_PROC = pEXPR + "(" + pEXPRS + ")" + ";"
    pSTMT_PROC.setParseAction(lambda result: ECall(result[0],result[2]))

    pSTMTS = ZeroOrMore(pSTMT)
    pSTMTS.setParseAction(lambda result: [result])

    def mkBlock (decls,stmts):
        bindings = [ (n,ERefCell(expr)) for (n,expr) in decls ]
        return ELet(bindings,EDo(stmts))
        
    pSTMT_BLOCK = "{" + pDECLS + pSTMTS + "}"
    pSTMT_BLOCK.setParseAction(lambda result: mkBlock(result[1],result[2]))

    def parse_for(result):
        init = result[2]
        cond = ECall(EPrimCall(oper_deref,[EId(result[3][1])]),[result[3][0],result[3][2]])

        if result[3][1] == "!=":
            cond = ECall(EPrimCall(oper_deref,[EId("not")]),[ECall(EPrimCall(oper_deref,[EId("zero?")]),[ECall(EPrimCall(oper_deref,[EId("-")]),[result[3][0],result[3][2]])])])

        mod = EPrimCall(oper_update,[EId(result[5]),ECall(result[8],[result[7],result[9]])])
        return EFor(init,cond,mod,result[11])

    pSTMT_FOR = Keyword("for") + "(" + pSTMT_UPDATE + Group(pEXPR + pNAME + pEXPR) + ";" + pNAME + "=" + pEXPR + pEXPR + pEXPR + ")"+ pSTMT_BLOCK
    pSTMT_FOR.setParseAction(parse_for)
    
    pSTMT << ( pSTMT_IF_1 | pSTMT_IF_2 | pSTMT_WHILE | pSTMT_PRINT | pSTMT_UPDATE_ARR | pSTMT_UPDATE |  pSTMT_BLOCK | pSTMT_FOR | pSTMT_PROC)

    # can't attach a parse action to pSTMT because of recursion, so let's duplicate the parser
    pTOP_STMT = pSTMT.copy()
    pTOP_STMT.setParseAction(lambda result: {"result":"statement",
                                             "stmt":result[0]})

    pTOP_DECL = pDECL.copy()
    pTOP_DECL.setParseAction(lambda result: {"result":"declaration",
                                             "decl":result[0]})

    pABSTRACT = "#abs" + pSTMT
    pABSTRACT.setParseAction(lambda result: {"result":"abstract",
                                             "stmt":result[1]})

    pQUIT = Keyword("#quit")
    pQUIT.setParseAction(lambda result: {"result":"quit"})
    
    pTOP = (pQUIT | pABSTRACT | pTOP_DECL | pTOP_STMT )

    result = pTOP.parseString(input)[0]
    return result    # the first element of the result is the expression


def shell_imp ():
    # A simple shell
    # Repeatedly read a line of input, parse it, and evaluate the result

    print "Homework 6 - Imp Language"
    print "#quit to quit, #abs to see abstract representation"
    env = initial_env_imp()

        
    while True:
        inp = raw_input("imp> ")

        try:
            result = parse_imp(inp)

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
    result = parse_imp(exp)

    if result["result"] == "statement":
        stmt = result["stmt"]
        # print "Abstract representation:", exp
        v = stmt.eval(env)

    elif result["result"] == "abstract":
        print result["stmt"]

    elif result["result"] == "quit":
        return

    elif result["result"] == "declaration":
        print result
        (name,expr) = result["decl"]
        v = expr.eval(env)
        env.insert(0,(name,VRefCell(v)))
        print "{} defined".format(name)

if __name__ == '__main__':

    ##Question 1 Tester
    # print "Question 1: C-Style For loop"
    # print "For ( <name> <- <expr> ; <name> <cond> <expr> ; <name> = <name> <oper> <expr>) { <stmts> }"
    # print "example: For ( x <- 10 ; x < 20 ; x = x + 1) { print x; }"
    # print ""
    # global_env = initial_env_imp()
    # printTest("var a = 0;",global_env)
    # printTest("print (+ 1 2);",global_env)
    # printTest("print (not (zero? (- 0 5)));",global_env)
    # printTest("for ( a <- 10 ; a != 20 ; a = a + 1 ) { print a;}",global_env)
    # printTest("for ( a <- 10 ; a < 20 ; a = a + 1 ) { print a;}",global_env)
    # printTest("for ( a <- 30 ; a > 20 ; a = a - 1 ) { print a;}",global_env)
    # printTest("for ( a <- 30 ; a >= 20 ; a = a - 1 ) { print a;}",global_env)
    # printTest("for ( a <- 10 ; a <= 20 ; a = a + 1 ) { print a;}",global_env)

    ##Question 2 Tester
    # print "Question 2: Immutable Strings"
    # global_env = initial_env_imp()
    # printTest("print \"Hi, I'm a \\\"string\\\" named Paul\";",global_env)
    # printTest("print (length \"Hi, I'm a \\\"string\\\" named Paul\");",global_env)
    # printTest("print (substring \"Hi, I'm a \\\"string\\\" named Paul\" 0 10);",global_env)
    # printTest("print (concat \"Hi, I'm a \\\"string\\\" named Paul\" \" Giamatti\");",global_env)
    # printTest("print (startswith \"Hi, I'm a \\\"string\\\" named Paul\" \"Hi, I'm \");",global_env)
    # printTest("print (startswith \"Hi, I'm a \\\"string\\\" named Paul\" \"Hello, I'm \");",global_env)
    # printTest("print (endswith \"Hi, I'm a \\\"string\\\" named Paul\" \"Paul\");",global_env)
    # printTest("print (endswith \"Hi, I'm a \\\"string\\\" named Paul\" \"named P\");",global_env)
    # printTest("print (lower \"Hi, I'm a \\\"string\\\" named Paul\");",global_env)
    # printTest("print (upper \"Hi, I'm a \\\"string\\\" named Paul\");",global_env)

    ##Question 3 Tester
    # print "Question 3: Procedures"
    # global_env = initial_env_imp()
    # printTest("var x = 10;",global_env)
    # printTest("procedure t1 ( ) { var a = 0; a <- 10; print a; }",global_env)
    # printTest("procedure test (val) { var a = 0; a <- val; print a; }",global_env)
    # printTest("procedure plusn (n v) { var temp = (+ n v); v <- temp; print v; }",global_env)
    # printTest("var f = ( function (a b c) (* a (* b c)));",global_env)
    # printTest("print (f 2 3 4);",global_env)
    # printTest("print (f x x x);",global_env)
    # printTest("plusn (5 10);",global_env)
    # printTest("plusn (127 x);",global_env)
    # printTest("plusn ((+ 1 2) (+ 3 4));",global_env)
    # #printTest("print (+ (test 10) 30);",global_env)
    # printTest("print (+ (f 2 3 4) 30);",global_env)
    # printTest("f (2 3 4);",global_env)

    ##Question 4 Tester
    global_env = initial_env_imp()
    print "Question 3: Mutable Array Objects"
    printTest("var x = (new-array 10);",global_env)
    printTest("print x;",global_env)
    printTest("x[3]<-(+ 3 10);",global_env)
    printTest("print (with x (length));",global_env)
    printTest("print (with x (index 3));",global_env)
    printTest("var y = (new-array 10);",global_env)
    printTest("var a = 0;",global_env)
    printTest("for ( a <- 0 ; a < 10 ; a = a + 1 ) { y[a]<-(+ a 10);}",global_env)
    printTest("print y;",global_env)
    printTest("for ( a <- 0 ; a < 10 ; a = a + 1 ) { print a; print (with y (index a));}",global_env)
    printTest("var mult = (function (x) (* 2 x));",global_env)
    printTest("print (with y (map mult));",global_env)
    #printTest("for ( a <- 0 ; a < 10 ; a = a + 1 ) { print a;}",global_env)

    #shell_imp()