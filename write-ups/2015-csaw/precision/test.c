#include "stdio.h"
int main()
{
	char str_t[80] = {'\x00'};
	int i;
	scanf("%s", str_t);
	for (i = 0; i < 80; i++)
	{
		printf("%02x", str_t[i]);
	}
	printf("\n");
	return 0;
}