#include <stdio.h>
int main()
{
	char name[100];
	fgets(name, 50, stdin);
	printf("%s\n", name);
	int i;
	for (i = 0; i < 50; i++)
	{
		printf("%02x ", name[i]);
	}
	printf("\n");
	return 0;
}