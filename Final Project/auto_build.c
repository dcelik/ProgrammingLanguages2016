#include <stdlib.h>
#include <stdio.h>

typedef struct tClosure{
    long long val;
    void* addr;
    int envLen;
    struct tClosure * p_env[32];
} tClosure;

void* addr;

//RESULT
tClosure result;
//ARGS
tClosure args[32];
int args_index = 0;
//ENV
tClosure env[32];
int env_index = 0;
//For loop i
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

    tClosure addr1;
    addr1.val = -1;
    addr1.addr = &&PL_start0;
    addr1.envLen = 0;
    env[0] = addr1;
    env_index++;

    tClosure addr2;
    addr2.val = -1;
    addr2.addr = &&PL_start16;
    addr2.envLen = 0;
    env[1] = addr2;
    env_index++;

    tClosure addr3;
    addr3.val = -1;
    addr3.addr = &&PL_start32;
    addr3.envLen = 0;
    env[2] = addr3;
    env_index++;

    tClosure addr4;
    addr4.val = -1;
    addr4.addr = &&PL_start45;
    addr4.envLen = 0;
    env[3] = addr4;
    env_index++;

    goto FUNC_START;

    PL_start0:

    for (i=0;i<=args_index-1;i++){
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
    for (i = 0;i<result.envLen;i++){
        env[i] = *result.p_env[i];
    }
    env_index = result.envLen;

    goto *addr;

    PL_start16:

    for (i=0;i<=args_index-1;i++){
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
    for (i = 0;i<result.envLen;i++){
        env[i] = *result.p_env[i];
    }
    env_index = result.envLen;

    goto *addr;

    PL_start32:

    for (i=0;i<=args_index-1;i++){
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
    for (i = 0;i<result.envLen;i++){
        env[i] = *result.p_env[i];
    }
    env_index = result.envLen;

    goto *addr;

    PL_start45:

    for (i=0;i<=args_index-1;i++){
        env[env_index] = args[i];
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
    for (i = 0;i<env_index;i++){
        *result.p_env[i] = env[i];
    }
    result.envLen = env_index;

    env[env_index]=result;
    env_index++;

    for (i=0;i<=args_index-1;i++){
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
    for (i = 0;i<result.envLen;i++){
        env[i] = *result.p_env[i];
    }
    env_index = result.envLen;

    goto *addr;

    PL_L21:

    args_index = 0;

    result = env[6];

    args[args_index] = result;
    args_index++;

    result = env[7];

    printf("%d",*result.p_env);

    addr = result.addr;
    for (i = 0;i<result.envLen;i++){
        env[i] = *result.p_env[i];
    }
    env_index = result.envLen;

    return 0;
    goto *addr;

    PL_A19:

    addr = &&PL_B20;

    result.addr = addr;
    for (i = 0;i<env_index;i++){
        *result.p_env[i] = env[i];
    }
    result.envLen = env_index;

    printf("%d \n",**result.p_env);

    args[args_index] = result;
    args_index++;

    result = env[3];

    args[args_index] = result;
    args_index++;

    addr = &&PL_A22;

    goto *addr;

    PL_B23:

    for (i=0;i<=args_index-1;i++){
        env[env_index] = args[i];
        env_index++;
    }

    args_index = 0;

    result.val = 0;

    args[args_index] = result;
    args_index++;

    result.val = 0;

    args[args_index] = result;
    args_index++;

    result = env[5];

    //return result.val;

    args[args_index] = result;
    args_index++;

    result = env[4];

    addr = result.addr;
    for (i = 0;i<result.envLen;i++){
        env[i] = *result.p_env[i];
    }
    env_index = result.envLen;

    goto *addr;

    PL_A22:

    addr = &&PL_B23;

    result.addr = addr;
    for (i = 0;i<env_index;i++){
        *result.p_env[i] = env[i];
    }
    result.envLen = env_index;

    addr = result.addr;
    for (i = 0;i<result.envLen;i++){
        env[i] = *result.p_env[i];
    }
    env_index = result.envLen;

    goto *addr;
}

int main(){
    printf("Answer: %lli",func());
    return 0;
}
