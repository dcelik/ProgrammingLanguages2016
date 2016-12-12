#include <stdlib.h>
#include <stdio.h>

typedef struct tClosure{
    long long val;
    void* addr;
    int envLen;
    struct tClosure * p_env[16];
} tClosure;

void* addr;

//RESULT
tClosure result;
//ARGS
tClosure args[2];
int args_index = 0;
//ENV
tClosure env[16];
int env_index = 3;


long long oper_plus(tClosure clo[]){
    return clo[0].val+clo[1].val;
}
long long oper_minus(tClosure clo[]){
    return clo[0].val-clo[1].val;
}
long long oper_times(tClosure clo[]){
    return clo[0].val*clo[1].val;
}
long long oper_zero(tClosure clo[]){
    //true->1
    //false->0
    return clo[0].val==0;
}

long long func(){
    //Setup result
    result.val = -1;
    result.envLen = 0;

    tClosure addr1;
    addr1.addr = &&PL_start0;
    addr1.envLen = 0;
    env[0] = addr1;

    tClosure addr2;
    addr2.addr = &&PL_start16;
    addr2.envLen = 0;
    env[1] = addr2;

    tClosure addr3;
    addr3.addr = &&PL_start32;
    addr3.envLen = 0;
    env[2] = addr3;

    tClosure addr4;
    addr4.addr = &&PL_start45;
    addr4.envLen = 0;
    env[3] = addr4;

    goto FUNC_START;

    PL_start0:

    env[env_index]=args[0];
    env_index++;
    if(args_index==2){
        env[env_index]=args[1];
        env_index++;
    }

    args_index = 0;

    result = env[0];

    args[args_index] = result;
    args_index++;

    result = env[1];

    args[args_index] = result;
    args_index++;

    result.val = oper_plus(args);

    args_index = 0;

    args[args_index] = result;
    args_index++;

    result = env[2];

    addr = result.addr;
    *env = **result.p_env;
    env_index = result.envLen;

    goto *addr;

    PL_start16:

    env[env_index]=args[0];
    env_index++;
    if(args_index==2){
        env[env_index]=args[1];
        env_index++;
    }

    args_index = 0;

    result = env[0];

    args[args_index] = result;
    args_index++;

    result = env[1];

    args[args_index] = result;
    args_index++;

    result.val = oper_minus(args);

    args_index = 0;

    args[args_index] = result;
    args_index++;

    result = env[2];

    addr = result.addr;
    *env = **result.p_env;
    env_index = result.envLen;

    goto *addr;

    PL_start32:

    env[env_index]=args[0];
    env_index++;
    if(args_index==2){
        env[env_index]=args[1];
        env_index++;
    }

    args_index = 0;

    result = env[0];

    args[args_index] = result;
    args_index++;

    result.val = oper_zero(args);

    args_index = 0;

    args[args_index] = result;
    args_index++;

    result = env[1];

    addr = result.addr;
    *env = **result.p_env;
    env_index = result.envLen;

    goto *addr;

    PL_start45:

    env[env_index]=args[0];
    env_index++;
    if(args_index==2){
        env[env_index]=args[1];
        env_index++;
    }

    result = env[0];

    return result.val;

    FUNC_START:

    args_index = 0;

    addr = &&PL_A19;

    goto *addr;

    PL_B20:

    result.addr = addr;
    *result.p_env = env;
    result.envLen = env_index;

    env[env_index]=result;
    env_index++;

    env[env_index]=args[0];
    env_index++;
    if(args_index==2){
        env[env_index]=args[1];
        env_index++;
    }

    args_index = 0;

    result = env[5];

    args[args_index] = result;
    args_index++;

    result.val = oper_zero(args);

    env[env_index]=result;
    env_index++;

    result = env[8];

    addr = &&PL_L21;

    if(result.val==1){
        goto *addr;
    }

    args_index = 0;

    result = env[5];

    args[args_index] = result;
    args_index++;

    result.val = 1;

    args[args_index] = result;
    args_index++;

    result.val = oper_minus(args);

    env[env_index]=result;
    env_index++;

    args_index = 0;

    result = env[6];

    args[args_index] = result;
    args_index++;

    result = env[5];

    args[args_index] = result;
    args_index++;

    result.val = oper_plus(args);

    env[env_index]=result;
    env_index++;

    args_index = 0;

    result = env[9];

    args[args_index] = result;
    args_index++;

    result = env[10];

    args[args_index] = result;
    args_index++;

    result = env[7];

    args[args_index] = result;
    args_index++;

    result = env[4];

    addr = result.addr;
    *env = **result.p_env;
    env_index = result.envLen;

    goto *addr;

    PL_L21:

    args_index = 0;

    result = env[6];

    args[args_index] = result;
    args_index++;

    result = env[7];

    addr = result.addr;
    *env = **result.p_env;
    env_index = result.envLen;

    goto *addr;

    PL_A19:

    addr = &&PL_B20;

    result.addr = addr;
    *result.p_env = env;
    result.envLen = env_index;

    args[args_index] = result;
    args_index++;

    result = env[3];

    args[args_index] = result;
    args_index++;

    addr = &&PL_A22;

    goto *addr;

    PL_B23:

    env[env_index]=args[0];
    env_index++;
    if(args_index==2){
        env[env_index]=args[1];
        env_index++;
    }

    args_index = 0;

    result.val = 200;

    args[args_index] = result;
    args_index++;

    result.val = 0;

    args[args_index] = result;
    args_index++;

    result = env[5];

    args[args_index] = result;
    args_index++;

    result = env[4];

    addr = result.addr;
    *env = **result.p_env;
    env_index = result.envLen;

    goto *addr;

    PL_A22:

    addr = &&PL_B23;

    result.addr = addr;
    *result.p_env = env;
    result.envLen = env_index;

    addr = result.addr;
    *env = **result.p_env;
    env_index = result.envLen;

    goto *addr;
}

int main(){
    printf("Answer: %lli",func());
    return 0;
}
