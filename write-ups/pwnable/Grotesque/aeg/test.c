#include <stdlib.h>
#include <errno.h>
#include <sys/mman.h>

#ifndef PAGESIZE
#define PAGESIZE 4096
#endif

int
main(void)
{
	printf("PROT_READ:%d\n", PROT_READ);
	printf("PROT_WRITE:%d\n", PROT_WRITE);
	printf("PROT_EXEC:%d\n", PROT_EXEC);
	return 0;
}