#include <stdio.h>
int main()
{

	system("http://;/bin/sh;ls");

	char *p = "12\034\056";
	int val;
	printf("%s\n", p);
	val = strtoul(p, 0, 16);
	printf("%s\n", p);
	printf("%d\n", val);
	return 0;
}