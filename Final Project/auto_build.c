#include <stdlib.h>
#include <stdio.h>
#define array_size 16

typedef struct tClosure{
    long long val;
    void* addr;
    int envLen;
    struct tClosure* p_env;
} tClosure;

void* addr;

//RESULT
tClosure result;
//ARGS
tClosure args[array_size];
int args_index = 0;
//ENV
tClosure env[array_size];
int env_index = 0;

int i;

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
    result.p_env = (tClosure*)malloc(sizeof(tClosure)*array_size);

    tClosure addr1;
    addr1.addr = &&PL_start0;
    addr1.envLen = 0;
    addr1.p_env = (tClosure*)malloc(sizeof(tClosure)*array_size);
    env[0] = addr1;
    env_index++;

    tClosure addr2;
    addr2.addr = &&PL_start16;
    addr2.envLen = 0;
    addr2.p_env = (tClosure*)malloc(sizeof(tClosure)*array_size);
    env[1] = addr2;
    env_index++;

    tClosure addr3;
    addr3.addr = &&PL_start32;
    addr3.envLen = 0;
    addr3.p_env = (tClosure*)malloc(sizeof(tClosure)*array_size);
    env[2] = addr3;
    env_index++;

    tClosure addr4;
    addr4.addr = &&PL_start45;
    addr4.envLen = 0;
    addr4.p_env = (tClosure*)malloc(sizeof(tClosure)*array_size);
    env[3] = addr4;
    env_index++;

    goto PL_START_FUNC;

    PL_start0:

    for (i=0;i<args_index;i++){
        env[env_index] = args[i];
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
    memcpy(env,result.p_env,result.envLen*sizeof(tClosure));
    env_index = result.envLen;

    goto *addr;

    PL_start16:

    for (i=0;i<args_index;i++){
        env[env_index] = args[i];
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
    memcpy(env,result.p_env,result.envLen*sizeof(tClosure));
    env_index = result.envLen;

    goto *addr;

    PL_start32:

    for (i=0;i<args_index;i++){
        env[env_index] = args[i];
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
    memcpy(env,result.p_env,result.envLen*sizeof(tClosure));
    env_index = result.envLen;

    goto *addr;

    PL_start45:

    for (i=0;i<args_index;i++){
        env[env_index] = args[i];
        env_index++;
    }

    result = env[0];

    return result.val;

    PL_START_FUNC:

    args_index = 0;

    addr = &&PL_A19;

    goto *addr;

    PL_B20:

    result.addr = addr;
    memcpy(result.p_env,env,env_index*sizeof(tClosure));
    result.envLen = env_index;

    env[env_index]=result;
    env_index++;

    for (i=0;i<args_index;i++){
        env[env_index] = args[i];
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
    memcpy(env,result.p_env,result.envLen*sizeof(tClosure));
    env_index = result.envLen;

    goto *addr;

    PL_L21:

    args_index = 0;

    result = env[6];

    args[args_index] = result;
    args_index++;

    result = env[7];

    addr = result.addr;
    memcpy(env,result.p_env,result.envLen*sizeof(tClosure));
    env_index = result.envLen;

    goto *addr;

    PL_A19:

    addr = &&PL_B20;

    result.addr = addr;
    memcpy(result.p_env,env,env_index*sizeof(tClosure));
    result.envLen = env_index;

    args[args_index] = result;
    args_index++;

    result = env[3];

    args[args_index] = result;
    args_index++;

    addr = &&PL_A22;

    goto *addr;

    PL_B23:

    for (i=0;i<args_index;i++){
        env[env_index] = args[i];
        env_index++;
    }

    args_index = 0;

    result.val = 200000;

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
    memcpy(env,result.p_env,result.envLen*sizeof(tClosure));
    env_index = result.envLen;

    goto *addr;

    PL_A22:

    addr = &&PL_B23;

    result.addr = addr;
    memcpy(result.p_env,env,env_index*sizeof(tClosure));
    result.envLen = env_index;

    addr = result.addr;
    memcpy(env,result.p_env,result.envLen*sizeof(tClosure));
    env_index = result.envLen;

    goto *addr;
}

int main(){
    printf("Answer: %lli",func());
    return 0;
}
