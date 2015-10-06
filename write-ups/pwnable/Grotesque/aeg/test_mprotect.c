#include <stdlib.h>
#include <errno.h>
#include <sys/mman.h>

#ifndef PAGESIZE
#define PAGESIZE 4096
#endif

int
main(void)
{
	char *addr, *a = malloc(2048);
	addr = (long unsigned int)a & 0xffffffffffffff00;
	printf("%p\n", a);
	printf("%p\n", addr);
	int tmp;
	printf("1:\n");
	scanf("%d", &tmp);
	int ret_val = mprotect(addr, 1024, 7);
	printf("ret_val:%d\n", ret_val);
	printf("errno:%d\n", errno);
	printf("2:\n");
	scanf("%d", &tmp);
	printf("PROT_READ:%d\n", PROT_READ);
	printf("PROT_WRITE:%d\n", PROT_WRITE);
	printf("PROT_EXEC:%d\n", PROT_EXEC);
	return 0;
}