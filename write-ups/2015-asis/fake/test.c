#include "stdio.h"
int main()
{
	long int a;
	printf("size:%d\n", sizeof(a));
	char input[100];
	gets(input);
	a = strtol(input, 0, 10);
	printf("%d\n", a);
	return 0;
}