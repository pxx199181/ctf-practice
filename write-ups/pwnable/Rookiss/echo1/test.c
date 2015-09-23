#include<stdio.h>
int main(int argc, char const *argv[])
{
	char str[100];
	fgets(str, 100, stdin);
	int i;
	for (i = 0; i < 100; i++)
	{
		printf("%c ", str[i]);
	}
	printf("\n");
	printf("%s\n", str);
	return 0;
}