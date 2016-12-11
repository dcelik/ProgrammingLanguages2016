unsigned long pc = 0;
unsigned long addr=0;

int env[256] = {0};
int args[2] = {0};

typedef struct{
    int addr;
    int envLen;
    int *p_env;
} tTuple;

tTuple result;
int fresh_arg = 0;
int fresh_env = 0;
int i=0;
tTuple t[2];

//int n = 10;

int oper_plus(int arr[]){
    return arr[0]+arr[1];
}
int oper_minus(int arr[]){
    return arr[0]-arr[1];
}
int oper_times(int arr[]){
    return arr[0]*arr[1];
}
int oper_zero(int arr[]){
    //true->1
    //false->0
    return arr[0]==0;
}

//-2 -> plus
//-3 -> minus
//-4 -> times
//-5 -> zero
int code[59] = {2,10,3,2,0,3,9,8,10,8,7,1,4,1,3,
    11,-5,9,55,12,1,4,1,3,2,1,3,
    11,-3,1,3,7,1,4,1,3,4,2,3,
    11,-2,1,3,7,1,4,3,3,4,4,3,4,
    0,5,6,4,2,0};

int main(){
    result.addr = -1;
    result.envLen = 0;
    result.p_env = (int *)malloc(sizeof(int)*result.envLen);

    //tTuple test={-1,10};
    //t[1] = test;
    //t[2] = test;
    //return t[1].addr+t[2].addr;


    //LOAD\n 10
    asm("movl $10, _result\n");

    //PUSH-ARGS\n
    asm("movl _fresh_arg, %eax\n"
        "movl _result, %edx\n"
        "movl %edx, _args(,%eax,4)\n");

    //fresh_arg++;
    asm("movl _fresh_arg, %eax\n"
        "addl $1, %eax\n"
        "movl %eax, _fresh_arg\n");

    //LOAD\n 0
    asm("movl $0, _result\n");

    //PUSH-ARGS\n
    asm("movl _fresh_arg, %eax\n"
        "movl _result, %edx\n"
        "movl %edx, _args(,%eax,4)\n");

    //fresh_arg++;
    asm("movl _fresh_arg, %eax\n"
        "addl $1, %eax\n"
        "movl %eax, _fresh_arg\n");

    //@loop
    asm("LOOP:\n");


    asm("movl _args, %eax\n"
        "leave\n"
        "ret\n");
    //return args[0];

//    result = n; //LOAD 0-1
//
//    args[fresh_arg] = result; //PUSH-ARGS 2
//    fresh_arg++; //args = [n]
//
//    result = 0; //LOAD 3-4
//
//    args[fresh_arg] = result; //PUSH-ARGS 5
//    fresh_arg++; //args = [n,0]
//
//    addr = 8; //LOAD-ADDR 6-7
//
//    result = (addr,env); //LOAD-FUN 8
//
//    env[fresh_env] = result;//PUSH-ENV 9
//    fresh_env++; //env = [(8,[])]
//
//    env = env+args; //env = [(8,[]),n,0]
//
//    clear_args(); // args = []
//
//    result = env[1] // result = n
//
//    args[fresh_arg] = result; //PUSH-ARGS 14
//    fresh_arg++; // args = [n]
//
//    //PRIM-CALL
//    oper = oper_zero
//    result = apply(oper,args) // oper_zero([n])
//
//    //LOAD-ADDR
//    addr = 55;
//
//    if (result == true){}




    //asm("movl $10, _pc \n");

    //memset(args, i, sizeof(int)*128);
    //asm("movl $10, _pc \n");
    //for (i=0; i<128; ++i)
    //    args[i]=i;


    //set args to index value
//    asm("movl $0, _i\n"
//        "   jmp D2\n"
//        "D3:\n"
//        "   movl _i, %eax\n"
//        "   movl _i, %edx\n"
//        "   movl %edx, _args(,%eax,4)\n"
//        "   addl $1, _i\n"
//        "D2:\n"
//        "   cmpl $127, _i\n"
//        "   jle D3\n");

    //clear args
//    asm("movl $0, _i\n"
//        "   jmp D4\n"
//        "D5:\n"
//        "   movl _i, %eax\n"
//        "   movl $0, _args(,%eax,4)\n"
//        "   addl $1, _i\n"
//        "D4:\n"
//        "   cmpl $127, _i\n"
//        "   jle D5\n");

    //increment PC
//    asm("   movl $0, 44(%esp)\n"
//        "   jmp L4\n"
//        "L5:\n"
//        "   movl _pc, %eax\n"
//        "   addl $1, %eax\n"
//        "   movl %eax, _pc\n"
//        "   addl $1, 44(%esp)\n"
//        "L4:\n"
//        "   cmpl $127, 44(%esp)\n"
//        "   jle L5\n");


    //return args[100];
//    asm("movl _args+400, %eax\n"
//        "leave\n"
//        "ret\n");

    //return pc;
//    asm("movl _i, %eax\n"
//        "leave\n"
//        "ret\n");


}
