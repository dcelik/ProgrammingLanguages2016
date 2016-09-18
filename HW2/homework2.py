############################################################
#
# A simple expression language of integers and Booleans
#
# Extended with primitive operations and local bindings
#
#


#
# Expressions
#

class Exp (object):
    pass



class EInteger (Exp):
    # Integer literal

    def __init__ (self,i):
        self._integer = i

    def __str__ (self):
        return "EInteger({})".format(self._integer)

    def eval (self,prim_dict):
        return VInteger(self._integer)

    def substitute (self,id,new_e):
        return self


class EBoolean (Exp):
    # Boolean literal

    def __init__ (self,b):
        self._boolean = b

    def __str__ (self):
        return "EBoolean({})".format(self._boolean)

    def eval (self,prim_dict):
        return VBoolean(self._boolean)

    def substitute (self,id,new_e):
        return self


def oper_plus (v1,v2): 
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value + v2.value)
    raise Exception ("Runtime error: trying to add non-numbers")

def oper_minus (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value - v2.value)
    raise Exception ("Runtime error: trying to add non-numbers")

def oper_times (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value * v2.value)
    raise Exception ("Runtime error: trying to add non-numbers")
    

class EPrimCall (Exp):

    def __init__ (self,name,es):
        self._name = name
        self._exps = es

    def __str__ (self):
        return "EPrimCall({},[{}])".format(self._name,",".join([ str(e) for e in self._exps]))

    def eval (self,prim_dict):
        vs = [ e.eval(prim_dict) for e in self._exps ]
        return apply(prim_dict[self._name],vs)

    def substitute (self,ids,new_e):
        print ids
        print new_e
        new_es = [e.substitute(ids,new_e) for e in self._exps]
        return EPrimCall(self._name,new_es)

class EIf (Exp):
    # Conditional expression

    def __init__ (self,e1,e2,e3):
        self._cond = e1
        self._then = e2
        self._else = e3

    def __str__ (self):
        return "EIf({},{},{})".format(self._cond,self._then,self._else)

    def eval (self,prim_dict):
        v = self._cond.eval(prim_dict)
        if v.type != "boolean":
            raise Exception ("Runtime error: condition not a Boolean")
        if v.value:
            return self._then.eval(prim_dict)
        else:
            return self._else.eval(prim_dict)

    def substitute (self,id,new_e):
        return EIf(self._cond.substitute(id,new_e),
                   self._then.substitute(id,new_e),
                   self._else.substitute(id,new_e))


class ELet (Exp):
    # local binding

    def __init__ (self,bindings,e1):
        self._bindings = bindings
        self._e1 = e1

    def __str__ (self):
        return "ELet({},{})".format(self._bindings,self._e1)

    def eval (self,prim_dict):
        print self._bindings
        for bind in self._bindings:
            print "Bind: {}".format(bind)
            temp_e = self._e1.substitute(bind,self._e1)
            self._e1 = temp_e
            print "New_e {}".format(ELet(self._bindings,self._e1))
        return self._e1.eval(prim_dict)

    def substitute (self,id,new_e):
        print self._bindings
        print id
        new_binds = [(e[0],e[1].substitute(id[0],id[1])) for e in self._bindings]
        print "New Binds: " + str(new_binds)
        for inner_id in self._bindings:
            if inner_id[0] == id[0]:
                return ELet(new_binds,self._e1)
        # print new_e
        return ELet(new_binds,new_e.substitute(id,self._e1))




        # for i in xrange(len(self._bindings)):
        #   if ids[i] == self._bindings[i][0]:
        #       return ELet([(self._bindings[i][0],
        #                   self._bindings[i][1].substitute(ids,new_e))],
        #                   self._e1)
        #   return ELet([(self._bindings[i][0],
        #               self._bindings[i][1].substitute(ids,new_e))],
        #               self._e1.substitute(ids,new_e))


class EId (Exp):
    # identifier

    def __init__ (self,id):
        self._id = id

    def __str__ (self):
        return "EId({})".format(self._id)

    def eval (self,prim_dict):
        raise Exception("Runtime error: unknown identifier {}".format(self._id))

    def substitute (self,id,new_e):
        if id == self._id:
            return new_e
        return self

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

class VBoolean (Value):
    # Value representation of Booleans
    def __init__ (self,b):
        self.value = b
        self.type = "boolean"

# Primitive operations

def oper_plus (v1,v2): 
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value + v2.value)
    raise Exception ("Runtime error: trying to add non-numbers")

def oper_minus (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value - v2.value)
    raise Exception ("Runtime error: trying to add non-numbers")

def oper_times (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value * v2.value)
    raise Exception ("Runtime error: trying to add non-numbers")


# Initial primitives dictionary

INITIAL_PRIM_DICT = {
    "+": oper_plus,
    "*": oper_times,
    "-": oper_minus
}

if __name__ == '__main__':

    #print EPrimCall("+",[EId("x"),EId("x")]).eval(INITIAL_PRIM_DICT)
    #print ELet("x",EInteger(10), EPrimCall("+",[EId("x"),EId("x")])).eval(INITIAL_PRIM_DICT).value
    print ELet(\
            "a",EInteger(5),\
            ELet(\
                "b",EInteger(10),\
                EPrimCall("-",[EId("a"),EId("b")]))).eval(INITIAL_PRIM_DICT).value

    # print EPrimCall("+",[EInteger(10),EInteger(20)]).eval(INITIAL_PRIM_DICT).value
    # print "++++++++++++++"
    # print ELet(\
    #       [("b",EInteger(10))],\
    #       ELet(\
    #           [("a",EId("b"))],\
    #           ELet(\
    #               [("b",EId("a"))],\
    #               EPrimCall("+",[EId("a"),EId("b")])
    #               )
    #           )
    #       ).eval(INITIAL_PRIM_DICT).value

    # print ELet([("x",EInteger(10)),\
 #          ("y",EInteger(20)),\
 #          ("z",EInteger(30))],\
 #              EPrimCall("*",[EPrimCall("+",[EId("x"),EId("y")]),EId("z")])).eval(INITIAL_PRIM_DICT).value

    # print ELet([("a",EInteger(20))],\
    #           ELet([("b",EInteger(5)),\
    #           ("b",EId("a"))],\
    #               EPrimCall("-",[EId("a"),EId("b")]))).eval(INITIAL_PRIM_DICT).value

    print ELet([("a",EInteger(5)),\
            ("b",EInteger(20))],\
                ELet([("a",EId("b")),\
                ("b",EId("a"))],\
                    EPrimCall("-",[EId("a"),EId("b")]))).eval(INITIAL_PRIM_DICT).value
    