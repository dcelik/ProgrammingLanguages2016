code = ["#start0","PUSH-ENV-ARGS","CLEAR-ARGS","LOOKUP",0,"PUSH-ARGS","LOOKUP",1,"PUSH-ARGS","PRIM-CALL","oper_plus","CLEAR-ARGS","PUSH-ARGS","LOOKUP",2,"LOAD-ADDR-ENV","JUMP","#start16",
                   "PUSH-ENV-ARGS","CLEAR-ARGS","LOOKUP",0,"PUSH-ARGS","LOOKUP",1,"PUSH-ARGS","PRIM-CALL","oper_minus","CLEAR-ARGS","PUSH-ARGS","LOOKUP",2,"LOAD-ADDR-ENV","JUMP","#start32",
                   "PUSH-ENV-ARGS","CLEAR-ARGS","LOOKUP",0,"PUSH-ARGS","PRIM-CALL","oper_zero","CLEAR-ARGS","PUSH-ARGS","LOOKUP",1,"LOAD-ADDR-ENV","JUMP","#start45",
                     "PUSH-ENV-ARGS","LOOKUP",0,"RETURN"]

print len(code)
print code[16]